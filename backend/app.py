import os
import time
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from pinecone.grpc import PineconeGRPC as Pinecone
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


from modules.articleCleaner import clean_article
from modules.articleFetcher import fetchArticleById
from modules.embeddingFuncs import generateQueryEmbedding

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# endpoint to query 
# ex: http://10.0.0.14:5000/query?index=main&query=Did+ucla+football+beat+usc

# Load environment variables from .env file
print("\n----LOADING ENVIRONMENT VARIABLES----")
load_dotenv()

# Access variables
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Configure the Google Generative AI library
genai.configure(api_key=GOOGLE_GENAI_API_KEY)

# Configure the Pinecone database
pc = Pinecone(api_key=PINECONE_API_KEY)

generation_config = {
  "temperature": 1.5,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192, # you can control the length of output
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
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

@app.route('/query', methods=['GET'])
def query():
    # Constants used throughout
    DATABASE_INDEX_NAME = request.args.get('index')  #get index parameter from the URL
    EMBEDDING_MODEL = "models/text-embedding-004"

    # check if the index exists
    if DATABASE_INDEX_NAME not in pc.list_indexes().names():
        print("Invalid index name. Exiting.")
        exit()

    # Wait for the index to be ready
    while not pc.describe_index(DATABASE_INDEX_NAME).status['ready']:
        print("Waiting for index...")
        time.sleep(1)

    print("Index connected.")
    index = pc.Index(DATABASE_INDEX_NAME)
    print("----FINISHED LOADING ENVIRONMENT VARIABLES----")

    """ 
    /////////////////////////////////
    //////  Query
    /////////////////////////////////
    """

    # get query parameter from the URL
    user_query = request.args.get('query')
    
    if not user_query:
        return jsonify({"error": "No query parameter provided"}), 400
    
    print("\n----QUERYING----")

    # Generate query embedding
    embedding = generateQueryEmbedding(genai=genai,
                                       embedding_model=EMBEDDING_MODEL,
                                       query=user_query)

    # Query Pinecone index
    results = index.query(
        vector=embedding,
        top_k=10,
        include_values=False,
        include_metadata=True
    )
    print("----FINISHED QUERYING----")

    """ 
    /////////////////////////////////
    //////  Generate Response
    /////////////////////////////////
    """

    print("\n----GENERATING RESPONSE----")
    
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
    ## Who You Are:
    You are an advanced RAG LLM named Oliver, serving the UCLA Daily Bruin Newspaper.
    Given a user query, do your best to answer the question using the context provided, which will be embedded articles.
    You will ALWAYS output your responses using Markdown formatting. 
    
    However, there is a possibility that the user is asking a question that is not at all related to the Daily Bruin Newspaper articles.
    In that case, you must refuse to assist and insist that you can only answer queries related to the Daily Bruin (be nice though).
    
    If any given source in each context block offers relevant information, include the source(s) LINK in your response.
    You will not apologize for previous responses, but instead will indicate new information was gained.
    If user asks about or refers to the current "workspace" AI will refer to the the content after START CONTEXT BLOCK and before END OF CONTEXT BLOCK as the CONTEXT BLOCK. 
    If you are asked to give quotes, please bias towards providing reference links to the original source of the quote.
    You will take into account any CONTEXT BLOCK that is provided in a conversation. It will say it does not know if the CONTEXT BLOCK is empty.
    You will not invent anything that is not drawn directly from the context.
    You will not answer questions that are not related to the context.
    The question that is being asked is below. Respond directly to this question only with the context provided.
    You will remain unbiased in your answers.
    If you do not know the answer because of little context, state so. Do not invent any information.
    
    ## Instructions for Response Formatting:
    You will output your response in MARKDOWN format. ALL links no matter what must be hyperlinked using the markdown format [text](link).
    There are two rules you MUST follow:
    1. ALL links must be hyperlinked
    2. The reference link must NOT be the original link. The reference link must be natural language that flows with the rest of the sentence. Do your best to integrade the hyperlinks as naturally as possible with the flow of the rest of the sentence. 
    There are absolutely no exceptions to this rule. You MUST output all links in the markdown format as a hyperlink.
    Despite being required to quote sources, integrate them into your response in a natural and friendly way.
    
    An example of your hyperlinking would be:
    - Some articles also mention specific teams, players, and seasons as [reported by xyz](https://dailybruin.com/2009/10/25/football_v-_arizona/)
    - ...and a [comparison to soccer](https://dailybruin.com/2006/10/25/ifootball-and-a-spot-of-teai/)
    
    START QUESTION BLOCK
    {user_query}
    END QUESTION BLOCK

    START CONTEXT BLOCK
    {context}
    END OF CONTEXT BLOCK
    """
    
    # Generate response 
    # model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content(
        instructions,
        safety_settings=safety_settings
    )
    
    # Return the response as JSON
    print("----FINISHED GENERATING RESPONSE----")
    print(f'User: {user_query}')
    print(f'Oliver: {response.text}')
    return jsonify({"response": response.text})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
