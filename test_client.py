import streamlit as st
import requests
import logging
import json
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

st.title("Llama Model Chat App")
st.sidebar.title("Settings")

user_input = st.text_input("Enter your query:", "", placeholder="Type your question here")

ENDPOINT_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "arms_unsloth_ollama_model"

alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""


# Helper function to parse multiple JSON objects in a single string
def parse_multiple_json(raw_text: str):
    """
    Looks for consecutive JSON objects (e.g. {...} {...}) and parses them.
    Returns a list of Python dicts.
    """
    # Regex pattern to capture { ... } blocks.
    # The '(?=\s*\{|$)' part ensures we stop right before the next '{' or the end of string.
    pattern = re.compile(r'(\{.*?\})(?=\s*\{|$)')
    json_strings = pattern.findall(raw_text)

    results = []
    for js in json_strings:
        try:
            data = json.loads(js)
            results.append(data)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON chunk: {e}")
    return results


def query_backend(model_name, instruction, input_text):
    try:
        headers = {"Content-Type": "application/json"}
        prompt = alpaca_prompt.format(instruction, input_text, "")
        payload = {
            "model": model_name,
            "prompt": prompt
        }

        logging.debug(f"Sending payload to backend: {payload}")
        response = requests.post(ENDPOINT_URL, json=payload, headers=headers)
        response.raise_for_status()

        # Debug: show raw text
        raw_text = response.text
        logging.debug(f"Raw response text:\n{raw_text}")

        # We now handle multiple JSON objects in raw_text
        json_chunks = parse_multiple_json(raw_text)

        if not json_chunks:
            # No valid JSON found
            logging.warning("No valid JSON objects found in response.")
            return None

        # Typically, the last chunk might contain the final "done" response.
        # You can choose whichever chunk you want. For example:
        last_chunk = json_chunks[-1]

        # If the chunk has a "response" field
        model_answer_full = last_chunk.get("response", "")

        response_start = "### Response:\n"
        if response_start in model_answer_full:
            model_answer = model_answer_full.split(response_start, 1)[-1].strip()
        else:
            model_answer = model_answer_full

        return model_answer

    except requests.exceptions.RequestException as e:
        logging.error(f"Error communicating with the backend: {e}", exc_info=True)
        st.error(f"Error communicating with the backend: {e}")
        return None


if st.button("Submit"):
    if user_input.strip():
        with st.spinner("Querying the backend..."):
            result = query_backend(MODEL_NAME, "Complete the following task:", user_input)
        if result:
            st.success("Response:")
            st.write(result)
        else:
            logging.error("Failed to get a valid response from the backend.")
            st.error("Failed to get a response from the backend.")
    else:
        st.warning("Please enter a query.")

st.sidebar.markdown("### About")
st.sidebar.info("This app uses a custom backend to provide AI-powered responses using the 'llama3.2' model.")
