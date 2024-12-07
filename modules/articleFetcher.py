import requests
from datetime import datetime

def findTotalPages(articles_per_page):
    """
    With a set number of articles per page (0-100) and a starting page (1), returns the total number of pages
    """
    # Get a response element
    response = requests.get("https://wp.dailybruin.com/wp-json/wp/v2/posts", params={"per_page": articles_per_page, "page": 1})

    # Extract total pages and total articles from the response headers
    total_pages = int(response.headers["X-WP-TotalPages"])
    total_articles = int(response.headers["x-WP-Total"])

    return total_pages

def findTotalArticles():
    """
    Returns the total number of articles
    """
    # Get a response element
    response = requests.get("https://wp.dailybruin.com/wp-json/wp/v2/posts", params={"per_page": 1, "page": 1})

    # Extract total pages and total articles from the response headers
    total_articles = int(response.headers["x-WP-Total"])

    return total_articles

def fetchArticles(starting_page=1, ending_page=None, posts_per_page=100) -> list:
    """
        Get all articles as an array from the Daily Bruin article database.

        @param starting_page: What page to start on, defualt is 1
        @param ending_page: What page to end on, default is None (changed to last available page)
        @param posts_per_page: How many posts to fetch per page from 1 to 100, default is 100
        @return: An array of articles, with each element being in JSON format
    """
    url = "https://wp.dailybruin.com/wp-json/wp/v2/posts"
    articles = []

    # Find total pages to iterate through
    total_pages = findTotalPages(posts_per_page)

    # If there was no input for ending page, make the ending page the last available page
    if ( ending_page is None ):
        ending_page = total_pages

    # Check boundaries of parameters
    if ( starting_page <= 0 ):
        print("Starting page must be greater than or equal to 1")
        return []
    elif ( ending_page <= 0 ):
        print("Ending page must be greater than or equal to 1")
        return []
    elif ( ending_page > total_pages ):
        print("Ending page must be less than or equal to total pages (", total_pages, ")")
        return []
    elif ( starting_page > ending_page ):
        print("Starting page must be less than ending page")
        return []

    # Iterate through the pages
    page = starting_page
    while (page <= ending_page):
        # Request posts_per_page articles from a given page
        response = requests.get(url, params={"page": page, "per_page": posts_per_page})

        # Only follow through if the response says successful
        if (response.status_code == 200):
            try:
                # Append all articles from this page
                articles.extend(response.json())
            except:
                # Write out error and terminate function
                print("Could not make JSON out of articles")
                return []

            print("Successfully fetched articles from page", page)
            page+=1
        # If the request was unsuccessful, write out error and terminate function
        else:
            print("Error with fetching a page")
            return []
    
    # Return the articles array
    return articles

def fetchArticlesExcept(starting_offset, ending_offset, start_except, end_except) -> list:
    url = "https://wp.dailybruin.com/wp-json/wp/v2/posts"
    articles = []

    # Find total pages to iterate through
    total_articles = findTotalArticles()

    # Check boundaries of parameters
    if ( starting_offset < 0 or ending_offset < 0 or start_except < 0 or end_except < 0):
        print("All offsets must be greater than or equal to 0")
        return []
    elif ( starting_offset >= total_articles or start_except >= total_articles or end_except >= total_articles or ending_offset >= total_articles):
        print("Offsets must be less than the total pages (", total_articles, ")")
        return []
    elif ( start_except > end_except ):
        print("Starting offset must be less than ending offset")
        return []
    elif ( start_except > end_except ):
        print("Starting offset except must be less than ending offset except")
        return []
    elif ( starting_offset > ending_offset ):
        print("Starting offset must be less than ending offset")
        return []

    # Iterate through the pages
    article = starting_offset
    while (article <= ending_offset):

        # Skip if in range of offset excepts
        if article >= start_except and article <= end_except:
            print("Skipping article", article)
            article+=1
            continue

        # Request posts_per_page articles from a given page
        response = requests.get(url, params={"per_page": 1, "offset": article})

        # Only follow through if the response says successful
        if (response.status_code == 200):
            try:
                # Append all articles from this page
                articles.extend(response.json())
            except:
                # Write out error and terminate function
                print("Could not make JSON out of article")
                return []

            print("Successfully fetched article from offset", article, "id", response.json()[0]['id'],)
            article+=1
        # If the request was unsuccessful, write out error and terminate function
        else:
            print("Error with fetching a page")
            return []
    
    # Return the articles array
    return articles

def fetchArticleById(id: str) -> str:
    """
    Fetch an uncleaned article with a corresponding id from the wordpress endpoint

    @param id: The id of the article
    @return: A string of the uncleaned article
    """

    # Get post based on id through wordpress endpoint
    url = f"https://wp.dailybruin.com/wp-json/wp/v2/posts/{id}"
    response = requests.get(url)
    
    # Only follow through if the response says successful
    if (response.status_code == 200):
        try:
            # Get the content of the article (exclude metadata)
            responseJSON = response.json()
            content = responseJSON['content']['rendered']

            return content
        except:
            # We couldn't convert the article into a JSON
            print("Error producing JSON from page corresponding with id {id}")
            return ""
    else:
        # If the request was unsuccessful, write out error and terminate function
        print(f"Error with fetching the page corresponding with id {id}")
        return ""
    
def getLatestArticlesByID(last_checked_id: str) -> list:
    """
    Gets the latest articles up to the last article id that we checked
    """
    articles = []
    page_num = 1
    id_found = False

    while True:
        one_page_articles = fetchArticles(starting_page=page_num,
                                        ending_page=page_num)
        if one_page_articles == []:
            return []
        
        for article in one_page_articles:
            if str(article['id']) == last_checked_id:
                id_found = True
                break

            articles.append(article)

        if id_found == True:
            return articles
        page_num += 1

def getLatestArticlesByDate(last_synced_date: str) -> list:
    """
    @param last_synced_date: Must be in format "yyyy-mm-dd hh:mm:ss"
    """
    # Ensure date is in correct format
    try:
        last_synced_date_obj = datetime.strptime(last_synced_date, '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(e)
        return []
    
    articles = []
    page_num = 1

    while True:
        one_page_articles = fetchArticles(starting_page=page_num,
                                        ending_page=page_num)
        if one_page_articles == []:
            return []
        
        for article in one_page_articles:
            article_date = article['date']
            article_date_obj = datetime.strptime(article_date, '%Y-%m-%dT%H:%M:%S')
            # If there's a more recent article than last synced
            if article_date_obj > last_synced_date_obj:
                articles.append(article)
            else:
                # If we found all recent articles
                return articles
        page_num += 1
