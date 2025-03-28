import requests
from bs4 import BeautifulSoup
import pandas as pd

all_books = []

for page in range(1, 3):  # Scrape 2 pages
    url = f"http://books.toscrape.com/catalogue/page-{page}.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all books
    books = soup.find_all("article", class_="product_pod")
    
    for book in books:
        title = book.h3.a["title"]  # Book title
        price = book.find("p", class_="price_color").text  # Price
        all_books.append({"Title": title, "Price": price})

# Save to CSV
df = pd.DataFrame(all_books)
df.to_csv("books_output.csv", index=False)
print("Saved to books_output.csv!")