import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
import os

# Configuration
URL = "http://quotes.toscrape.com"  # Change this to any URL
OUTPUT_FILE = "scraped_data.json"
CHROMEDRIVER_PATH = "path/to/chromedriver"  # Replace with your ChromeDriver path
USE_SELENIUM = False  # Set to True for dynamic sites

# Function to fetch page content
def fetch_page(url, use_selenium=False):
    if use_selenium:
        options = Options()
        options.add_argument("--headless")  # Run without opening browser
        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        time.sleep(3)  # Wait for dynamic content
        html = driver.page_source
        driver.quit()
        return html
    else:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

# Function to smartly extract content
def scrape_everything(html):
    if not html:
        return None
    
    soup = BeautifulSoup(html, "html.parser")
    data = {
        "headings": [],
        "paragraphs": [],
        "links": [],
        "images": [],
        "tables": []
    }

    # Extract headings (h1-h6)
    for level in range(1, 7):
        headings = soup.find_all(f"h{level}")
        for h in headings:
            data["headings"].append({"level": f"h{level}", "text": h.get_text(strip=True)})

    # Extract paragraphs
    paragraphs = soup.find_all("p")
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > 20:  # Filter short, irrelevant text (e.g., nav links)
            data["paragraphs"].append(text)

    # Extract links
    links = soup.find_all("a", href=True)
    for link in links:
        data["links"].append({"text": link.get_text(strip=True), "url": link["href"]})

    # Extract images
    images = soup.find_all("img", src=True)
    for img in images:
        data["images"].append({"alt": img.get("alt", ""), "src": img["src"]})

    # Extract tables
    tables = soup.find_all("table")
    for table in tables:
        rows = []
        for tr in table.find_all("tr"):
            row = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if row:
                rows.append(row)
        if rows:
            data["tables"].append(rows)

    return data

# Main execution
def main():
    # Fetch the page
    html = fetch_page(URL, use_selenium=USE_SELENIUM)
    if not html:
        print("Failed to fetch the page. Exiting.")
        return

    # Scrape everything
    scraped_data = scrape_everything(html)
    if not scraped_data:
        print("No data scraped.")
        return

    # Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=4, ensure_ascii=False)
    print(f"Data saved to {OUTPUT_FILE}")

    # Optional: Save tables to CSV if they exist
    if scraped_data["tables"]:
        for i, table in enumerate(scraped_data["tables"], 1):
            df = pd.DataFrame(table)
            csv_file = f"table_{i}.csv"
            df.to_csv(csv_file, index=False)
            print(f"Table {i} saved to {csv_file}")

if __name__ == "__main__":
    main()