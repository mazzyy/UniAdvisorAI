# DAAD Scraper Selectors for BeautifulSoup Migration

# This file contains the CSS selectors used in the Selenium scraper.
# You can use these with BeautifulSoup's .select() or .select_one() methods.

selectors = {
    # Main Search Page
    "course_list_item": ".list-inline-item.mr-0.js-course-detail-link",  # Links to individual course pages
    "cookie_accept_button": "button.qa-cookie-consent-accept-selected",

    # Individual Course Page Details
    "course_title": "h2.c-detail-header__title > span:nth-child(1)",
    "institution_name": "h3.c-detail-header__subtitle",
    
    # The following use the same base structure but different child indices
    # Base container: #registration > .container > .c-description-list
    "admission_requirements": "#registration > .container > .c-description-list > *:nth-child(2) > *",
    "language_requirements": "#registration > .container > .c-description-list > *:nth-child(4) > *",
    "deadline": "#registration > .container > .c-description-list > *:nth-child(6) > *"
}

# Notes for BeautifulSoup implementation:
# 1. For 'institution_name', the original code splits lines and takes the second line.
# 2. For requirements and deadline, the original code iterates over all elements matching the selector 
#    and joins their innerText. In BS4, you might want to use .get_text(strip=True).
