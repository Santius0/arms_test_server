#!/bin/bash

# Step 1: Check if ollama is installed, and install if not
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

# Step 2: Clone the GitHub repository
GITHUB_REPO_URL="<github-repo-url>"
REPO_DIR="my-repo"

echo "Cloning the GitHub repository..."
git clone "$GITHUB_REPO_URL" "$REPO_DIR"
if [ $? -ne 0 ]; then
    echo "Failed to clone GitHub repository. Exiting."
    exit 1
fi

# Step 3: Download the GGUF model from Hugging Face
HUGGING_FACE_MODEL_URL="<hugging-face-repo-url>"
MODEL_DIR="${REPO_DIR}/downloaded_model"

mkdir -p "$MODEL_DIR"
echo "Downloading GGUF model from Hugging Face..."
wget -O "$MODEL_DIR/unsloth.Q8_0.gguf" "$HUGGING_FACE_MODEL_URL"
if [ $? -ne 0 ]; then
    echo "Failed to download the GGUF model. Exiting."
    exit 1
fi

# Step 4: Navigate into the cloned repository
echo "Navigating into the cloned repository..."
cd "$REPO_DIR" || exit

# Step 5: Create the unsloth model using ollama
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
