#!/bin/bash

# Install required dependencies
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Installing Python3..."
    sudo apt update && sudo apt install -y python3 python3-pip
    if [ $? -ne 0 ]; then
        echo "Failed to install Python3. Exiting."
        exit 1
    fi
else
    echo "Python3 is already installed."
fi

if ! python3 -m pip show streamlit &> /dev/null
then
    echo "Streamlit is not installed. Installing Streamlit..."
    python3 -m pip install streamlit
    if [ $? -ne 0 ]; then
        echo "Failed to install Streamlit. Exiting."
        exit 1
    fi
else
    echo "Streamlit is already installed."
fi

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
MODEL_DIR="arms_lora_model_gguf"

mkdir -p "$MODEL_DIR"
echo "Downloading GGUF model from Hugging Face..."
wget -O "$MODEL_DIR/unsloth.Q8_0.gguf" "$HUGGING_FACE_MODEL_URL"
if [ $? -ne 0 ]; then
    echo "Failed to download the GGUF model. Exiting."
    exit 1
fi

# Create the unsloth model using ollama
echo "Creating the unsloth model with ollama..."
ollama create arms_unsloth_ollama_model -f "$MODEL_DIR/unsloth.Q8_0.gguf"
if [ $? -ne 0 ]; then
    echo "Failed to create the unsloth model. Exiting."
    exit 1
fi

# Run the Streamlit Python script
echo "Running the Streamlit Python script..."
streamlit run test_client.py --server.port 8501
if [ $? -ne 0 ]; then
    echo "Failed to run the Streamlit script. Exiting."
    exit 1
fi
