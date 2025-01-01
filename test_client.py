import streamlit as st
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Streamlit App Configuration
st.title("Llama Model Chat App")
st.sidebar.title("Settings")

# User Input
user_input = st.text_input("Enter your query:", "", placeholder="Type your question here")

# API Endpoint Configuration
ENDPOINT_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "arms_unsloth_ollama_model"

# Prompt Template
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""


# Function to send request to the custom backend
def query_backend(model_name, instruction, input_text):
    try:
        headers = {"Content-Type": "application/json"}
        prompt = alpaca_prompt.format(instruction, input_text, "")
        payload = {
            "model": model_name,
            "prompt": prompt
        }

        # Logging the payload for debugging
        logging.debug(f"Sending payload to backend: {payload}")

        response = requests.post(ENDPOINT_URL, json=payload, headers=headers)
        response.raise_for_status()

        # Log the raw JSON for debug-level
        logging.debug(f"Raw response JSON: {response.text}")

        # Parse JSON
        response_json = response.json()

        # If "response" key doesn't exist, log a warning
        if "response" not in response_json:
            logging.warning("The 'response' key was not found in the JSON from the backend.")

        model_answer_full = response_json.get("response", "")
        response_start = "### Response:\n"

        model_answer = (
            model_answer_full.split(response_start, 1)[-1].strip()
            if response_start in model_answer_full
            else model_answer_full
        )
        return model_answer

    except requests.exceptions.RequestException as e:
        # Log the error to the console
        logging.error(f"Error communicating with the backend: {e}", exc_info=True)
        # Show the error in Streamlit UI
        st.error(f"Error communicating with the backend: {e}")
        return None


# Submit Button
if st.button("Submit"):
    if user_input.strip():
        with st.spinner("Querying the backend..."):
            result = query_backend(MODEL_NAME, "Complete the following task:", user_input)
        if result:
            st.success("Response:")
            st.write(result)
        else:
            # Log the failure to the console
            logging.error("Failed to get a valid response from the backend.")
            st.error("Failed to get a response from the backend.")
    else:
        st.warning("Please enter a query.")

# Footer
st.sidebar.markdown("### About")
st.sidebar.info("This app uses a custom backend to provide AI-powered responses using the 'llama3.2' model.")
