import os
import time
from dotenv import load_dotenv

from pinecone.grpc import PineconeGRPC as Pinecone
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter

from articleCleaner import clean_all_articles
from articleFetcher import fetchArticles
from embeddingFuncs import embedArticle
from embeddingFuncs import embedChunksAsArticle

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
DATABASE_INDEX_NAME = str(input("Enter database index name (hit enter for default of 768dim): "))
EMBEDDING_MODEL = "models/text-embedding-004"
MODEL_MAX_CHUNKS = 9500
CHUNK_OVERLAP = 200

if (DATABASE_INDEX_NAME == ""):
    DATABASE_INDEX_NAME = "768dim"

print("----FINISHED LOADING ENVIRONMENT VARIABLES----")

""" 
/////////////////////////////////
//////  Fetch and Clean Articles
/////////////////////////////////
"""
print("\n----FETCHING ARTICLES----")

# Fetch articles
try:
    STARTING_PAGE = int(input("Enter starting page (hit enter for default of 1): "))
except:
    STARTING_PAGE = 1
try:
    ENDING_PAGE = int(input("Enter ending page (hit enter for default of 3): "))
except:
    ENDING_PAGE = 3


articles = fetchArticles(starting_page=STARTING_PAGE, ending_page=ENDING_PAGE)

if (articles):
    # Clean articles
    print(len(articles), "articles successfully fetched")
    clean_all_articles(articles)
else:
    print("Error fetching articles.")
    exit()

print("----FINISHED FETCHING ARTICLES----")

""" 
/////////////////////////////////
//////  Embed Articles
/////////////////////////////////
"""
print("\n----GENERATING EMBEDDINGS----", end="\n")
# Generate embeddings
embeddings = []
ARTICLES_LEN = len(articles)
# Dynamic step calculation
update_factor = max(1, len(articles) // 100)

for i, article in enumerate(articles):
    content = article['content']['rendered']
    article_id = str(article['id'])
    
    # Only run if there is both content to embed and an id to associate it with
    if content and article_id:
        try:
            # Embed the article
            embedArticle(genai, embeddings, EMBEDDING_MODEL, article)
        
        # The article may be too big. In that case, try splitting it into chunks
        except Exception as e:
            print(f"\nError generating embedding for article {article_id}: {e} (index {i}). Attempting to split into chunks...")
            
            # Split text into chunks of up to 10000
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=(MODEL_MAX_CHUNKS-CHUNK_OVERLAP), chunk_overlap=CHUNK_OVERLAP)
            texts = text_splitter.split_text(content)

            # Embed the chunks
            embed_success = embedChunksAsArticle(genai, embeddings, EMBEDDING_MODEL, article, texts)

            # If the embed of chunks was successful, print to indicate
            if (embed_success):
                print(f"Successfully split into {len(texts)} chunks.")
            else:
                print(f"Error generating embedding for article {article_id}. Could not split into chunks.")
    # If the article is missing an id or content, skip it
    else:
        if article_id:
            # No content
            print(f"\nSkipping article with missing content (ID {article_id}, index {i})")
        else:
            # No ID
            print(f"\nSkipping article with no content (index {i})")
    
    # Print a progress bar (updates every {update_factor} articles)
    if i % update_factor == 0 or i == ARTICLES_LEN-1:
        # If we finished, set the percent to 100
        if (i == ARTICLES_LEN-1):
            percent = 100.0
        # Otherwise, set percent to the ratio of index of current article and length of articles
        else:
            percent = str(round((i+update_factor)*100/ARTICLES_LEN, 2))
        print(f"\r{'#'*(round((i+update_factor)/update_factor))}{' '*(round( (ARTICLES_LEN-(i+update_factor))/update_factor ))} {percent}%", end='', flush=True)

print(f"\nSuccessfully created {len(embeddings)} embeddings")
print("----FINISHED GENERATING EMBEDDINGS----")

""" 
/////////////////////////////////
//////  Upsert Data
/////////////////////////////////
"""
print("\n----UPSERTING DATA----")
# Wait for the index to be ready
while not pc.describe_index(DATABASE_INDEX_NAME).status['ready']:
    print("Waiting for index...")
    time.sleep(1)

print("Index connected.")
index = pc.Index(DATABASE_INDEX_NAME)

index.upsert(
    vectors=embeddings
)
print("Successfully upserted articles.")
print("----FINISHED UPSERTING DATA----")