import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import asyncio
import json
import os
from datetime import datetime

# Configuration
INPUT_FILE = "universities.json"
OUTPUT_FILE = "programs_detailed.json"
FAILED_FILE = "failed_urls.json"
CONCURRENT_LIMIT = 100  # Number of concurrent requests per batch
DELAY_BETWEEN_REQUESTS = 1.0  # Seconds between batches
REQUEST_TIMEOUT = 30.0
BASE_DOMAIN = "https://www.daad.de"

async def extract_program_info(client: httpx.AsyncClient, url: str) -> dict:
    """Extract program information from a DAAD program detail page."""
    response = await client.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    result = {
        'name': None,
        'link': url,
        'description': None,
        'degree': None,
        'program': None,
        'standard_period_of_study': None,
        'location': None,
        'deadlines': [],
        'deadline_moreinfo_link': None,
        'study_type': None,
        'admission_semester': None,
        'area_of_study': [],
        'annotation': None,
        'admission_modus': None,
        'application_deadlines': [],
        'tuition_fees_link': None,
        'tuition_fees_info': None,
        'languages_of_instruction': {},
        'lecture_period': [],
        'university_name': None,
        'university_website': None,
        'contacts': {},
        'scraped_at': datetime.now().isoformat()
    }

    # Extract name and description from header
    h2 = soup.find('h2', class_='u-divider')
    if h2:
        name_span = h2.find('span', class_=lambda x: x and 'u-text-primary' in x)
        if name_span:
            result['name'] = name_span.get_text(strip=True)
        desc_span = h2.find_all('span')
        if len(desc_span) > 1:
            result['description'] = desc_span[1].get_text(strip=True)

    # Extract keyfacts
    keyfacts = soup.find_all('div', class_='keyfact__item')
    for kf in keyfacts:
        dt = kf.find('dt')
        dds = kf.find_all('dd')
        if dt:
            label = dt.get_text(strip=True).lower()
            values = [dd.get_text(strip=True) for dd in dds]
            if 'degree' in label:
                result['degree'] = values[0] if values else None
                result['program'] = values[1] if len(values) > 1 else values[0] if values else None
            elif 'period of study' in label:
                result['standard_period_of_study'] = values[0] if values else None
            elif 'location' in label:
                result['location'] = values[0] if values else None
            elif 'deadline' in label:
                result['deadlines'] = [v for v in values if 'enquire' not in v.lower()]
                for dd in dds:
                    link = dd.find('a')
                    if link and link.get('href'):
                        href = link.get('href')
                        result['deadline_moreinfo_link'] = BASE_DOMAIN + href if href.startswith('/') else href

    # Overview section
    overview_section = soup.find('div', id='hsk-detail-overview')
    if overview_section:
        result.update(_extract_section_content(overview_section))

    # Application Deadlines section
    deadlines_section = soup.find('div', id='hsk-detail-deadlines')
    if deadlines_section:
        result['application_deadlines'] = _extract_deadlines(deadlines_section)

    # Tuition Fees section
    fees_section = soup.find('div', id='hsk-detail-fees')
    if fees_section:
        fee_link = fees_section.find('a', href=True)
        if fee_link:
            result['tuition_fees_link'] = fee_link.get('href')
        fee_info = fees_section.find('p', class_=lambda x: x and 'js-dynamic-content' in x)
        if fee_info:
            result['tuition_fees_info'] = fee_info.get_text(strip=True)

    # Languages section
    lang_section = soup.find('div', id='hsk-detail-languages')
    if lang_section:
        result['languages_of_instruction'] = _extract_languages(lang_section)

    # Sidebar / University info
    sidebar = soup.find('aside')
    if sidebar:
        result.update(_extract_sidebar_info(sidebar))

    return result

def _extract_section_content(section) -> dict:
    data = {
        'study_type': None,
        'admission_semester': None,
        'area_of_study': [],
        'annotation': None,
        'admission_modus': None,
        'lecture_period': []
    }
    for h4 in section.find_all('h4'):
        label = h4.get_text(strip=True).lower()
        next_elem = h4.find_next_sibling()
        if 'study type' in label and next_elem and next_elem.name == 'p':
            data['study_type'] = next_elem.get_text(strip=True)
        elif 'admission semester' in label and next_elem and next_elem.name == 'p':
            data['admission_semester'] = next_elem.get_text(strip=True)
        elif 'area of study' in label:
            ul = h4.find_next('ul')
            if ul:
                data['area_of_study'] = [li.get_text(strip=True) for li in ul.find_all('li')]
        elif 'annotation' in label and next_elem and next_elem.name == 'p':
            data['annotation'] = next_elem.get_text(strip=True)
        elif 'admission modus' in label and next_elem and next_elem.name == 'p':
            data['admission_modus'] = next_elem.get_text(strip=True)
        elif 'lecture period' in label:
            ul = h4.find_next('ul')
            if ul:
                data['lecture_period'] = [li.get_text(strip=True) for li in ul.find_all('li')]
    return data

def _extract_deadlines(section) -> list:
    deadlines = []
    for item in section.find_all('li', class_='mb-16'):
        entry = {}
        h5 = item.find('h5')
        if h5:
            entry['type'] = h5.get_text(strip=True)
        paragraphs = item.find_all('p', class_='js-dynamic-content')
        for i, p in enumerate(paragraphs):
            text = p.get_text(strip=True)
            if i == 0:
                entry['date'] = text
            else:
                entry['comment'] = text
                links = p.find_all('a', href=True)
                if links:
                    entry['links'] = [{'text': a.get_text(strip=True), 'url': a['href']} for a in links]
        if entry:
            deadlines.append(entry)
    return deadlines

def _extract_languages(section) -> dict:
    languages = {}
    for h4 in section.find_all('h4'):
        label = h4.get_text(strip=True)
        next_p = h4.find_next_sibling('p')
        if next_p:
            languages[label] = next_p.get_text(strip=True)
    return languages

def _extract_sidebar_info(sidebar) -> dict:
    data = {'university_name': None, 'university_website': None, 'contacts': {}}
    head = sidebar.find('div', class_='sidebar-head')
    if head:
        link = head.find('a', href=True)
        if link:
            data['university_website'] = link.get('href')
            sr = link.find('span', class_='sr-only')
            if sr:
                full = sr.get_text(strip=True)
                if ' - ' in full:
                    data['university_name'] = full.split(' - ')[0]
    for contact_sec in sidebar.find_all('div', class_='qa-contact-list'):
        h3 = contact_sec.find('h3')
        if h3:
            ctype = h3.get_text(strip=True)
            data['contacts'][ctype] = _extract_contact_details(contact_sec)
    return data

def _extract_contact_details(section) -> dict:
    contact = {}
    h4 = section.find('h4')
    if h4:
        contact['name'] = h4.get_text(strip=True)
    for cls, key in [('qa-address', 'address'), ('qa-zip', 'zip'), ('qa-city', 'city')]:
        dd = section.find('dd', class_=cls)
        if dd:
            contact[key] = dd.get_text(strip=True)
    for cls, key in [('qa-phone', 'phone'), ('qa-fax', 'fax')]:
        a = section.find('a', class_=cls)
        if a:
            contact[key] = a.get_text(strip=True)
    email = section.find('a', class_='qa-email')
    if email:
        contact['email'] = email.get_text(strip=True).replace(' at ', '@')
    web = section.find('a', class_='qa-web')
    if web:
        contact['web'] = web.get('href')
    return contact

def load_json(filepath: str) -> list:
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_json(filepath: str, data: list):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def process_batch(client: httpx.AsyncClient, urls: List[dict], results: list, failed: list, processed_urls: set):
    async def fetch_one(item: dict):
        url = item['url']
        if url in processed_urls:
            return None
        try:
            data = await extract_program_info(client, url)
            return ('success', data)
        except httpx.HTTPStatusError as e:
            return ('fail', {'url': url, 'error': f"HTTP {e.response.status_code}"})
        except httpx.ReadTimeout:
            return ('fail', {'url': url, 'error': "Timeout"})
        except Exception as e:
            return ('fail', {'url': url, 'error': str(e)})
    tasks = [fetch_one(item) for item in urls]
    outcomes = await asyncio.gather(*tasks)
    for outcome in outcomes:
        if outcome is None:
            continue
        status, data = outcome
        if status == 'success':
            results.append(data)
            processed_urls.add(data['link'])
        else:
            failed.append(data)

async def main():
    universities = load_json(INPUT_FILE)
    if not universities:
        print(f"No data found in {INPUT_FILE}. Run the university scraper first.")
        return
    print(f"Loaded {len(universities)} program URLs from {INPUT_FILE}")

    results = load_json(OUTPUT_FILE)
    failed = load_json(FAILED_FILE)
    processed_urls = {item['link'] for item in results}
    print(f"Resuming: {len(results)} already processed, {len(failed)} failed")

    remaining = [u for u in universities if u['url'] not in processed_urls]
    print(f"Remaining to process: {len(remaining)}")
    if not remaining:
        print("All URLs already processed!")
        return

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, headers=headers) as client:
        total_batches = (len(remaining) + CONCURRENT_LIMIT - 1) // CONCURRENT_LIMIT
        for i in range(0, len(remaining), CONCURRENT_LIMIT):
            batch = remaining[i:i + CONCURRENT_LIMIT]
            batch_num = i // CONCURRENT_LIMIT + 1
            print(f"\nBatch {batch_num}/{total_batches} - Processing {len(batch)} URLs...")
            await process_batch(client, batch, results, failed, processed_urls)
            save_json(OUTPUT_FILE, results)
            save_json(FAILED_FILE, failed)
            print(f"Progress: {len(results)} successful, {len(failed)} failed")
            if i + CONCURRENT_LIMIT < len(remaining):
                await asyncio.sleep(DELAY_BETWEEN_REQUESTS)
    print("\n" + "="*50)
    print("COMPLETED!")
    print(f"Successfully scraped: {len(results)}")
    print(f"Failed: {len(failed)}")
    print(f"Results saved to: {OUTPUT_FILE}")
    if failed:
        print(f"Failed URLs saved to: {FAILED_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
