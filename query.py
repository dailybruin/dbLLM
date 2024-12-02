import os
import time
from dotenv import load_dotenv

from pinecone.grpc import PineconeGRPC as Pinecone
import google.generativeai as genai

from modules.articleCleaner import clean_article
from modules.articleFetcher import fetchArticleById
from modules.embeddingFuncs import generateQueryEmbedding

print("\n----LOADING ENVIRONMENT VARIABLES----")
# Load environment variables from .env file
load_dotenv()

# Access variables
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Configure the Google Generative AI library
genai.configure(api_key=GOOGLE_GENAI_API_KEY)

# Configure the Pinecone database
pc = Pinecone(api_key=PINECONE_API_KEY)

# Constants used throughout
DATABASE_INDEX_NAME = str(input("Enter database index name, (hit enter for default of 768dim): "))
EMBEDDING_MODEL = "models/text-embedding-004"

if (DATABASE_INDEX_NAME == ""):
    DATABASE_INDEX_NAME = "768dim"

print("----FINISHED LOADING ENVIRONMENT VARIABLES----")

""" 
/////////////////////////////////
//////  Query
/////////////////////////////////
"""
print("\n----QUERYING----")
query = str(input("Ask any question: "))

embedding = generateQueryEmbedding(genai=genai,
                                   embedding_model=EMBEDDING_MODEL,
                                   query=query)

# Wait for the index to be ready
while not pc.describe_index(DATABASE_INDEX_NAME).status['ready']:
    print("Waiting for index...")
    time.sleep(1)

print("Index connected.")
index = pc.Index(DATABASE_INDEX_NAME)

results = index.query(
    vector=embedding,
    top_k=5,
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
model = genai.GenerativeModel("gemini-1.5-flash")

context = ""

for result in results['matches']:
    # Get ID (incase it's a chunk, only get whatever is before '_' - ex: 18352_chunk0)
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
DO NOT SHARE REFERENCE URLS THAT ARE NOT INCLUDED IN THE CONTEXT BLOCK.
You will not apologize for previous responses, but instead will indicate new information was gained.
If user asks about or refers to the current "workspace" AI will refer to the the content after START CONTEXT BLOCK and before END OF CONTEXT BLOCK as the CONTEXT BLOCK. 
If you are asked to give quotes, please bias towards providing reference links to the original source of the quote.
You will take into account any CONTEXT BLOCK that is provided in a conversation. It will say it does not know if the CONTEXT BLOCK is empty.
You will not invent anything that is not drawn directly from the context.
You will not answer questions that are not related to the context.
The question that is being asked is below. Respond directly to this question only with the context provided.
START QUESTION BLOCK
{query}
END QUESTION BLOCK

START CONTEXT BLOCK
{context}
END OF CONTEXT BLOCK
"""

# Generate a response
response = model.generate_content(instructions)

# Display response
print("Response created:\n")
print(response.text)
print("----FINISHED GENERATING RESPONSE----")