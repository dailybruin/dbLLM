# LLM Project for the Daily Bruin Main Site

## Installation Guide

1. Clone the repository
`git clone https://github.com/dailybruin/dbLLM`

<!-- 2. Install dependencies
`pip install -r requirements.txt` -->

2. Install dependencies
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
GOOGLE_GEMINI_API_KEY="your_google_gemini_api_key"
PINECONE_API_KEY="your_pinecone_api_key"
```

- To get your Google Gemini API key, go to https://aistudio.google.com/apikey and click the bright blue "Get API Key" button on the top left
- To get your Pinecone API key, go to your Pinecone account, click "API Keys"

Replace the values in the quotes with your own API keys

5. Run store.py to store articles into the database

   
7. Run query.py to run a query and get a response

