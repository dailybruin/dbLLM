import html
from bs4 import BeautifulSoup
import re

def clean_article(text):
    # Step 1: Remove HTML tags
    text = BeautifulSoup(text, "html.parser").get_text()
    
    # Step 2: Convert HTML character entities to unicode
    text = html.unescape(text)
    
    # Step 3: Remove any extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_all_articles(articles):
    """
    Changes articles to a cleaned state
    Implementation is specific for wordpress' returned JSON
    
    articles: array of articles, where each article is a JSON. Passed by reference
    """

    # Loop through articles
    for article in articles:
        # Clean article, append to cleaned articles
        cleaned_article = clean_article(article["content"]["rendered"])
        article["content"]["rendered"] = cleaned_article
    