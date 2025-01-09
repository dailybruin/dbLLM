#!/bin/bash

set -e  # Exit immediately if a command fails

# create conda environment if -conda flag is provided
if [[ "$1" == "-conda" ]]; then
  echo "Checking if conda is installed at path..."
  if ! command -v conda &> /dev/null; then
    echo "Error: Conda is not installed or not in your PATH. Please install conda and try again."
    exit 1
  fi
  echo "Creating Anaconda environment 'dbllm' with latest version of Python 3.9..."
  conda create -n dbllm python=3.9
  conda activate dbllm
else
  echo "You have not toggled the -conda flag. You are responsible for managing the dependency conflicts. To install using a conda environment, use the -conda flag"
fi

echo "Starting installation process..."
echo "Please make sure that you are installing these packages into the correct environment. Once you have verified that, enter 'CONTINUE' to continue with the installation"


# Wait for the correct keyword
keyword="CONTINUE"
while true; do
    read -p "Enter 'CONTINUE' to proceed with the installation " userInput
    if [[ "$userInput" == "$keyword" ]]; then
        echo "Continuing with installation..."
        break
    else
        echo "Please enter 'CONTINUE' to continue with the installation process."
    fi
done

pip install -q -U google-generativeai
pip install --upgrade google-auth
pip install langchain
pip install python-dotenv
pip install "pinecone-client[grpc]"
pip install -U "protobuf==5.26.1"
pip install beautifulsoup4
pip install flask
pip install Flask-Cors

echo "All packages have been installed successfully!"

# Define the file name
ENV_FILE=".env"

# Create backend .env file
cd backend
# Check if the file exists
if [ ! -f "$ENV_FILE" ]; then
  # File does not exist, create it and write lines
  echo "Backend environment file does not yet exist. Creating and writing to it..."
    cat > "$ENV_FILE" << EOF
GOOGLE_GENAI_API_KEY = "INSERT API KEY HERE"
GOOGLE_CLIENT_ID = "INSERT CLIENT ID HERE"
PINECONE_API_KEY = "INSERT API KEY HERE"
EOF
   echo "'Backend environment file was created successfully with empty keys and ID"
else
  # File already exists, print a message
  echo "Backend environment' file already exists. No changes were made."
fi
cd ..

# Create frontend .env file
cd frontend
# Check if the file exists
if [ ! -f "$ENV_FILE" ]; then
  # File does not exist, create it and write lines
  echo "Frontend environment file does not yet exist. Creating and writing to it..."
    cat > "$ENV_FILE" << EOF
VITE_GOOGLE_CLIENT_ID = "INSERT CLIENT ID HERE"
EOF
   echo "Frontend environment file was created successfully with empty ID"
else
  # File already exists, print a message
  echo "Frontend environment file already exists. No changes were made."
fi
cd ..

# install all npm requirements (in frontend)
cd frontend
npm install
cd .. # return to parent directory