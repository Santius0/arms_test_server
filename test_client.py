import streamlit as st
import requests

# Streamlit App Configuration
st.title("Ollama Backend Chat App")
st.sidebar.title("Settings")

# User Input
user_input = st.text_input("Enter your query:", "", placeholder="Type your question here")

# API Endpoint Configuration
OLLAMA_SERVER_URL = "http://localhost:11434"
MODEL_NAME = "arms_unsloth_ollama_model"

# Function to send request to Ollama backend
def query_ollama(model_name, prompt):
    try:
        url = f"{OLLAMA_SERVER_URL}/query"
        payload = {"model": model_name, "prompt": prompt}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with Ollama server: {e}")
        return None

# Submit Button
if st.button("Submit"):
    if user_input.strip():
        with st.spinner("Querying the Ollama backend..."):
            result = query_ollama(MODEL_NAME, user_input)
        if result and "response" in result:
            st.success("Response:")
            st.write(result["response"])
        else:
            st.error("Failed to get a response from the backend.")
    else:
        st.warning("Please enter a query.")

# Footer
st.sidebar.markdown("### About")
st.sidebar.info("This app uses the Ollama backend to provide AI-powered responses using the 'arms_unsloth_ollama_model'.")
