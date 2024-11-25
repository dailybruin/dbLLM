import requests

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

def fetchArticles(starting_page=1, ending_page=None, posts_per_page=100):
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
        print(f"Error with fetching the page corresopnding with id {id}")
        return ""
