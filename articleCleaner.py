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