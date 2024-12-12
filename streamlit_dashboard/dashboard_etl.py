"""Functions for the dashboard"""

import requests
import logging
from bs4 import BeautifulSoup


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
        html = requests.get(web_page, timeout=20)
    except requests.exceptions.MissingSchema:
        return "That URL does not exist."
    except requests.exceptions.ConnectionError:
        return "Cannot connect to that URL."
    if html.status_code > 299 or html.status_code < 200:
        return f"Error: {html.status_code}."
    return html.content


def get_website_from_url(url: str) -> str:
    """Gets a main website address from a given URL """
    website_url = url
    if ".com" in url:
        website_url = url.split(".com")[0] + ".com"
    elif ".co.uk" in url:
        website_url = url.split(".co.uk")[0] + ".co.uk"
    return website_url


def scrape_pricing_process(html_content: bytes, url: str) -> dict:
    """Chooses which scraper to use based off of the URL."""

    website_url = get_website_from_url(url)

    if "https://store.steampowered.com" in website_url:
        return scrape_from_steam_html(html_content, url)

    if "https://www.debenhams.com" in website_url:
        return scrape_from_debenhams_html(html_content, url)

    logging.error(
        "Cannot scrape that URL, since it's not a Debenhams or Steam webpage.")
    return


def scrape_from_steam_html(html_content: bytes, url: str) -> dict:
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

    image_element = s.find("img", class_="game_header_image_full")
    description_element = s.find("div", class_="game_description_snippet")

    if not game_title_element:
        logging.error("Cannot find product title on the page for URL: %s", url)
        return None
    game_title = game_title_element.text.strip()

    if image_element:
        image_url = image_element['src']
    else:
        image_url = None

    if description_element:
        product_description = description_element.text.strip()
    else:
        product_description = "No description found."

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

    product_information = {
        "original_price": original_price,
        "discount_price": discount_price,
        "product_name": game_title,
        "image_url": image_url,
        "product_description": product_description,
        "website": get_website_from_url(url)}

    return product_information


def scrape_from_debenhams_html(html_content: bytes, url: str) -> dict:
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

    product_description_element = s.find(
        "div", class_="prose")
    if not product_description_element:
        logging.error(
            "Cannot find product_description element for URL: %s", url)
        return None
    product_description = product_description_element.text.strip()
    image_url_element = s.find(
        'img', attrs={'class': 'h-auto w-auto object-cover undefined undefined'})
    if not image_url_element:
        logging.error("Cannot find image element for URL: %s", url)
        image_url_element = None
    image_url = image_url_element['src']

    product_information = {
        "original_price": original_price,
        "discount_price": current_price,
        "product_name": product_title,
        "image_url": image_url,
        "product_description": product_description,
        "website": get_website_from_url(url)
    }

    print(product_information)
    return product_information


def clean_price(price_str: str) -> float:
    """Cleans current/discount price string to float"""
    try:
        cleaned_price = float(price_str.replace(
            "£", "").replace(",", "").strip())
        return cleaned_price if cleaned_price >= 0 else None
    except ValueError:
        return None
