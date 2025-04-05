import requests
from bs4 import BeautifulSoup
import pandas as pd

file_name = "all_quotes.csv"
base_url = "http://quotes.toscrape.com/page/{}/"

# Main list to store all quote info
data = []

# Loop through pages
for page_num in range(1, 100):
    print(f"Scraping page {page_num}...")

    url = base_url.format(page_num)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    quotes = soup.find_all("div", class_="quote")

    if not quotes:
        print("No more quotes found. Stopping.")
        break

    for quote in quotes:
        text = quote.find("span", class_="text").text
        author = quote.find("small", class_="author").text

        # Get tags
        tags = []
        tag_elements = quote.find_all("a", class_="tag")
        for tag in tag_elements:
            tags.append(tag.text)
        tags_joined = ", ".join(tags)


        ##Author Details
        
        author_info=quote.find("a")["href"]
        author_url=f"http://quotes.toscrape.com{author_info}"
        author_res=requests.get(author_url)
        author_soup = BeautifulSoup(author_res.text, "html.parser")
     

        author_details=soup.find("div", class_="author-details")
        birth_date = author_soup.find("span", class_="author-born-date").text
        birth_place = author_soup.find("span", class_="author-born-location").text




        # Add all to data
        row = {
            "Quote": text,
            "Author": author,
            "Tags": tags_joined,
            "Birth Date": birth_date,
            "Birth Place": birth_place
        }
        data.append(row)

# Save to CSV
df = pd.DataFrame(data)
df.to_csv(file_name, index=False)

print(f"\nAll quotes with author info saved to '{file_name}' successfully!")
