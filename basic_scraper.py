import requests
from bs4 import BeautifulSoup

# URL to scrape
url = "http://quotes.toscrape.com"

# Fetch the webpage
response = requests.get(url)

# Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# Find all quotes
quotes = soup.find_all("span", class_="text")

# Print each quote
for i, quote in enumerate(quotes, 1):
    print(f"Quote {i}: {quote.text}")