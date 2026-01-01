import requests
from bs4 import BeautifulSoup
from typing import Optional
import re
import asyncio

async def extract_program_info(url: str) -> dict:
    """
    Extract program information from a DAAD program detail page.

    Args:
        url: The DAAD program URL

    Returns:
        Dictionary containing all program information
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers)
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
        'lecture_period': [],
        'university_name': None,
        'university_website': None,
        'contacts': {}
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
                        result['deadline_moreinfo_link'] = link.get('href')

    # Extract Overview section
    overview_section = soup.find('div', id='hsk-detail-overview')
    if overview_section:
        result.update(await _extract_section_content(overview_section))

    # Extract Application Deadlines section
    deadlines_section = soup.find('div', id='hsk-detail-deadlines')
    if deadlines_section:
        result['application_deadlines'] = await _extract_deadlines(deadlines_section)

    # Extract Tuition Fees section
    fees_section = soup.find('div', id='hsk-detail-fees')
    if fees_section:
        fee_link = fees_section.find('a', href=True)
        if fee_link:
            result['tuition_fees_link'] = fee_link.get('href')
        fee_info = fees_section.find('p', class_=lambda x: x and 'js-dynamic-content' in x)
        if fee_info:
            result['tuition_fees_info'] = fee_info.get_text(strip=True)

    # Extract Languages section
    lang_section = soup.find('div', id='hsk-detail-languages')
    if lang_section:
        result['languages_of_instruction'] = await _extract_languages(lang_section)

    # Extract University/Sidebar info
    sidebar = soup.find('aside')
    if sidebar:
        result.update(await _extract_sidebar_info(sidebar))

    return result

async def _extract_section_content(section) -> dict:
    """Extract content from overview section."""
    data = {
        'study_type': None,
        'admission_semester': None,
        'area_of_study': [],
        'annotation': None,
        'admission_modus': None,
        'lecture_period': []
    }
    h4s = section.find_all('h4')
    for h4 in h4s:
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

async def _extract_deadlines(section) -> list:
    """Extract detailed application deadlines."""
    deadlines = []
    deadline_items = section.find_all('li', class_='mb-16')
    for item in deadline_items:
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

async def _extract_languages(section) -> dict:
    """Extract language information."""
    languages = {}
    for h4 in section.find_all('h4'):
        label = h4.get_text(strip=True)
        next_p = h4.find_next_sibling('p')
        if next_p:
            languages[label] = next_p.get_text(strip=True)
    return languages

async def _extract_sidebar_info(sidebar) -> dict:
    """Extract university and contact information from sidebar."""
    data = {'university_name': None, 'university_website': None, 'contacts': {}}
    sidebar_head = sidebar.find('div', class_='sidebar-head')
    if sidebar_head:
        link = sidebar_head.find('a', href=True)
        if link:
            data['university_website'] = link.get('href')
            sr_text = link.find('span', class_='sr-only')
            if sr_text:
                full_text = sr_text.get_text(strip=True)
                if ' - ' in full_text:
                    data['university_name'] = full_text.split(' - ')[0]
    for contact_sec in sidebar.find_all('div', class_='qa-contact-list'):
        h3 = contact_sec.find('h3')
        if h3:
            contact_type = h3.get_text(strip=True)
            data['contacts'][contact_type] = await _extract_contact_details(contact_sec)
    return data

async def _extract_contact_details(contact_section) -> dict:
    """Extract contact details from a contact section."""
    contact = {}
    h4 = contact_section.find('h4')
    if h4:
        contact['name'] = h4.get_text(strip=True)
    for cls, key in [('qa-address', 'address'), ('qa-zip', 'zip'), ('qa-city', 'city')]:
        dd = contact_section.find('dd', class_=cls)
        if dd:
            contact[key] = dd.get_text(strip=True)
    for cls, key in [('qa-phone', 'phone'), ('qa-fax', 'fax')]:
        link = contact_section.find('a', class_=cls)
        if link:
            contact[key] = link.get_text(strip=True)
    email_link = contact_section.find('a', class_='qa-email')
    if email_link:
        contact['email'] = email_link.get_text(strip=True).replace(' at ', '@')
    web_link = contact_section.find('a', class_='qa-web')
    if web_link:
        contact['web'] = web_link.get('href')
    return contact

import json
async def main():
    try:
        url = "https://www.daad.de/en/studying-in-germany/universities/all-degree-programmes/detail/technische-hochschule-koeln-3d-animation-for-film-and-games-w60835/?hec-p=1&hec-id=w60835&hec-offset=0"
        program_info = await extract_program_info(url)
        print(json.dumps(program_info, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
