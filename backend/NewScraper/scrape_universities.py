import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
import asyncio
import json
import os

## we are scraping universities data under DAAD scholarships website 
BASE_URL = "https://www.daad.de/en/studying-in-germany/universities/all-degree-programmes/?hec-limit=100"
BASE_DOMAIN = "https://www.daad.de"

# extract all universities card from daad webpage
async def extract_all_universities_data(webpage_url: str) -> List[Dict[str, str]]:
    """
    Extracts university/programme names and their full URLs from the DAAD webpage.
    """
    # Increased timeout to 30s to handle slow DAAD responses
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(webpage_url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    target_classes = [
        "link", "link--nowrap", "u-stretched-link", "u-position-static",
        "result__link", "qa-more-link", "u-text-primary", "u-font-italic"
    ]
    
    # CSS Selector for "AND" matching: a.link.link--nowrap...
    selector = "a." + ".".join(target_classes)
    university_links = soup.select(selector)
    
    results = []
    for link in university_links:
        href = link.get('href')
        if href:
            # Prefix relative URLs with the base domain
            full_url = BASE_DOMAIN + href if href.startswith('/') else href
            
            # The name is inside the sr-only span in your example HTML
            # "More about University of Erlangen-Nuremberg..."
            sr_text = link.find('span', class_='sr-only')
            if sr_text:
                name = sr_text.get_text(strip=True).replace("More about ", "")
            else:
                name = link.get_text(strip=True)
            
            results.append({
                "name": name,
                "url": full_url
            })
    
    return results

async def main():
    filename = "universities.json"
    last_page = 224
    
    # Load existing data to resume or build upon
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                all_universities = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            all_universities = []
    else:
        all_universities = []
    
    # Use a set to track known URLs to avoid duplicates if re-running
    known_urls = {item['url'] for item in all_universities}
    print(f"Resuming with {len(all_universities)} existing records.")
    
    for i in range(1, last_page + 1):
        url = f"{BASE_URL}&hec-p={i}"
        print(f"Fetching page {i}/{last_page}...")
        
        try:
            data = await extract_all_universities_data(url)
            
            # Add only new items
            new_count = 0
            for item in data:
                if item['url'] not in known_urls:
                    all_universities.append(item)
                    known_urls.add(item['url'])
                    new_count += 1
            
            # IMPORTANT: Save progress after EACH successful page
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(all_universities, f, indent=4, ensure_ascii=False)
            
            print(f"Page {i}: Found {len(data)} links. Added {new_count} new. Total: {len(all_universities)}")
            
        except httpx.ReadTimeout:
            print(f"Timeout on page {i}. Progress saved. Moving to next page...")
            continue
        except Exception as e:
            print(f"Unexpected error on page {i}: {e}. Skipping...")
            continue
    
    print(f"\nFinished scraping. Final count: {len(all_universities)}")

if __name__ == "__main__":
    asyncio.run(main())
