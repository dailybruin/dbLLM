"""
Gets the latest articles that haven't been stored yet (uses last synced time)
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv

from pinecone.grpc import PineconeGRPC as Pinecone
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter

from modules.articleCleaner import clean_all_articles
from modules.articleFetcher import fetchArticles
from modules.articleFetcher import getLatestArticlesByDate
from modules.embeddingFuncs import embedArticle
from modules.embeddingFuncs import embedChunksAsArticle

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
DATABASE_INDEX_NAME = str(input("Enter database index name: "))
EMBEDDING_MODEL = "models/text-embedding-004"
MODEL_MAX_CHUNKS = 9500
CHUNK_OVERLAP = 200

if DATABASE_INDEX_NAME not in pc.list_indexes().names():
    print("Invalid index name. Exiting.")
    exit()

print("----FINISHED LOADING ENVIRONMENT VARIABLES----")

# Check if lastSynced.txt exists, create it if it doesn't
if not os.path.isfile('./lastSynced.txt'):
    print("No './lastSynced.txt' file found - creating one and exiting. Please input a time in the format %Y-%m-%d %H:%M:%S and try again.")
    file = open('./lastSynced.txt', 'w')
    file.close()
    exit()

# Extract our lastSynced time
file = open('./lastSynced.txt', 'r')
last_synced_time = file.read()
file.close()

# Check if lastSynced time exists
if last_synced_time == "":
    print("No lastSynced time found in './lastSynced.txt'. Exiting. Please input a time in the format %Y-%m-%d %H:%M:%S and try again.")
    exit()

# Check if lastSynced time is in correct format
try:
    last_synced_date_obj = datetime.strptime(last_synced_time, '%Y-%m-%d %H:%M:%S')
except Exception as e:
    print(e)
    print("Last synced time is not in correct format. Exiting.")
    exit()

# Update lastSynced with current time
file = open('./lastSynced.txt', 'w')

curr_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
file.write( curr_time )

file.close()

""" 
/////////////////////////////////
//////  Fetch and Clean Articles
/////////////////////////////////
"""
print("Fetching new articles...")
articles = getLatestArticlesByDate(last_synced_date = last_synced_time)

if len(articles) <= 0:
    print("No new articles. Exiting.")
    exit()

print(f"{len(articles)} new articles successfully fetched")

# Clean articles

clean_all_articles(articles)


""" 
/////////////////////////////////
//////  Embed Articles
/////////////////////////////////
"""
# Generate embeddings
embeddings = []
ARTICLES_LEN = len(articles)
update_factor = max(1, ARTICLES_LEN // 50)

print(f"Generating embeddings for {ARTICLES_LEN} articles")

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
            # Split text into chunks of up to 10000
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=(MODEL_MAX_CHUNKS-CHUNK_OVERLAP), chunk_overlap=CHUNK_OVERLAP)
            texts = text_splitter.split_text(content)

            # Embed the chunks
            embed_success = embedChunksAsArticle(genai, embeddings, EMBEDDING_MODEL, article, texts)

            if not embed_success:
                print(f"Error generating embedding for article {article_id}. Could not split into chunks.\n")

    # If the article is missing an id or content, skip it
    else:
        if article_id:
            # No content
            print(f"\nSkipping article with missing content (ID {article_id}, index {i})\n")

        else:
            print(f"\nSkipping article with no ID (index {i})\n")
    
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

""" 
/////////////////////////////////
//////  Upsert Data
/////////////////////////////////
"""

# Wait for the index to be ready
while not pc.describe_index(DATABASE_INDEX_NAME).status['ready']:
    print("Waiting for index...")
    time.sleep(1)

print("Index connected.")
index = pc.Index(DATABASE_INDEX_NAME)

index.upsert(
    vectors=embeddings
)
print("---------------------------------------------------------")
print(f"\nSuccessfully upserted {len(embeddings)} embeddings.\n")
print("---------------------------------------------------------")

