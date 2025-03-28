import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import urllib.request
import os
import time
from urllib.parse import urljoin
import cssutils  # For parsing CSS
import spacy  # For NLP-based filtering
import re

# Configuration
URL = "http://books.toscrape.com"  # Change this to any website
OUTPUT_FOLDER = "ai_scraped_images"  # Where images are saved
CHROMEDRIVER_PATH = "path/to/chromedriver"  # Replace with your ChromeDriver path
TIMEOUT = 10  # Seconds to wait for page load

# Load NLP model (small English model for text analysis)
nlp = spacy.load("en_core_web_sm")

# Create output folder
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Suppress CSS parsing warnings
cssutils.log.setLevel("CRITICAL")

# Function to fetch page content dynamically
def fetch_page(url):
    options = Options()
    options.add_argument("--headless")
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(TIMEOUT)  # Wait for full render
    
    # Scroll to load lazy-loaded images
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for scroll to load content
    
    html = driver.page_source
    driver.quit()
    return html

# Function to extract image URLs from CSS
def extract_css_images(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    css_urls = []
    
    # Find inline styles and linked stylesheets
    inline_styles = soup.select("[style]")
    for element in inline_styles:
        style = cssutils.parseStyle(element["style"])
        bg_image = style.getPropertyValue("background-image")
        if bg_image and "url(" in bg_image:
            url = re.search(r"url\(['\"]?(.*?)['\"]?\)", bg_image).group(1)
            css_urls.append(urljoin(base_url, url))

    # Find linked stylesheets
    stylesheets = soup.select("link[rel='stylesheet']")
    for sheet in stylesheets:
        css_url = urljoin(base_url, sheet["href"])
        try:
            css_content = requests.get(css_url, timeout=5).text
            sheet = cssutils.parseString(css_content)
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    bg_image = rule.style.getPropertyValue("background-image")
                    if bg_image and "url(" in bg_image:
                        url = re.search(r"url\(['\"]?(.*?)['\"]?\)", bg_image).group(1)
                        css_urls.append(urljoin(base_url, url))
        except Exception as e:
            print(f"Failed to parse CSS {css_url}: {e}")
    
    return css_urls

# Function to filter meaningful images (AI-inspired)
def is_image_meaningful(url, alt_text=""):
    # Simple heuristic: exclude tiny images or common UI elements
    exclude_patterns = [r"logo", r"icon", r"sprite", r"1x1", r"pixel", r"spacer"]
    if any(re.search(pattern, url.lower()) for pattern in exclude_patterns):
        return False
    
    # Use NLP to analyze alt text (if available)
    if alt_text:
        doc = nlp(alt_text)
        # Keep images with descriptive alt text (e.g., nouns like "photo", "picture")
        has_content = any(token.pos_ == "NOUN" for token in doc)
        return has_content
    
    # Default: assume meaningful if URL ends in image extension
    return url.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))

# Function to scrape all images
def scrape_images(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    image_urls = set()  # Avoid duplicates
    
    # 1. Standard <img> tags
    img_tags = soup.find_all("img", src=True)
    for img in img_tags:
        url = urljoin(base_url, img["src"])
        alt = img.get("alt", "")
        if is_image_meaningful(url, alt):
            image_urls.add(url)

    # 2. CSS background images
    css_images = extract_css_images(html, base_url)
    for url in css_images:
        if is_image_meaningful(url):
            image_urls.add(url)

    # 3. JavaScript-loaded images (via Selenium attributes)
    # (Already captured in rendered HTML from fetch_page)

    # Download images
    image_count = 0
    for i, img_url in enumerate(image_urls, 1):
        file_extension = img_url.split(".")[-1].split("?")[0]
        if len(file_extension) > 4 or not file_extension:
            file_extension = "jpg"
        filename = os.path.join(OUTPUT_FOLDER, f"image_{i}.{file_extension}")
        
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            urllib.request.urlretrieve(img_url, filename, reporthook=None, data=None)
            print(f"Downloaded: {filename} from {img_url}")
            image_count += 1
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")
    
    return image_count

# Main execution
def main():
    print(f"Scraping images from {URL} with AI-enhanced logic...")
    html = fetch_page(URL)
    if not html:
        print("Failed to fetch the page. Exiting.")
        return

    image_count = scrape_images(html, URL)
    if image_count > 0:
        print(f"Successfully downloaded {image_count} images to '{OUTPUT_FOLDER}'!")
    else:
        print("No images found or downloaded.")

if __name__ == "__main__":
    main()