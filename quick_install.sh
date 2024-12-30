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
else
  echo "You have not toggled the -conda flag. You are responsible for managing the dependency conflicts. To install using a conda environment, use the -conda flag"
fi

pip install -q -U google-generativeai
pip install langchain
pip install python-dotenv
pip install jupyter # jupyter notebooks is for experimental scripting - this should be removed after deployment
pip install "pinecone-client[grpc]"
pip install -U "protobuf==5.26.1"
pip install beautifulsoup4
pip install flask
pip install Flask-Cors

echo "All packages have been installed successfully!"

# Define the file name
ENV_FILE=".env"

cd backend
# Check if the file exists
if [ ! -f "$ENV_FILE" ]; then
  # File does not exist, create it and write lines
  echo "'$ENV_FILE' file does not yet exist. Creating and writing to it..."
    cat > "$ENV_FILE" << EOF
    GOOGLE_GENAI_API_KEY = "INSERT API KEY HERE"
    PINECONE_API_KEY = "INSERT API KEY HERE"
EOF
   echo "'$ENV_FILE' file was created successfully with two lines of text"
else
  # File already exists, print a message
  echo "'$ENV_FILE' file already exists. No changes were made."
fi
cd ..

# install all npm requirements
cd frontend
npm install
cd .. # return to parent directory