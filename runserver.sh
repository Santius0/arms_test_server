#!/bin/bash

# Check if ollama is installed, and install if not
if ! command -v ollama &> /dev/null
then
    echo "Ollama is not installed. Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    if [ $? -ne 0 ]; then
        echo "Failed to install Ollama. Exiting."
        exit 1
    fi
else
    echo "Ollama is already installed."
fi

# Download the GGUF model from Hugging Face
HUGGING_FACE_MODEL_URL="https://huggingface.co/santius0/arms_lora_model/"
MODEL_DIR="${REPO_DIR}/arms_lora_model"

mkdir -p "$MODEL_DIR"
echo "Downloading GGUF model from Hugging Face..."
wget -O "$MODEL_DIR/unsloth.Q8_0.gguf" "$HUGGING_FACE_MODEL_URL"
if [ $? -ne 0 ]; then
    echo "Failed to download the GGUF model. Exiting."
    exit 1
fi

# Create the unsloth model using ollama
echo "Creating the unsloth model with ollama..."
ollama create unsloth_model -f "$MODEL_DIR/unsloth.Q8_0.gguf"
if [ $? -ne 0 ]; then
    echo "Failed to create the unsloth model. Exiting."
    exit 1
fi

# Step 6: Run the Streamlit Python script
echo "Running the Streamlit Python script..."
streamlit run test_client.py --server.port 8501
if [ $? -ne 0 ]; then
    echo "Failed to run the Streamlit script. Exiting."
    exit 1
fi
