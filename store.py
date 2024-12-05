import os
import time
from dotenv import load_dotenv

from pinecone.grpc import PineconeGRPC as Pinecone
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter

from modules.articleCleaner import clean_all_articles
from modules.articleFetcher import fetchArticles
from modules.embeddingFuncs import embedArticle
from modules.embeddingFuncs import embedChunksAsArticle
from modules.Logger import Logger

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

if DATABASE_INDEX_NAME not in pc.list_indexes().names():
    print("Invalid index name. Exiting.")
    exit()

DISPLAY_SKIPPED_ARTICLES = str(input("Would you like to display info about skipped or chunked articles (y/n)? "))
if DISPLAY_SKIPPED_ARTICLES != "y" and DISPLAY_SKIPPED_ARTICLES != "n":
    DISPLAY_SKIPPED_ARTICLES = "y"

LOG_SKIPPED_ARTICLES = str(input("Would you like to log skipped articles in a new log file (y/n)? "))
if LOG_SKIPPED_ARTICLES != "y" and LOG_SKIPPED_ARTICLES != "n":
    LOG_SKIPPED_ARTICLES = "y"

print("----FINISHED LOADING ENVIRONMENT VARIABLES----")


print("\n----FETCHING ARTICLES----")

# Fetch articles
try:
    STARTING_PAGE = int(input("Enter starting page (hit enter for default of 1): "))
except:
    STARTING_PAGE = 1
try:
    ENDING_PAGE = int(input("Enter ending page (hit enter for default of 10): "))
except:
    ENDING_PAGE = 10

# Store articles in segments (incase of runtime failure)
EVERY_N = 5

logger = Logger(storage_path="./logs",
                    index_name=DATABASE_INDEX_NAME,
                    logging_enabled=LOG_SKIPPED_ARTICLES,
                    display_skipped_articles=DISPLAY_SKIPPED_ARTICLES,
                    starting_page=STARTING_PAGE,
                    ending_page=ENDING_PAGE)

# If we decide to log skipped articles
if (LOG_SKIPPED_ARTICLES == "y"):
    if logger.create_log_file() == False:
        print("Invalid parent directory for logging. Exiting.")
        exit()

logger.start_fetching_articles_section()
# Loop through every n articles
curr_page = STARTING_PAGE
while (curr_page <= ENDING_PAGE):
    # Calculate how many pages to search (either 5, or if we're near the end, less than 5)
    page_range = min(4, ENDING_PAGE-curr_page)
    end_segment = curr_page + page_range
    print(f"Getting pages {curr_page}-{end_segment}")
    
    """ 
    /////////////////////////////////
    //////  Fetch and Clean Articles
    /////////////////////////////////
    """
    articles = fetchArticles(starting_page=curr_page, ending_page=end_segment)

    if (articles):
        # Clean articles
        print(len(articles), "articles successfully fetched")
        logger.log_successful_article_fetch(curr_page, end_segment)

        clean_all_articles(articles)

        # Store ID of first (most recent) article found
        if (curr_page == STARTING_PAGE):
            logger.store_latest_id(str(articles[0]['id']))
    else:
        print("Error fetching articles.")
        logger.log_failed_article_fetch(curr_page, end_segment)
        logger.end_log(f"FATAL ERROR: COULD NOT FETCH ARTICLES {curr_page}-{end_segment}")
        exit()

    """ 
    /////////////////////////////////
    //////  Embed Articles
    /////////////////////////////////
    """
    # Generate embeddings
    embeddings = []
    ARTICLES_LEN = len(articles)
    # Dynamic step calculation
    update_factor = max(1, len(articles) // 100)

    print(f"Generating embeddings for {ARTICLES_LEN} articles")
    logger.start_embedding_section(start_page=curr_page,
                                   end_page=end_segment)

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
                if DISPLAY_SKIPPED_ARTICLES=="y":
                    print(f"\nError generating embedding for article {article_id}: {e} (index {i}). Attempting to split into chunks...")
                
                # Split text into chunks of up to 10000
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=(MODEL_MAX_CHUNKS-CHUNK_OVERLAP), chunk_overlap=CHUNK_OVERLAP)
                texts = text_splitter.split_text(content)

                # Embed the chunks
                embed_success = embedChunksAsArticle(genai, embeddings, EMBEDDING_MODEL, article, texts)

                # If the embed of chunks was successful, print to indicate
                if (embed_success):
                    if DISPLAY_SKIPPED_ARTICLES=="y":
                        print(f"Successfully split into {len(texts)} chunks.\n")
                else:
                    if DISPLAY_SKIPPED_ARTICLES=="y":
                        print(f"Error generating embedding for article {article_id}. Could not split into chunks.\n")

                    # Log skipped article
                    if LOG_SKIPPED_ARTICLES=="y":
                        logger.log_chunking_error(article_id=article_id)

        # If the article is missing an id or content, skip it
        else:
            if article_id:
                # No content
                if DISPLAY_SKIPPED_ARTICLES=="y":
                    print(f"\nSkipping article with missing content (ID {article_id}, index {i})\n")

                # Log skipped article
                if LOG_SKIPPED_ARTICLES=="y":
                    logger.log_missing_content(article_id=article_id)

            else:
                # No ID
                if DISPLAY_SKIPPED_ARTICLES=="y":
                    print(f"\nSkipping article with no ID (index {i})\n")

                # Log skipped article
                if LOG_SKIPPED_ARTICLES=="y":
                        logger.log_missing_id()

        
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

    logger.start_upserting_section(start_page=curr_page,
                                   end_page=end_segment)
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
    logger.log_successful_upsert(len(embeddings))

    curr_page = end_segment + 1

logger.end_log()