from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from webdriver_manager.chrome import ChromeDriverManager

 
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

 
driver.get("http://quotes.toscrape.com/scroll")

 
data = []

 
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    quotes = driver.find_elements(By.CSS_SELECTOR, "div.quote")
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        print("Reached the end of the page.")
        break
    last_height = new_height

# Extract data from all quotes
for quote in quotes:
    text = quote.find_element(By.CSS_SELECTOR, "span.text").text
    author = quote.find_element(By.CSS_SELECTOR, "small.author").text
    tags = [tag.text for tag in quote.find_elements(By.CSS_SELECTOR, "a.tag")]
    tags_joined = ", ".join(tags)
    data.append({"Quote": text, "Author": author, "Tags": tags_joined})

#   CSV
df = pd.DataFrame(data)
df.to_csv("infinite_quotes.csv", index=False)

print(f"Saved {len(data)} quotes to 'infinite_quotes.csv'!")

 
driver.quit()