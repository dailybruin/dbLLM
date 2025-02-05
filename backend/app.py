import os
import time
from dotenv import load_dotenv
import logging
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

#pip install --upgrade google-auth
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from pinecone.grpc import PineconeGRPC as Pinecone
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


from modules.articleCleaner import clean_article
from modules.articleFetcher import fetchArticleById
from modules.embeddingFuncs import generateQueryEmbedding

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Only show errors and critical messages
CORS(app, supports_credentials=True)  # Enable CORS for all routes and origins

# endpoint to query 
# ex: http://10.0.0.14:5000/query?index=main&query=Did+ucla+football+beat+usc

# Load environment variables from .env file
print("\n----LOADING ENVIRONMENT VARIABLES----")
load_dotenv()

# Access variables
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# Configure the Google Generative AI library
genai.configure(api_key=GOOGLE_GENAI_API_KEY)

# Configure the Pinecone database
pc = Pinecone(api_key=PINECONE_API_KEY)

generation_config = {
  "temperature": 1.5,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 2048, # you can control the length of output
}

model_name = "gemini-2.0-flash-exp"
#model_name = "gemini-1.5-flash-8b"
model = genai.GenerativeModel(
  model_name= model_name,
  generation_config=generation_config,
)

# Safety Settings are currently set to MAX
# See official documentation: https://ai.google.dev/gemini-api/docs/safety-settings?t
safety_settings = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    # HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE, # I'm not sure what this category is
}

NUM_ARTICLES_QUERY = 5

print("----LOADED ENVIRONMENT VARIABLES----")

@app.route('/api/get_message/')
def get_message():
    try:
        response = model.generate_content(
            "type 'hi'",
        )
        if response.text:
            return jsonify({"message": 'Connection Successful', "model": model_name})
        else:
            return jsonify({"message": "Unknown Error."})
    except Exception as e:
        return jsonify({"message": f'Encountered Error {str(e)}'})
    
"""
HANDLING USER AUTHENTICATION
"""
@app.route('/api/login/', methods=['POST']) 
def login():
    print(request.json)
    TOKEN = request.json['token']
    resp = make_response('Response')

    if not TOKEN:
        print("No token provided.")
        resp.status_code = 400
        return resp

    try:
        # Verify the token using Google's OAuth2 library
        id_info = id_token.verify_oauth2_token(TOKEN, google_requests.Request(), GOOGLE_CLIENT_ID)

        # Check if the email is verified and belongs to the correct domain
        email = id_info.get('email')
        email_verified = id_info.get('email_verified', False)

        if email_verified and email.endswith("@media.ucla.edu"):
            resp.status_code = 200
            resp = jsonify({
                "name": id_info.get('name'),
                "email": email
            })
            print("Login successful.")
        else:
            resp.status_code = 401
            print("Login unsuccessful. Not a student media email or email not verified.")
    except ValueError as e:
        print(f"Invalid token: {e}")
        resp.status_code = 401

    return resp

"""
LIVE TIMING FUNCTIONS
"""
timer_start_time = None
timer_running = False
timer_duration = 0
timer_start_timeR = None
timer_runningR = False
timer_durationR = 0
def timer():
    """
    Toggle timer function that starts/stops the timer.
    Returns the timer's state and duration.
    """
    global timer_start_time, timer_running, timer_duration
    
    if not timer_running:
        # Start the timer
        timer_start_time = time.time()
        timer_running = True
        return jsonify({"status": "started"})
    else:
        # Stop the timer
        timer_running = False
        end_time = time.time()
        timer_duration = end_time - timer_start_time
        return jsonify({
            "status": "stopped",
            "duration": str(timer_duration)
        })

@app.route('/api/get_timer/')
def get_timer():
    global timer_start_time, timer_running, timer_duration
    
    if timer_start_time and timer_running:
        current_time = time.time()
        current_duration = current_time - timer_start_time
        return jsonify({
            "status": "running",
            "duration": str(current_duration)
        })
    elif not timer_running and timer_start_time:
        return jsonify({
            "status": "stopped",
            "duration": str(timer_duration)
        })
    else:
        return jsonify({"status": "waiting"})
    
# Response Timer
def timerR():
    """
    Toggle timer function that starts/stops the timer.
    Returns the timer's state and duration.
    """
    global timer_start_timeR, timer_runningR, timer_durationR
    
    if not timer_runningR:
        # Start the timer
        timer_start_timeR = time.time()
        timer_runningR = True
        return jsonify({"status": "started"})
    else:
        # Stop the timer
        timer_runningR = False
        end_time = time.time()
        timer_durationR = end_time - timer_start_timeR
        return jsonify({
            "status": "stopped",
            "duration": str(timer_durationR)
        })

@app.route('/api/get_timerR/')
def get_timerR():
    global timer_start_timeR, timer_runningR, timer_durationR
    
    if timer_start_timeR and timer_runningR:
        current_time = time.time()
        current_duration = current_time - timer_start_time
        return jsonify({
            "status": "running",
            "duration": str(current_duration)
        })
    elif not timer_runningR and timer_start_timeR:
        return jsonify({
            "status": "stopped",
            "duration": str(timer_durationR)
        })
    else:
        return jsonify({"status": "waiting"})

# Disable logging for these constant update functions

"""
AUTHENTICATION HELPER FUNCTION USED IN QUERY ROUTE
"""
def isAuthenticated(TOKEN: str) -> bool:
    try:
        # Verify the token using Google's OAuth2 library
        id_info = id_token.verify_oauth2_token(TOKEN, google_requests.Request(), GOOGLE_CLIENT_ID)

        # Check if the email is verified and belongs to the correct domain
        email = id_info.get('email')
        email_verified = id_info.get('email_verified', False)

        if email_verified and email.endswith("@media.ucla.edu"):
            return True
        else:
            return False
    except ValueError as e:
        return False
    
@app.route('/api/query/', methods=['GET'])
def query():
    if "token" not in request.args:
        return jsonify({"response": "Unauthorized. Please sign in with a student media account."}), 401
    
    jwt_token = request.args.get('token')
    if not isAuthenticated(jwt_token):
        return jsonify({"response": "Unauthorized. Please sign in with a student media account."}), 401
    
    DATABASE_INDEX_NAME = request.args.get('index')
    EMBEDDING_MODEL = "models/text-embedding-004"

    if DATABASE_INDEX_NAME not in pc.list_indexes().names():
        print("Invalid index name. Exiting.")
        exit()

    while not pc.describe_index(DATABASE_INDEX_NAME).status['ready']:
        time.sleep(1)

    index = pc.Index(DATABASE_INDEX_NAME)

    # Start query timer
    t0_query = time.time()
    user_query = request.args.get('query')
    if not user_query:
        return jsonify({"error": "No query parameter provided"}), 400

    embedding = generateQueryEmbedding(genai=genai,
                                       embedding_model=EMBEDDING_MODEL,
                                       query=user_query)

    results = index.query(
        vector=embedding,
        top_k=NUM_ARTICLES_QUERY,
        include_values=False,
        include_metadata=True
    )
    t1_query = time.time()
    query_time = round(t1_query - t0_query, 2)
    print(f'Querying took ~{query_time} seconds.')
    """ 
    /////////////////////////////////
    //////  Generate Response
    /////////////////////////////////
    """

    print("\n----GENERATING RESPONSE----")
    
    t0_response = time.time() # start timer for generating response
    timerR()
    # Generate context for the response
    context = ""

    for result in results['matches']:
        # Get ID (incase it's a chunk, only get whatever is before '_')
        # ex: if id="18352_chunk0", we only want id="18352"
        id = result['id'].split('_')[0]

        # Get article
        article = fetchArticleById(id)

        # Clean article
        cleanedArticle = clean_article(article)

        # Add context to feed into LLM
        link = result['metadata']['link']
        context += f"""\nARTICLE START (Source: {link})\n
        {cleanedArticle}
        \nARTICLE END\n
        """

    instructions = f"""
    # Who You Are:
    You are an advanced RAG LLM named Oliver, serving the UCLA Daily Bruin Newspaper.
    Given a user query, do your best to answer the question using the context provided, which will be embedded articles.
    
    However, there is a possibility that the user is asking a question that is not at all related to the Daily Bruin Newspaper articles.
    In that case, you must refuse to assist and insist that you can only answer queries related to the Daily Bruin (be nice though).
    
    # Instructions
    ## Response Guidelines
    You are a news source. You will quote your sources and provide links to the articles you are referencing.
    All quoted sources must be from the Context below, which is pulled from a database of our (Daily Bruin's) newspaper articles.
    You will not invent anything that is not drawn directly from the context.
    Limit responses to a 3 sentences. Pack this short paragraph with as much information as possible, while keeping it concise.
    
    # User Query:
    {user_query}

    # Context (Pulled from RAG Database)
    {context}
    
    # Response Formatting:
    You will output your response in MARKDOWN format.
    There are 2 rules you MUST follow:
    1. ALL links must be hyperlinked using Markdown format [text](link)
    2. The reference text must NOT be the original link. The reference text must be natural language that flows with the rest of the sentence.
    There are **absolutely no exceptions to this rule**. You **MUST** output all links in the markdown format as a hyperlink.
    
    ## Hyperlinking Examples
    Follow these examples to produce proper hyperlinks. **It is vital that you produce links in this exact format in order to render to the user properly.**
    
    - Some articles also mention specific teams, players, and seasons as [reported by xyz](https://dailybruin.com/2009/10/25/football_v-_arizona/)
    - ...and a [comparison to soccer](https://dailybruin.com/2006/10/25/ifootball-and-a-spot-of-teai/)
    - The Daily Bruin is the student newspaper of the UCLA community as mentioned in the annual Orientation Issue [as seen here](https://dailybruin.com/tag/oissue-23)
    - ...as detailed in this [article](https://dailybruin.com/2024/05/03/daily-bruin-print-issue-may-3/)
    - The Daily Bruin also had a TV program that became [Daily Bruin Video](https://dailybruin.com/2009/09/20/prodvideo/).
    """
    
    # Generate response 
    # model = genai.GenerativeModel("gemini-2.0-flash-exp")
    try:
        response = model.generate_content(
            instructions,
            safety_settings=safety_settings
        )
        t1_response = time.time()
        response_time = round(t1_response - t0_response, 2)
        return jsonify({
            "response": response.text,
            "query_time": query_time,
            "response_time": response_time
        })
    except Exception as e:
        print(e)
        model_old = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )
        response = model_old.generate_content(
            instructions,
            safety_settings=safety_settings
        )
        t1_response = time.time()
        response_time = round(t1_response - t0_response, 2)
        return jsonify({
            "response": response.text,
            "query_time": query_time,
            "response_time": response_time
        })


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
