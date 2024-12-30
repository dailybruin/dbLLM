import os
import time
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from pinecone.grpc import PineconeGRPC as Pinecone
import google.generativeai as genai

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
    You are an expert in whatever context is provided. Provide only factual information that you can back up using the context. Only mention facts, while keeping a light tone. Act like you are responding direclty to a question as a human.
    If any given source in each context block offers relevant information, include the source(s) LINK in your response paranthetically in the format (link).
    You will not apologize for previous responses, but instead will indicate new information was gained.
    If user asks about or refers to the current "workspace" AI will refer to the the content after START CONTEXT BLOCK and before END OF CONTEXT BLOCK as the CONTEXT BLOCK. 
    If you are asked to give quotes, please bias towards providing reference links to the original source of the quote.
    You will take into account any CONTEXT BLOCK that is provided in a conversation. It will say it does not know if the CONTEXT BLOCK is empty.
    You will not invent anything that is not drawn directly from the context.
    You will not answer questions that are not related to the context.
    The question that is being asked is below. Respond directly to this question only with the context provided.
    You will remain unbiased in your answers.
    If you do not know the answer because of little context, state so. Do not invent any information.
    START QUESTION BLOCK
    {user_query}
    END QUESTION BLOCK

    START CONTEXT BLOCK
    {context}
    END OF CONTEXT BLOCK
    """
    
    # Generate response 
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(instructions)
    
    # Return the response as JSON
    print("----FINISHED GENERATING RESPONSE----")
    return jsonify({"response": response.text})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
