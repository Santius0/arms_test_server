import streamlit as st
import requests

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
        response = requests.post(ENDPOINT_URL, json=payload, headers=headers)
        # response.raise_for_status()
        # model_answer_full = response.json().get("response", "")
        # response_start = "### Response:\n"
        # model_answer = model_answer_full.split(response_start, 1)[-1].strip() if response_start in model_answer_full else model_answer_full
        # return model_answer
        response
    except requests.exceptions.RequestException as e:
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
            st.error("Failed to get a response from the backend.")
    else:
        st.warning("Please enter a query.")

# Footer
st.sidebar.markdown("### About")
st.sidebar.info("This app uses a custom backend to provide AI-powered responses using the 'llama3.2' model.")
