"""Extraction script that retrieves information from products with active subscriptions."""
import logging

from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

from connect_to_database import get_connection, get_cursor

QUERY_TO_FIND_URLS = """
SELECT product_id,url FROM product;
"""


def extract_urls_from_db() -> list[list[int, str]]:
    """Function to get urls from a database
    returns the id of the product and its URL page in a list: [id,url]"""
    conn = get_connection()

    with get_cursor(conn) as db_cursor:
        db_cursor.execute(QUERY_TO_FIND_URLS)
        url_list = db_cursor.fetchall()

    return url_list


def get_html_with_age_gate_bypass(url: str) -> bytes:
    """Handles Steam URLs with age-gates by simulating form submission."""
    try:
        session = requests.Session()
        session.get(url, timeout=20)

        app_id = url.split('/app/')[1].split('/')[0]

        age_gate_data = {
            "ageDay": "1",
            "ageMonth": "January",
            "ageYear": "1990",
        }
        bypass_url = f"https://store.steampowered.com/agecheck/app/{app_id}/"
        session.post(bypass_url, data=age_gate_data, timeout=20)

        response = session.get(url, timeout=20)
        response.raise_for_status()

        return response.content
    except requests.exceptions.RequestException as e:
        logging.error("Error fetching age-gated URL %s: %s", url, e)
        return None


def get_html_from_url(web_page: str) -> bytes:
    """ Gets the html content from a given URL"""
    if "store.steampowered.com" in web_page:
        return get_html_with_age_gate_bypass(web_page)

    try:
        html = requests.get(web_page, timeout=30)
    except requests.exceptions.MissingSchema:
        return "That URL does not exist."
    except requests.exceptions.ConnectionError:
        return "Cannot connect to that URL."
    if html.status_code > 299 or html.status_code < 200:
        logging.error(
            "Issue with provided web_page: HTML Status Code - %s", html.status_code)
        return "Error: Something went wrong when trying to reach your webpage."
    return html.content


def get_website_from_url(url: str) -> str:
    """ Gets a main website address from a given URL """
    website_url = url
    if ".com" in url:
        website_url = url.split(".com")[0] + ".com"
    elif ".co.uk" in url:
        website_url = url.split(".co.uk")[0] + ".co.uk"
    return website_url


def scrape_pricing_process(html_content: bytes, url: str, product_id: int) -> dict:
    """Chooses which scraper to use based off of the URL."""

    website_url = get_website_from_url(url)

    if "https://store.steampowered.com" in website_url:
        return scrape_from_steam_html(html_content, url, product_id)

    if "https://www.debenhams.com" in website_url:
        return scrape_from_debenhams_html(html_content, url, product_id)

    logging.error(
        "Cannot scrape that URL, since it's not a Debenhams or Steam webpage.")
    return


def scrape_from_debenhams_html(html_content: bytes, url: str, product_id: int) -> dict:
    """Scrapes product, price and website information from Debenhams."""
    s = BeautifulSoup(html_content, 'html.parser')

    product_title_element = s.find("h1", class_="text-xl")
    if not product_title_element:
        logging.error("Cannot find product title on the page for URL: %s", url)
        return None

    current_price_element = s.find(
        "span", {"data-test-id": "product-price-current"})
    if not current_price_element:
        logging.error("Cannot find current price element for URL: %s", url)
        return None

    original_price_element = s.find(
        "span", {"data-test-id": "product-price-was"})
    if not original_price_element:
        logging.error("Cannot find original price element for URL: %s", url)
        original_price_element = current_price_element

    product_title = product_title_element.text.strip()
    current_price = current_price_element.text.strip()
    original_price = original_price_element.text.strip(
    ) if original_price_element else current_price

    product_information = {
        "product_id": product_id,
        "original_price": original_price,
        "discount_price": current_price,
        "product_title": product_title,
        "website": get_website_from_url(url)}

    print(product_information)
    return product_information


def scrape_from_steam_html(html_content: bytes, url: str, product_id: int) -> dict:
    """Scrapes product, price and website information from Steam."""
    s = BeautifulSoup(html_content, 'html.parser')

    results = s.find(id="game_area_purchase")

    if not results:
        logging.error("Can't scrape that Steam URL.")
        return None

    original_price_element = results.find(
        "div", class_="discount_original_price")
    discount_price_element = results.find(
        "div", class_="discount_final_price")
    game_title_element = s.find(
        id="appHubAppName", class_="apphub_AppName")
    regular_price_element = s.find("div", class_="game_purchase_price price", attrs={
        "data-price-final": True})

    if not game_title_element:
        logging.error("Cannot find product title on the page for URL: %s", url)
        return None
    game_title = game_title_element.text.strip()

    if original_price_element and discount_price_element:
        original_price = original_price_element.text.strip(
        ) if original_price_element else "N/A"
        discount_price = discount_price_element.text.strip(
        ) if discount_price_element else "N/A"
    elif regular_price_element:
        original_price = regular_price_element.text.strip()
        discount_price = original_price
    else:
        original_price = "N/A"
        discount_price = "N/A"

    product_information = {"product_id": product_id,
                           "original_price": original_price,
                           "discount_price": discount_price,
                           "game_title": game_title,
                           "website": get_website_from_url(url)}
    print(product_information)
    return product_information


def main_extraction_process() -> list[dict]:
    """ Carries out the whole extraction process into a list of dictionaries,
    ready to be transformed/inserted into a Database.
    Reminder: extract_urls_from_db() -> list of [id,url]"""
    list_of_urls = extract_urls_from_db()
    print(list_of_urls)

    all_scraped_product_information = []

    for url_info in list_of_urls:
        web_url = url_info[1]
        html_of_url = get_html_from_url(web_url)

        extracted_web_data = scrape_pricing_process(
            html_of_url, web_url, url_info[0])

        if extracted_web_data:
            all_scraped_product_information.append(extracted_web_data)
    return all_scraped_product_information


if __name__ == "__main__":
    load_dotenv()
    main_extraction_process()
