from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import time
from webdriver_manager.chrome import ChromeDriverManager

# Setup ChromeDriver automatically
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
 
driver.get("https://books.toscrape.com/")

 
data = []
 
while True:
    
    books = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")
    
    
    for book in books:
        try:
            
            title = book.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("title")
        
            price = book.find_element(By.CSS_SELECTOR, "p.price_color").text
         
            stock = book.find_element(By.CSS_SELECTOR, "p.instock").text.strip()
        except:
            
            title = "Not Found"
            price = "Not Found"
            stock = "Not Found"
        
       
        data.append({"Title": title, "Price": price, "Stock": stock})
    
    # 
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "li.next a")
        next_button.click()
        time.sleep(2)   
    except:
        print("No more pages to scrape.")
        break

#  CSV
df = pd.DataFrame(data)
df.to_csv("bookstore_books.csv", index=False)

 

# Close the browser
driver.quit()