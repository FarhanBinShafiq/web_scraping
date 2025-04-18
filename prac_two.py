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
driver.get("https://webscraper.io/test-sites/e-commerce/more")

# Store data
data = []

# Handle pagination
while True:
    products = driver.find_elements(By.CSS_SELECTOR, "div.thumbnail")
    for product in products:
        try:
            title = product.find_element(By.CSS_SELECTOR, "a.title").text
            price = product.find_element(By.CSS_SELECTOR, "h4.price").text
            description = product.find_element(By.CSS_SELECTOR, "p.description").text
        except:
            title = "Not Found"
            price = "Not Found"
            description = "Not Found"
        data.append({"Title": title, "Price": price, "Description": description})
    
    # Check for "Load More" button (not a traditional "Next")
    try:
        load_more = driver.find_element(By.CSS_SELECTOR, "a.btn-load-more")
        load_more.click()
        time.sleep(2)
    except:
        print("No more products to load.")
        break

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("ecommerce_paginated.csv", index=False)

print(f"Saved {len(data)} products to 'ecommerce_paginated.csv'!")

# Close the browser
driver.quit()