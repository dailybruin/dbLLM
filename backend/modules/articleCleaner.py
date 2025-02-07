import html
from bs4 import BeautifulSoup
import re

def clean_article(text):
    """
    Clean an individual article's text content.

    Steps:
    1. Remove HTML tags.
    2. Convert HTML character entities to Unicode.
    3. Remove extra whitespace.

    Args:
    - text (str): The raw HTML content of the article.

    Returns:
    - str: The cleaned text.
    """
    # Step 1: Remove HTML tags using BeautifulSoup
    text = BeautifulSoup(text, "html.parser").get_text()
    
    # Step 2: Convert HTML character entities to unicode using html.unescape
    text = html.unescape(text)
    
    # Step 3: Remove any extra whitespace and trim the text
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_all_articles(articles):
    """
    Clean all articles in the provided list by modifying their content.

    This function is specifically designed for cleaning articles returned
    in a JSON format by WordPress.

    Args:
    - articles (list): A list of article dictionaries, where each article
                        contains a "content" key with a "rendered" HTML string.

    Modifies:
    - Updates the "content.rendered" field of each article in the articles list.
    """
    # Loop through each article in the articles list
    for article in articles:
        # Clean the article content and update it in the original article object
        cleaned_article = clean_article(article["content"]["rendered"])
        article["content"]["rendered"] = cleaned_article
