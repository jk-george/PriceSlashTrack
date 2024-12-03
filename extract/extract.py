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
    try:
        html = requests.get(web_page)
    except requests.exceptions.MissingSchema:
        return "That URL does not exist."
    except requests.exceptions.ConnectionError:
        return "That URL does not exist."
    if html.status_code > 299 or html.status_code < 200:
        return "That URL does not exist."
    return html.content


def get_website_from_url(url: str) -> str:
    """ Gets a main website address from a given URL """
    if ".com" in url:
        website_url = url.split(".com")[0] + ".com"
    elif ".co.uk" in url:
        website_url = url.split(".co.uk")[0] + ".co.uk"
    return website_url


def scrape_from_html(html_content: bytes, url: str) -> dict:
    """ Scrapes from html to get the product_name,original_price,discount_price in a dictionary. """
    s = BeautifulSoup(html_content, 'html.parser')

    results = s.find(id="game_area_purchase")
    original_price = results.find_all(
        "div", class_="discount_original_price")[0]
    discount_price = results.find_all(
        "div", class_="discount_final_price")[0]
    game_title = s.find(
        id="appHubAppName", class_="apphub_AppName")

    product_information = {"original_price": original_price.text,
                           "discount_price": discount_price.text,
                           "game_title": game_title.text}

    return product_information
