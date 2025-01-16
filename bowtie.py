import streamlit as st
import requests
import json
from graphviz import Digraph
from openai import OpenAI

OPENAI_API_KEY = ""

def strip_code_tags(output):
    if output.startswith("```json"):
        output = output[7:]  # Remove the opening ```json
    if output.startswith("```"):
            output = output[3:]  # Remove the opening ```json
    if output.endswith("```"):
        output = output[:-3]  # Remove the closing ```
    return output.strip()  # Remove any leading or trailing whitespace

# ---------------------------------------------------------------------
# 1. Streamlit App Layout
# ---------------------------------------------------------------------
st.title("Bowtie Risk Assessment Generator")

# Create a form to capture user inputs
with st.form("bowtie_form"):
    scenario = st.text_area(
        "Scenario",
        value="An industrial chemical storage facility is at risk of an explosion due to poor maintenance and untrained personnel."
    )
    detail_level = st.selectbox("Detail Level (1 = minimal, 3 = high)", [1, 2, 3])

    # Dropdown for selecting model provider
    provider = st.selectbox("Model Provider", ["Ollama", "OpenAI"])

    # Submit button
    submitted = st.form_submit_button("Generate Bowtie Assessment")

# ---------------------------------------------------------------------
# 2. Define the Prompt
# ---------------------------------------------------------------------
PROMPT_TEMPLATE = """
You are a knowledgeable risk assessment expert. Please create a Bowtie Risk Assessment for the scenario described below, with a specified detail level.

Scenario:
{scenario}

Detail Level:
- An integer "detail_level" ranging from 1 to 3, which determines how much detail to include:
  1. Minimal detail (short descriptions, fewer items)
  2. Moderate detail (moderate descriptions and items)
  3. High detail (comprehensive descriptions, more items)

Requirements:
1. Identify a "top_event" that represents the critical hazard or focal event in the bowtie.
2. List "threats" (causes) that could lead to the top event.
3. For each threat, specify:
   - "preventive_barriers" (measures to stop or reduce likelihood).
   - "escalation_factors" that could worsen the threat, along with appropriate "controls" for each escalation factor.
4. List "consequences" that occur if the top event materializes.
5. For each consequence, specify:
   - "recovery_measures" (measures to reduce severity or help recover).
   - "escalation_factors" that could worsen the consequence, along with appropriate "controls" for each.

Output Format:
1. Return valid JSON only (no extra commentary).
2. Incorporate a top-level field named "detail_level" indicating the integer passed in.
3. Use the structure below, expanding or shortening the content based on the detail level:

{{
  "detail_level": 1,
  "title": "",
  "top_event": "",
  "threats": [
    {{
      "name": "",
      "description": "",
      "preventive_barriers": [
        {{
          "name": "",
          "description": ""
        }}
      ],
      "escalation_factors": [
        {{
          "name": "",
          "controls": [
            {{
              "name": "",
              "description": ""
            }}
          ]
        }}
      ]
    }}
  ],
  "consequences": [
    {{
      "name": "",
      "description": "",
      "recovery_measures": [
        {{
          "name": "",
          "description": ""
        }}
      ],
      "escalation_factors": [
        {{
          "name": "",
          "controls": [
            {{
              "name": "",
              "description": ""
            }}
          ]
        }}
      ]
    }}
  ]
}}

Important:
- Do not include explanatory text or commentary outside the JSON.
- Only output valid JSON.
"""


def build_prompt(scenario_text, detail_level):
    """Constructs the final prompt string."""
    return PROMPT_TEMPLATE.format(scenario=scenario_text) + f'\nDetail Level:\n{detail_level}\n'


# ---------------------------------------------------------------------
# 3a. Function to Call Ollama Backend
# ---------------------------------------------------------------------
def call_ollama(prompt_text):
    """
    Calls the Ollama local API endpoint with the given prompt.
    Adjust server_url if running on a different host/port.
    """
    server_url = "http://localhost:11434/api/generate"
    # server_url = "http://107.170.54.31:11434/api/generate"
    payload = {
        "model": 'llama3.1:70b',
        "prompt": prompt_text,  # Pass the entire conversation
        "stream": False  # Disable streaming for a single response
    }
    try:
        response = requests.post(server_url, json=payload)
        response.raise_for_status()
        # Ollama sometimes streams tokens; we might get them in multiple chunks.
        # If the backend returns a JSON array of chunks, we’ll join them here.
        data = strip_code_tags(response.json()['response'])
        return data
        # generated_text = ""
        # for item in data:
        #     if "content" in item:
        #         generated_text += item["content"]
        # return generated_text
    except Exception as e:
        st.error(f"Error calling Ollama: {e}")
        return ""

# ---------------------------------------------------------------------
# 3b. Function to Call OpenAI
# ---------------------------------------------------------------------
def call_openai(prompt_text):
    """
    Calls OpenAI's ChatCompletion endpoint using the latest OpenAI Python SDK.
    Ensure your OpenAI API key is set in st.secrets["OPENAI_API_KEY"] or an environment variable.
    """
    # openai.api_key = st.secrets["OPENAI_API_KEY"]  # Replace with your environment variable if needed.
    client = OpenAI(api_key=OPENAI_API_KEY)
    try:
        # Use GPT models (gpt-3.5-turbo or gpt-4) with ChatCompletion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a knowledgeable risk assessment expert."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=1500,
            temperature=0.7
        )

        return strip_code_tags(response.choices[0].message.content.strip())

    except Exception as e:
        st.error(f"Error calling OpenAI: {e}")
        return ""



# ---------------------------------------------------------------------
# 4. Bowtie Diagram Generation (Optional)
# ---------------------------------------------------------------------
def create_bowtie_diagram(bowtie_data, output_filename='bowtie_diagram'):
    dot = Digraph(comment=bowtie_data.get('title', 'Bowtie Diagram'))
    dot.attr('node', shape='box', style='filled', color='lightgrey')

    # Central Top Event node
    top_event = bowtie_data.get('top_event', 'Top Event')
    dot.node('TOP', f"Top Event:\n{top_event}", shape='ellipse', style='filled', color='lightblue')

    # Threats (left side)
    for i, threat in enumerate(bowtie_data.get("threats", [])):
        threat_id = f"TH{i}"
        threat_name = threat.get("name", f"Threat {i}")
        dot.node(threat_id, f"Threat:\n{threat_name}", shape='box', color='tomato')
        dot.edge(threat_id, 'TOP', label="Leads to")

        # Preventive Barriers
        for j, barrier in enumerate(threat.get('preventive_barriers', [])):
            barrier_id = f"TH{i}_B{j}"
            barrier_label = f"Preventive Barrier:\n{barrier.get('name', f'Barrier {j}')}"
            dot.node(barrier_id, barrier_label, shape='box', style='rounded', color='green')
            dot.edge(threat_id, barrier_id, label="Prevents")
            dot.edge(barrier_id, 'TOP')

    # Consequences (right side)
    for i, consequence in enumerate(bowtie_data.get("consequences", [])):
        cons_id = f"CO{i}"
        cons_name = consequence.get("name", f"Consequence {i}")
        dot.node(cons_id, f"Consequence:\n{cons_name}", shape='box', color='gold')
        dot.edge('TOP', cons_id, label="Results in")

        # Recovery Measures
        for j, measure in enumerate(consequence.get('recovery_measures', [])):
            measure_id = f"CO{i}_R{j}"
            measure_label = f"Recovery Measure:\n{measure.get('name', f'Measure {j}')}"
            dot.node(measure_id, measure_label, shape='box', style='rounded', color='green')
            dot.edge('TOP', measure_id, label="Recovers")
            dot.edge(measure_id, cons_id)

    # Render the diagram to a file in the current directory
    output_path = dot.render(output_filename, format='svg', cleanup=True)
    return output_path

# ---------------------------------------------------------------------
# 5. Generate & Display Results
# ---------------------------------------------------------------------
if submitted:
    # Build the full prompt
    final_prompt = build_prompt(scenario, detail_level)
    st.write("**Generated Prompt:**")
    st.code(final_prompt, language="text")

    # Depending on the provider, call the appropriate function
    if provider == "Ollama":
        st.write("**Using Ollama**")
        generated_response = call_ollama(final_prompt)
    else:
        st.write("**Using OpenAI**")
        generated_response = call_openai(final_prompt)

    # Attempt to parse JSON
    if generated_response:
        st.write("**Model Output (Raw):**")
        st.code(generated_response, language="json")

        # Parse JSON
        try:
            bowtie_data = json.loads(generated_response)
            st.success("Valid JSON parsed successfully!")

            # Display JSON in a collapsible widget
            st.json(bowtie_data)

            # Optionally generate a bowtie diagram
            st.write("**Bowtie Diagram Preview**")
            output_svg = create_bowtie_diagram(bowtie_data, output_filename='bowtie_risk_assessment')
            # Display the generated SVG file (Streamlit can display SVG directly)
            with open(output_svg, 'r', encoding='utf-8') as f:
                svg_content = f.read()
                st.image(svg_content)

        except json.JSONDecodeError:
            st.error("Failed to parse the model response as JSON. Check the output above.")
    else:
        st.warning("No response generated or an error occurred.")
