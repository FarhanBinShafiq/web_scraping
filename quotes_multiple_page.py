import requests
from bs4 import BeautifulSoup
import pandas as pd

file_name = "all_quotes.csv"
base_url = "http://quotes.toscrape.com/page/{}/"

data = []  # This will store all rows of scraped data

# Loop through page numbers (start from 1)
for page_num in range(1, 100):  # 100 is just a large upper limit
    print(f"Scraping page {page_num}...")

    url = base_url.format(page_num)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    quotes = soup.find_all("div", class_="quote")

    # If there are no quotes, we've reached the last page
    if not quotes:
        print("No more quotes found. Stopping.")
        break

    # Loop through each quote block on the current page
    for quote in quotes:
        text_element = quote.find("span", class_="text")
        author_element = quote.find("small", class_="author")
        tag_elements = quote.find_all("a", class_="tag")

        # Get quote text and author name
        text = text_element.text
        author = author_element.text

        # Extract all tag names
        tags = []
        for tag in tag_elements:
            tags.append(tag.text)

        tags_joined = ", ".join(tags)

        # Add to data list
        row = {"Quote": text, "Author": author, "Tags": tags_joined}
        data.append(row)

# Save all collected data to CSV
df = pd.DataFrame(data)
df.to_csv(file_name, index=False)

print(f"\nAll quotes saved to '{file_name}' successfully!")
