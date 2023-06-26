import requests
from bs4 import BeautifulSoup
import re

# Replace 'your_search_query' with your desired search query
search_query = 'your_search_query'
url = f"https://www.google.com/search?q={search_query}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the search result containers
search_results = soup.find_all('div', class_=re.compile('^tF2Cxc'))

for result in search_results:
    # Extract the title
    title = result.find('div', class_=re.compile('^zBAuLc')).text

    # Extract the URL
    link = result.find('a')['href']

    # Extract the description (snippet)
    description = result.find('div', class_=re.compile('^s3v9rd')).text

    print(f"Title: {title}")
    print(f"URL: {link}")
    print(f"Description: {description}\n")