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
    """ Chooses which scraper to use based off of the URL """

    website_url = get_website_from_url(url)

    if "https://store.steampowered.com" in website_url:
        return scrape_from_steam_html(html_content, url)

    if "https://www.amazon.com" in url or "https://www.amazon.co." in website_url:
        return scrape_from_amazon_html(html_content, url)

    logging.error(
        "Cannot scrape that URL, since it's not an Amazon/Steam webpage.")
    return


def scrape_from_amazon_html(html_content: bytes, url: str) -> dict:
    """Scrapes product, price and website information from Amazon."""
    s = BeautifulSoup(html_content, 'html.parser')

    results = s.find("div", id="corePriceDisplay_desktop_feature_div")

    if not results:
        logging.error("Can't scrape from Amazon URL")
        return None

    product_title_element = s.find(id="productTitle")

    if not product_title_element:
        logging.error("Cannot find game title on the page for URL: %s", url)
        return None

    discount_price = results.find(
        "div", class_="a-section a-spacing-none aok-align-center aok-relative").find("span", class_="aok-offscreen").text
    original_price = results.find(
        "div",
        class_="a-section a-spacing-small aok-align-center").find("span", class_="a-offscreen").text
    product_title = product_title_element.text.strip()

    product_information = {
        "original_price": original_price,
        "discount_price": discount_price,
        "game_title": product_title,
        "website": get_website_from_url(url)}
    return product_information


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
        "game_title": game_title,
        "image_url": image_url,
        "product_description": product_description,
        "website": get_website_from_url(url)}

    return product_information


def clean_price(price_str: str) -> float:
    """Cleans current/discount price string to float"""
    try:
        cleaned_price = float(price_str.replace(
            "£", "").replace(",", "").strip())
        return cleaned_price if cleaned_price >= 0 else None
    except ValueError:
        return None
