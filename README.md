# LLM Project for the Daily Bruin Main Site

## About
*As of Aug 2025, this site is live at https://oliver.dailybruin.com/ and access is limited to Daily Bruin members for beta testing.*

This project aims to combine the forefront of AI with news, directly integrating summaries of articles and finding **exactly** the news you're looking for with the click of a few buttons.

Project pictures:
<img width="1918" height="941" alt="image" src="https://github.com/user-attachments/assets/abeed2ea-a503-4939-8d55-b4a5832bf735" />
<img width="961" height="470" alt="image" src="https://github.com/user-attachments/assets/e5f0fff9-8fce-4df8-b564-05aa9ef32371" />

## Local Installation Guide

1. Clone the repository
```
git clone https://github.com/dailybruin/dbLLM
```

### Quick Installation (Fastest)
* We have taken the liberty of creating a shell script to get everything installed properly with just two quick commands!
* However, if you would like to go through every step yourself, the full instructions are listed below. This shortcut command creates a conda environment, installs all dependencies, and creates a .env file for you (if it doesn't already exist)

<br>

* If you want to create the conda environment as well, use the -conda flag when running the shell script (./quick_install.sh -conda).
  * Otherwise, <ins>ensure that you are running this in your preferred environment</ins>

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
pip install --upgrade google-auth
pip install langchain
pip install python-dotenv
pip install "pinecone-client[grpc]"
pip install -U "protobuf==5.26.1"
pip install beautifulsoup4
pip install flask
pip install Flask-Cors
```

3. Create a .env file in the *backend* directory of the project. This is the file that will store your API keys for Pinecone and Google Gemini.

4. Inside of the .env file, create the following variables:
```
GOOGLE_GENAI_API_KEY="your_google_gemini_api_key"
GOOGLE_CLIENT_ID = "your_client_id"
PINECONE_API_KEY="your_pinecone_api_key"
```

- To get your Google Gemini API key, go to https://aistudio.google.com/apikey and click the bright blue "Get API Key" button on the top left
- To get your Pinecone API key, go to your Pinecone account, click "API Keys"

Replace the values in the quotes with your own API keys

5. Create a .env in the *frontend* directory of the project. This is the file that will store yor ID for UCLA user authentication.

6. Inside of the .env file, create the following variable:
```
VITE_GOOGLE_CLIENT_ID="your_vite_google_client_id"
```

Replace the value in quote with your own client ID

<br>

### Running the App
* Our web app's backend and frontend are separated into different folders, and each must be started independently.

* Ensure that you have all environment variables inputted in both .env files (one in frontend, one in backend).

#### Building Frontend
To build the frontend, change directory into the frontend folder and run npm install (you will have to do this every time we decide to update the frontend). Then, npm run dev starts the development server.

```
cd frontend
npm install
npm run dev
```

Make sure that you actually run npm install in the frontend folder and NOT the parent directory. If you run npm install in the parent directory, it will install the dependencies for the backend and not the frontend, and it will also create a package-lock.json file in the parent directory that we do not want.

#### Building Backend
To run the backend, switch over to the backend folder and run python3 app.py. This can be done in a new terminal window.

```
cd backend
python3 app.py
```

#### Accessing The Website
The website should start running in a new localhost port. Features on the website are only available if signed in with a UCLA Student Media Google Account.

<br>

### Other Features
-> Here's a link to the [technical outline](https://docs.google.com/document/d/1mlp1-htnD-S_U9HNwkMEw_ET3oo_sdBvaeePSHk90zc/edit?usp=sharing) if you need more insight into how this works.

* Run store.py to store articles into the database
* Run query.py to run a query and get a response
* Run update.py to update the vector database with all new articles
   * On first run, you will need to change the date in lastSynced.txt to get articles only published *after* that date
   * If there's no date in lastSynced.txt or the date is in the incorrect format, update.py will not run correctly
