#!/bin/bash

# Parse command-line arguments
DOWNLOAD_MODEL=false
for arg in "$@"
do
    case $arg in
        -d|--download)
        DOWNLOAD_MODEL=true
        shift
        ;;
    esac
done

# Install required dependencies
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Installing Python3..."
    sudo apt update && sudo apt install -y python3
    if [ $? -ne 0 ]; then
        echo "Failed to install Python3. Exiting."
        exit 1
    fi
else
    echo "Python3 is already installed."
fi

if ! command -v pip3 &> /dev/null
then
    echo "Pip3 is not installed. Installing Pip3..."
    sudo apt update && sudo apt install -y python3-pip
    if [ $? -ne 0 ]; then
        echo "Failed to install Pip3. Exiting."
        exit 1
    fi
    python3 -m ensurepip --upgrade
    python3 -m pip install --upgrade pip
else
    echo "Pip3 is already installed."
fi

# Check if graphviz is installed at the system level
if ! command -v dot &> /dev/null
then
    echo "Graphviz is not installed. Installing Graphviz via apt..."
    sudo apt update && sudo apt install -y graphviz
    if [ $? -ne 0 ]; then
        echo "Failed to install Graphviz. Exiting."
        exit 1
    fi
else
    echo "Graphviz is already installed at the system level."
fi

# Install Python packages: streamlit, openai, graphviz
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

if ! python3 -m pip show openai &> /dev/null
then
    echo "OpenAI Python package is not installed. Installing OpenAI..."
    python3 -m pip install openai
    if [ $? -ne 0 ]; then
        echo "Failed to install OpenAI. Exiting."
        exit 1
    fi
else
    echo "OpenAI package is already installed."
fi

if ! python3 -m pip show graphviz &> /dev/null
then
    echo "Graphviz Python package is not installed. Installing Graphviz..."
    python3 -m pip install graphviz
    if [ $? -ne 0 ]; then
        echo "Failed to install Graphviz (Python package). Exiting."
        exit 1
    fi
else
    echo "Graphviz Python package is already installed."
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

# Download the GGUF model from Hugging Face if it doesn't exist or if download flag is set
HUGGING_FACE_MODEL_URL="https://huggingface.co/santius0/arms_lora_model/resolve/main/unsloth.Q8_0.gguf"
MODEL_DIR="arms_lora_model_gguf"
MODEL_PATH="$MODEL_DIR/unsloth.Q8_0.gguf"

if [ ! -f "$MODEL_PATH" ] || [ "$DOWNLOAD_MODEL" = true ]
then
    mkdir -p "$MODEL_DIR"
    echo "Downloading GGUF model from Hugging Face..."
    wget -O "$MODEL_PATH" "$HUGGING_FACE_MODEL_URL"
    if [ $? -ne 0 ]; then
        echo "Failed to download the GGUF model. Exiting."
        exit 1
    fi
else
    echo "ARMS model already exists. Skipping download."
fi

# If the download flag is set, also download the Llama 3.1 8B and 70B models via Ollama
if [ "$DOWNLOAD_MODEL" = true ]
then
    echo "Downloading llama3.1 8B model with Ollama..."
    ollama pull llama3.1:8b
    if [ $? -ne 0 ]; then
        echo "Failed to download the llama3.1-8b model. Exiting."
        exit 1
    fi

    echo "Downloading llama3.1 70B model with Ollama..."
    ollama pull llama3.1:70b
    if [ $? -ne 0 ]; then
        echo "Failed to download the llama3.1-70b model. Exiting."
        exit 1
    fi
fi

# Create the unsloth model using ollama
echo "Creating the unsloth model with ollama..."
ollama create arms_unsloth_ollama_model -f Modelfile
if [ $? -ne 0 ]; then
    echo "Failed to create the unsloth model. Exiting."
    exit 1
fi

# Run the Streamlit Python script
echo "Running the Streamlit Python script..."
streamlit run bowtie.py --server.port 8501
if [ $? -ne 0 ]; then
    echo "Failed to run the Streamlit script. Exiting."
    exit 1
fi
