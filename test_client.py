import streamlit as st
import requests

# API Endpoint Configuration
ENDPOINT_URL = "http://localhost:11434/api/generate"

# Prompt Template
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

# ----------------------------------------
# Session State Initialization
# ----------------------------------------
if "chat_history" not in st.session_state:
    # We'll store each message as a dict: {"role": "user"/"assistant", "content": "..."}
    st.session_state.chat_history = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "arms_unsloth_ollama_model"


# ----------------------------------------
# Functions
# ----------------------------------------
def query_backend(model_name, instruction, input_text):
    """
    Sends a request to the custom backend to generate a model response.
    """
    try:
        headers = {"Content-Type": "application/json"}
        prompt = alpaca_prompt.format(instruction, input_text, "")
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(ENDPOINT_URL, json=payload, headers=headers)
        response.raise_for_status()

        # Extract full response text
        model_answer_full = response.json().get("response", "")

        # Attempt to split out the "### Response:" section if it exists
        response_start = "### Response:\n"
        if response_start in model_answer_full:
            model_answer = model_answer_full.split(response_start, 1)[-1].strip()
        else:
            model_answer = model_answer_full

        return model_answer

    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the backend: {e}")
        return None


def send_message():
    """
    Callback to send the user input to the backend, store both user message and
    assistant response in the chat history, and clear the input.
    """
    user_text = st.session_state.user_input.strip()
    if user_text:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_text})

        # Query the model
        with st.spinner("Querying the backend..."):
            result = query_backend(
                model_name=st.session_state.selected_model,
                instruction="Complete the following task:",
                input_text=user_text
            )

        if result:
            # Add assistant message to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": result})
        else:
            st.error("Failed to get a response from the backend.")

    # Clear the text input box after sending
    st.session_state.user_input = ""


# ----------------------------------------
# Streamlit Page Layout
# ----------------------------------------
st.title("ARMS Test Model Chat App")

# Sidebar for Model Selection
st.sidebar.title("Settings")
model_options = [
    "arms_unsloth_ollama_model",
    "llama3.1_8B",
    "llama3.1_70B"
]
selected_model = st.sidebar.selectbox(
    "Select a model:",
    model_options,
    index=model_options.index(st.session_state.selected_model) \
        if st.session_state.selected_model in model_options else 0
)
st.session_state.selected_model = selected_model

# Main Chat Interface
st.write("Welcome! Type your questions or commands below and press **Enter** to submit.")

# Display the chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        # User messages on the right
        st.markdown(
            f"<div style='text-align:right; padding:5px; border-radius:10px; background-color:#f0f0f5; margin:10px;'>"
            f"<strong>You:</strong> {message['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        # Assistant messages on the left
        st.markdown(
            f"<div style='text-align:left; padding:5px; border-radius:10px; background-color:#e8f4f8; margin:10px;'>"
            f"<strong>Assistant:</strong> {message['content']}</div>",
            unsafe_allow_html=True
        )

# Text input for user message - triggers send_message() on Enter
st.text_input(
    "Your message:",
    key="user_input",
    placeholder="Type your message and press Enter...",
    on_change=send_message
)

# Footer
st.sidebar.markdown("### About")
st.sidebar.info(
    f"This app uses a custom backend to provide AI-powered responses using the '{selected_model}' model."
)
