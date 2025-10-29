from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import logging
import datetime
import pandas as pd
import numpy as np
import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

today = datetime.date.today().isoformat()

# Create logs directory if it doesn't exist
os.makedirs('./logs', exist_ok=True)

logging.basicConfig(filename='./logs/log_'+str(today) +'.txt', level=logging.DEBUG)

base_url = "https://www2.daad.de/deutschland/studienangebote/international-programmes/en/result/?cert=&admReq=&langExamPC=&langExamLC=&langExamSC=&degree%5B%5D=3&fos%5B%5D=&langDeAvailable=&langEnAvailable=&lang%5B%5D=&modStd%5B%5D=&cit%5B%5D=&tyi%5B%5D=&ins%5B%5D=&fee=&bgn%5B%5D=&dat%5B%5D=&prep_subj%5B%5D=&prep_degree%5B%5D=&sort=4&dur=&q=&limit=100&offset=100&display=list&lvlEn%5B%5D=&subjectGroup%5B%5D=&subjects%5B%5D="
# Configure Chrome options
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)
    print("✓ Chrome driver initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize Chrome driver: {e}")
    logging.critical(f"Driver initialization failed: {e}", exc_info=True)
    exit(1)

params = ["course", "institution", "url", "admission req",
          "language req", "deadline"]
cols = ["course", "institution", "url", "admission req",
        "language req", "deadline"]

final_data = []


def build_url_with_offset(offset):
    """Build URL with specific offset value"""
    parsed = urlparse(base_url)
    query_params = parse_qs(parsed.query)
    
    # Update offset parameter
    query_params['offset'] = [str(offset)]
    
    # Rebuild query string
    new_query = urlencode(query_params, doseq=True)
    
    # Rebuild URL
    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    
    return new_url


def accept_cookies():
    try:
        wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "button.qa-cookie-consent-accept-selected"))).click()
        print("✓ Cookies accepted")
        time.sleep(2)
    except Exception as e:
        print(f"No cookie banner found or already accepted")


def get_links_from_current_page():
    """Get all course links from the current page"""
    try:
        time.sleep(3)  # Wait for page to load
        links = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".list-inline-item.mr-0.js-course-detail-link")))
        return [link.get_attribute("href") for link in links]
    except Exception as e:
        print(f"Error getting links from page: {e}")
        logging.error(f"Error getting links: {e}", exc_info=True)
        return []


def check_if_page_has_results():
    """Check if the current page has any results"""
    try:
        # Look for the "no results" message or check if links exist
        links = driver.find_elements(By.CSS_SELECTOR, ".list-inline-item.mr-0.js-course-detail-link")
        return len(links) > 0
    except Exception as e:
        return False


def textcombiner(targetIndex):
    all_text = []
    try:
        reqs = wait.until(EC.presence_of_all_elements_located((
            By.CSS_SELECTOR, "#registration > .container > .c-description-list > *:nth-child("+targetIndex+") > *")))
        for p in reqs:
            all_text.append(p.get_attribute('innerText'))
        return "\n".join(all_text)
    except Exception as e:
        return "N/A"


def paramData(param, item_link):
    try:
        if param == "course":
            return wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "h2.c-detail-header__title > span:nth-child(1)"))).get_attribute('innerText')
        if param == "institution":
            return wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "h3.c-detail-header__subtitle"))).get_attribute('innerHTML').splitlines()[1].strip()
        if param == "url":
            return item_link
        if param == 'admission req':
            return textcombiner("2")
        if param == 'language req':
            return textcombiner("4")
        if param == 'deadline':
            return textcombiner("6")
    except Exception as e:
        print(f'Error extracting {param}: {e}')
        logging.error(f"Error extracting {param} from {item_link}: {e}", exc_info=True)
        return "N/A"


def scrape_course(item_link, index, total):
    """Scrape a single course page"""
    try:
        print(f"  [{index}/{total}] Visiting: {item_link}")
        driver.get(item_link)
        time.sleep(2)

        dataFromURL = []
        for param in params:
            dataFromURL.append(paramData(param, item_link))

        print(f"    ✓ Extracted: {dataFromURL[0]}")
        return dataFromURL
        
    except Exception as e:
        print(f'    ✗ Error processing link: {e}')
        logging.critical(e, exc_info=True)
        return None


def scrape_page(page_number, offset):
    """Scrape all courses from a single page"""
    print(f"\n{'='*60}")
    print(f"SCRAPING PAGE {page_number} (offset={offset})")
    print(f"{'='*60}")
    
    # Build URL with offset
    page_url = build_url_with_offset(offset)
    print(f"  URL: {page_url}")
    
    # Navigate to the page
    driver.get(page_url)
    time.sleep(3)
    
    # Check if page has results
    if not check_if_page_has_results():
        print(f"  ✗ No results found on this page")
        return 0, False  # Return 0 courses and False to indicate no more pages
    
    # Get all links from current page
    links = get_links_from_current_page()
    
    if not links:
        print(f"  ✗ No links found on page {page_number}")
        return 0, False
    
    print(f"  ✓ Found {len(links)} courses on page {page_number}")
    
    # Scrape each course on this page
    courses_scraped = 0
    for i, link in enumerate(links, 1):
        result = scrape_course(link, i, len(links))
        if result:
            final_data.append(result)
            courses_scraped += 1
        time.sleep(2)  # Delay between courses
        
        # Go back to listing page
        driver.get(page_url)
        time.sleep(2)
    
    print(f"\n  ✓ Completed page {page_number}: {courses_scraped}/{len(links)} courses scraped")
    print(f"  Total courses so far: {len(final_data)}")
    
    # Return True if we got results (there might be more pages)
    return courses_scraped, True


def exportCSV():
    os.makedirs('./PHD', exist_ok=True)
    filename = "PHD Informatik Course List for Summer 2023 - Tuition Free"
    df2 = pd.DataFrame(np.array(final_data), columns=cols)
    print("\n" + "="*60)
    print("PREVIEW OF SCRAPED DATA:")
    print("="*60)
    print(df2.head(10))
    print("="*60)
    df2.to_csv("./PHD/"+filename+".csv", encoding='utf-8-sig', index=False)
    print(f"\n✓ Saved {len(final_data)} courses to ./PHD/{filename}.csv")


def main():
    try:
        print("\n" + "="*60)
        print("DAAD COURSE SCRAPER - URL-BASED PAGINATION")
        print("="*60)
        print(f"Base URL: {base_url}\n")
        
        # Load initial page and accept cookies
        driver.get(base_url)
        print("✓ Initial page loaded")
        time.sleep(3)
        accept_cookies()
        
        # Scrape page by page using offset
        page_number = 1
        offset = 0
        limit = 100  # Results per page
        
        while True:
            # Scrape current page
            courses_on_page, has_results = scrape_page(page_number, offset)
            
            # If no results found, stop
            if not has_results or courses_on_page == 0:
                print(f"\n✓ No more results available. Completed scraping.")
                break
            
            # Move to next page
            page_number += 1
            offset += limit
            print(f"\n➜ Moving to page {page_number}...")
            time.sleep(3)
        
        # Export results
        if final_data:
            exportCSV()
        else:
            print("\n✗ No data was scraped")
            
    except Exception as e:
        print(f"\n✗ Critical error in main: {e}")
        logging.critical(e, exc_info=True)
    finally:
        print(f'\n{"="*60}')
        print(f"SCRAPING COMPLETED")
        print(f"Total pages scraped: {page_number}")
        print(f"Total courses scraped: {len(final_data)}")
        print("="*60)
        driver.quit()


if __name__ == "__main__":
    main()