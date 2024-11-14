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
    For now, implementation requires that articles is in the form [{"id": "...", "text": "..."}, {...}]
    FIX: This will change once we use wordpress' endpoint
    """
    cleaned_articles = []
    # Loop through articles
    for article in articles:
        # Clean article, append to cleaned articles
        cleaned_articles.append({"id": article["id"], "text": clean_article(article["text"])})

    return cleaned_articles
    