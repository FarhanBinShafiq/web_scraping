import requests
from bs4 import BeautifulSoup
import pandas as pd

 
file_name = "my_quotes_multiple_page.csv"

 
url = "http://quotes.toscrape.com"
response = requests.get(url)

 
soup = BeautifulSoup(response.text, "html.parser")

 
quotes = soup.find_all("div", class_="quote")

 
data = []

 
for quote in quotes:
 
    text_element = quote.find("span", class_="text")
    text = text_element.text
    
 
    author_element = quote.find("small", class_="author")
    author = author_element.text
 
    tag_elements = quote.find_all("a", class_="tag")   
    tags = []  
 
    for tag in tag_elements:
        tags.append(tag.text)

 
    tags_joined = ", ".join(tags)
 
    row = {"Quote": text, "Author": author, "Tags": tags_joined}
    data.append(row)

 
df = pd.DataFrame(data)
df.to_csv(file_name, index=False)

 
print(f"Quotes saved to '{file_name}' successfully!")
