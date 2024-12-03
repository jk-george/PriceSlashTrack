"""
Extraction script to find all sales tracking data we need from subscribed URL pages.

1. Connect to RDS
2. Query all URLs from the RDS
3. Scrape the URL for: product_name,original_price,discount_price

"""

import requests
from bs4 import BeautifulSoup


def extract_urls_from_db() -> list[str]:
    """Function to get urls from a database"""
    ...


def get_html_from_url(web_page: str) -> bytes:
    """ Gets the html content from a given URL"""
    html = requests.get(web_page)
    return html.content


def scrape_from_html(html_content: bytes) -> dict:
    """ Scrapes from html to get the product_name,original_price,discount_price in a dictionary. """
    product_information = {}

    return product_information
