"""
Extraction script to find all sales tracking data we need from subscribed URL pages.

1. Connect to RDS
2. Query all URLs from the RDS
3. Scrape the URL for: product_name,original_price,discount_price

psql -h $DB_HOST -U $DB_USER -d $DB_NAME -p $DB_PORT -> to connect to db for testing


"""
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
        html = requests.get(web_page, timeout=20)
    except requests.exceptions.MissingSchema:
        return "That URL does not exist."
    except requests.exceptions.ConnectionError:
        return "Cannot connect to that URL."
    if html.status_code > 299 or html.status_code < 200:
        logging.error(
            f"Issue with provided web_page: HTML Status Code - {html.status_code}")
        return f"Error: Something went wrong when trying to reach your webpage.."
    return html.content


def get_website_from_url(url: str) -> str:
    """ Gets a main website address from a given URL """
    website_url = url
    if ".com" in url:
        website_url = url.split(".com")[0] + ".com"
    elif ".co.uk" in url:
        website_url = url.split(".co.uk")[0] + ".co.uk"
    return website_url


def scrape_from_steam():
    """ Scrapes from Steam Websites. """


def scrape_from_amazon():
    """ Scrapes from Amazon product pages. """


def scrape_pricing_process(html_content: bytes, url: str, product_id: int) -> dict:
    """ Chooses which scraper to use based off of the URL """
    if get_website_from_url(url) not in ["https://www.amazon.co.uk", "https://www.amazon.com", "https://store.steampowered.com/"]:
        logging.error(
            "Cannot scrape that URL, since it's not an Amazon/Steam webpage.")
        return


def scrape_from_html(html_content: bytes, url: str, product_id: int) -> dict:
    """ Scrapes from html to get a dictionary with the:
    - Product_ID 
    - product_name
    - original_price
    - discount_price
    - website 
    for STEAM Games/Products."""
    s = BeautifulSoup(html_content, 'html.parser')

    results = s.find(id="game_area_purchase")

    if not results:
        logging.error("Can't scrape that URL.")
        return None

    original_price_elem = results.find(
        "div", class_="discount_original_price")
    discount_price_elem = results.find(
        "div", class_="discount_final_price")
    game_title_elem = s.find(
        id="appHubAppName", class_="apphub_AppName")
    regular_price_elem = s.find("div", class_="game_purchase_price price", attrs={
                                "data-price-final": True})

    if not game_title_elem:
        logging.error("Cannot find game title on the page for URL: %s", url)
        return None
    game_title = game_title_elem.text.strip()

    if original_price_elem and discount_price_elem:
        original_price = original_price_elem.text.strip() if original_price_elem else "N/A"
        discount_price = discount_price_elem.text.strip() if discount_price_elem else "N/A"
    elif regular_price_elem:
        original_price = regular_price_elem.text.strip()
        discount_price = original_price
    else:
        original_price = "N/A"
        discount_price = "N/A"

    product_information = {"product_id": product_id,
                           "original_price": original_price,
                           "discount_price": discount_price,
                           "game_title": game_title,
                           "website": get_website_from_url(url)}

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
        extracted_web_data = scrape_from_html(
            html_of_url, web_url, url_info[0])

        if extracted_web_data:
            all_scraped_product_information.append(extracted_web_data)
    return all_scraped_product_information


if __name__ == "__main__":
    load_dotenv()
    print(main_extraction_process())
