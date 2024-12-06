"""
Gets the latest articles that haven't been stored yet (uses last synced time)
"""

import os
from datetime import datetime
from modules.articleFetcher import getLatestArticlesByDate

# Check if lastSynced.txt exists, create it if it doesn't
if not os.path.isfile('./lastSynced.txt'):
    file = open('./lastSynced.txt', 'w')
    file.close()

# Extract our lastSynced time
file = open('./lastSynced.txt', 'r')
last_synced_time = file.read()
file.close()

# Update lastSynced with current time
file = open('./lastSynced.txt', 'w')

curr_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
file.write( curr_time )

file.close()

# Fetch new articles
articles = getLatestArticlesByDate(last_synced_date = last_synced_time)

print(f"{len(articles)} new articles")

