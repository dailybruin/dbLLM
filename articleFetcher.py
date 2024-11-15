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

    # Print & return
    print(total_pages, "pages found.")
    print(total_articles, "articles found")
    return total_pages

def fetchArticles(starting_page=1, ending_page=None):
    """
        Returns all articles (array) from the Daily Bruin article database.
        Can optionally input starting and ending pages
        Default function: get all articles
    """
    url = "https://wp.dailybruin.com/wp-json/wp/v2/posts"
    articles = []
    POSTS_PER_PAGE = 100

    # Find total pages to iterate through
    total_pages = findTotalPages(POSTS_PER_PAGE)

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
        # Request POSTS_PER_PAGE articles from a given page
        response = requests.get(url, params={"page": page, "per_page": POSTS_PER_PAGE})

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
    print("Successfully fetched all articles.")
    return articles

# Example usage
"""
    # Test that the function works
    all_articles = fetchArticles(starting_page=1)
    if (all_articles==-1):
        print("Error fetching articles.")
    else:
        print(len(all_articles), "successfully fetched")
"""
