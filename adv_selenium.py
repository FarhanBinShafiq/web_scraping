from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome with advanced features
options = webdriver.ChromeOptions()
# Comment out headless for debugging:
# options.add_argument("--headless")  # Run without GUI (disabled for now)
# Uncomment and replace with a working proxy if desired:
# options.add_argument("--proxy-server=http://192.241.169.70:8080")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Open site and add a cookie
driver.get("https://webscraper.io/test-sites/e-commerce/static/computers/laptops")
driver.add_cookie({"name": "scraper", "value": "advanced_user"})

# Debug: Print page source to check if dropdown exists
print("Page source snippet:")
print(driver.page_source[:1000])  # First 1000 characters to avoid flooding output

# Wait for and set items per page to 20 using dropdown
try:
    print("Looking for dropdown...")
    dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select#per_page"))
    )
    print("Dropdown found! Selecting '20'...")
    Select(dropdown).select_by_visible_text("20")
    print("Waiting for page to update with 20 items...")
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.thumbnail"))
    )
except Exception as e:
    print(f"Dropdown error: {type(e).__name__}: {str(e)}")
    driver.quit()
    exit()

data = []
page_num = 1

while True:
    print(f"Scraping page {page_num}...")
    laptops = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.thumbnail"))
    )
    
    for laptop in laptops:
        try:
            title = laptop.find_element(By.CSS_SELECTOR, "a.title").text
            price = laptop.find_element(By.CSS_SELECTOR, "h4.price").text
            desc = driver.execute_script(
                "return arguments[0].querySelector('.description').innerText;",
                laptop
            )
            data.append({"Title": title, "Price": price, "Description": desc})
        except Exception as e:
            print(f"Error on item: {e}")
            data.append({"Title": "Error", "Price": "N/A", "Description": "N/A"})
    
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a.page-link[rel='next']")
        driver.execute_script("arguments[0].scrollIntoView();", next_button)
        next_button.click()
        page_num += 1
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.thumbnail"))
        )
    except:
        print("No more pages!")
        break

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("laptops_advanced.csv", index=False)
print(f"Saved {len(data)} laptops!")
print("Cookies:", driver.get_cookies())

driver.quit()