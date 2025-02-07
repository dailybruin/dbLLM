import requests
from datetime import datetime

def findTotalPages(articles_per_page):
    """
    Get the total number of pages for the given articles per page.

    Args:
    - articles_per_page (int): Number of articles per page (1-100).

    Returns:
    - int: Total number of pages.
    """
    response = requests.get("https://wp.dailybruin.com/wp-json/wp/v2/posts", params={"per_page": articles_per_page, "page": 1})
    total_pages = int(response.headers["X-WP-TotalPages"])
    return total_pages

def findTotalArticles():
    """
    Get the total number of articles.

    Returns:
    - int: Total number of articles.
    """
    response = requests.get("https://wp.dailybruin.com/wp-json/wp/v2/posts", params={"per_page": 1, "page": 1})
    total_articles = int(response.headers["x-WP-Total"])
    return total_articles

def fetchArticles(starting_page=1, ending_page=None, posts_per_page=100):
    """
    Fetch articles from the Daily Bruin article database.

    Args:
    - starting_page (int): The page to start from (default is 1).
    - ending_page (int): The page to end on (default is None, which means the last available page).
    - posts_per_page (int): Number of posts per page (1-100, default is 100).

    Returns:
    - list: List of articles in JSON format.
    """
    url = "https://wp.dailybruin.com/wp-json/wp/v2/posts"
    articles = []
    total_pages = findTotalPages(posts_per_page)

    if ending_page is None:
        ending_page = total_pages

    if starting_page <= 0 or ending_page <= 0 or ending_page > total_pages or starting_page > ending_page:
        print("Invalid page range.")
        return []

    for page in range(starting_page, ending_page + 1):
        response = requests.get(url, params={"page": page, "per_page": posts_per_page})

        if response.status_code == 200:
            try:
                articles.extend(response.json())
                print(f"Fetched articles from page {page}")
            except:
                print("Error parsing JSON from articles.")
                return []
        else:
            print(f"Error fetching page {page}.")
            return []

    return articles

def fetchArticlesExcept(starting_offset, ending_offset, start_except, end_except):
    """
    Fetch articles while excluding a specific range of articles.

    Args:
    - starting_offset (int): The starting offset.
    - ending_offset (int): The ending offset.
    - start_except (int): The starting offset to exclude.
    - end_except (int): The ending offset to exclude.

    Returns:
    - list: List of articles in JSON format.
    """
    url = "https://wp.dailybruin.com/wp-json/wp/v2/posts"
    articles = []
    total_articles = findTotalArticles()

    if starting_offset < 0 or ending_offset < 0 or start_except < 0 or end_except < 0:
        print("Offsets must be greater than or equal to 0.")
        return []
    
    if starting_offset >= total_articles or ending_offset >= total_articles or start_except >= total_articles or end_except >= total_articles:
        print(f"Offsets must be less than the total articles ({total_articles}).")
        return []

    for article in range(starting_offset, ending_offset + 1):
        if start_except <= article <= end_except:
            print(f"Skipping article {article}.")
            continue

        response = requests.get(url, params={"per_page": 1, "offset": article})

        if response.status_code == 200:
            try:
                articles.extend(response.json())
                print(f"Fetched article {article}, ID: {response.json()[0]['id']}.")
            except:
                print("Error parsing article.")
                return []
        else:
            print(f"Error fetching article {article}.")
            return []

    return articles

def fetchArticleById(id: str):
    """
    Fetch an article by its ID.

    Args:
    - id (str): The ID of the article.

    Returns:
    - str: The content of the article.
    """
    url = f"https://wp.dailybruin.com/wp-json/wp/v2/posts/{id}"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            return response.json()['content']['rendered']
        except:
            print(f"Error parsing article with ID {id}.")
            return ""
    else:
        print(f"Error fetching article with ID {id}.")
        return ""

def getLatestArticlesByID(last_checked_id: str):
    """
    Fetch the latest articles until the last checked article ID.

    Args:
    - last_checked_id (str): The ID of the last checked article.

    Returns:
    - list: List of articles in JSON format.
    """
    articles = []
    page_num = 1

    while True:
        page_articles = fetchArticles(starting_page=page_num, ending_page=page_num)
        if not page_articles:
            return []

        for article in page_articles:
            if str(article['id']) == last_checked_id:
                return articles
            articles.append(article)

        page_num += 1

def getLatestArticlesByDate(last_synced_date: str):
    """
    Fetch the latest articles by date after the given date.

    Args:
    - last_synced_date (str): The date in "yyyy-mm-dd hh:mm:ss" format.

    Returns:
    - list: List of articles in JSON format.
    """
    try:
        last_synced_date_obj = datetime.strptime(last_synced_date, '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(e)
        return []

    articles = []
    page_num = 1

    while True:
        page_articles = fetchArticles(starting_page=page_num, ending_page=page_num)
        if not page_articles:
            return []

        for article in page_articles:
            article_date_obj = datetime.strptime(article['date'], '%Y-%m-%dT%H:%M:%S')
            if article_date_obj > last_synced_date_obj:
                articles.append(article)
            else:
                return articles
        page_num += 1
