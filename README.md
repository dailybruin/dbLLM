# LLM Project for the Daily Bruin Main Site

## Installation Guide

1. Clone the repository
```
git clone https://github.com/dailybruin/dbLLM
```

### Quick Installation (Fastest)
We have taken the liberty of creating a shell script to get everything installed properly with just two quick commands! 
However, if you would like to go through every step yourself, the full instructions are listed below. This shortcut command creates a conda environment, installs all dependencies, and creates a .env file for you (if it doesn't already exist)

If you want to create the conda environment as well, use the -conda flag when running the shell script (./quick_install.sh -conda)

In your (Linux/Mac) terminal: 
```
chmod +x quick_install.sh
./quick_install.sh
```

### Step by Step Installation (if not doing Quick Installation)

#### Backend Installation
2. Install dependencies (recommended in a virtual environment). This project runs on (any) Python version 3.9
```
pip install -q -U google-generativeai
pip install langchain
pip install python-dotenv
pip install jupyter
pip install "pinecone-client[grpc]"
pip install -U "protobuf==5.26.1"
pip install beautifulsoup4
```

3. Create a .env file in the root directory of the project. This is the file that will store your API keys for Pinecone and Google Gemini.

4. Inside of the .env file, create the following variables:
```
GOOGLE_GENAI_API_KEY="your_google_gemini_api_key"
PINECONE_API_KEY="your_pinecone_api_key"
```

- To get your Google Gemini API key, go to https://aistudio.google.com/apikey and click the bright blue "Get API Key" button on the top left
- To get your Pinecone API key, go to your Pinecone account, click "API Keys"

Replace the values in the quotes with your own API keys

5. Run store.py to store articles into the database
   
7. Run query.py to run a query and get a response

#### Running the App
Our web app's backend and frontend are separated into different folders. To build the frontend, change directory into the frontend folder and run npm install (you will have to do this every time we decide to update the frontend)

```
pip install flask

cd frontend
npm install
```

Make sure that you actually run npm install in the frontend folder and NOT the parent directory. If you run npm install in the parent directory, it will install the dependencies for the backend and not the frontend, and it will also create a package-lock.json file in the parent directory that we do not want.

To run the backend, switch over to the backend folder and run python app.py

```
cd backend
python app.py
```