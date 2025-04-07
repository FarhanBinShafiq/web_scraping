from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import time
from webdriver_manager.chrome import ChromeDriverManager

# Setup ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open the paginated e-commerce test site
driver.get("https://books.toscrape.com/")

# Store data
data = []

# Handle pagination
while True:
    products = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")
    for product in products:
        try:
            book_title = product.find_element(By.CSS_SELECTOR, "h3 a").get_attribute('title')
            price = product.find_element(By.CSS_SELECTOR, "p.product_color").text
            
        except:
            book_title = "Not Found"
            price = "Not Found"
           
        data.append({"Title":book_title, "Price": price})
    
    # Check for "Load More" button (not a traditional "Next")
    try:
        load_more = driver.find_element(By.CSS_SELECTOR, "li.next a")
        load_more.click()
        time.sleep(2)
    except:
        print("No more products to load.")
        break

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("aginated.csv", index=False)

print(f"Saved {len(data)} products to 'ecommerce_paginated.csv'!")

# Close the browser
driver.quit()