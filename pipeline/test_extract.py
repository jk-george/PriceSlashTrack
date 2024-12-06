import pytest

from extract import scrape_from_html, get_html_from_url, get_website_from_url, scrape_pricing_process


def test_scrape_pricing_process_only_accepts_amazon_and_steam():
    """Tests that scrape pricing process only accepts amazon and steam"""
    assert scrape_pricing_process(
        "html_data", "https://unknown.co.uk/something-random", 1) == None


def test_website_finder_finds_com_websites():
    """ Tests if .com/asdasf gets replaced correctly. """
    assert get_website_from_url(
        "something.com/something-else") == "something.com"


def test_website_finder_finds_co_uk_websites():
    """ Tests if .co.uk/sasda gets replaced correctly"""
    assert get_website_from_url(
        "something.co.uk/something-else") == "something.co.uk"


def test_url_is_not_valid_returns_error_message():
    """ Tests if an invalid URL gets caught. """
    assert get_html_from_url(
        "https://random_url") == "Cannot connect to that URL."
    assert get_html_from_url("random_url") == "That URL does not exist."
    assert get_html_from_url(
        "https://amazon.co.uk/something-random") == "Error: Something went wrong when trying to reach your webpage."


@pytest.fixture
def html_object():
    """Fixture that creates a test html string of a game called The Planet Crafter"""
    with open("test_extract_html.txt", "r", encoding="UTF-8") as test_file:
        html_string = test_file.read()
    return html_string


def test_scraper_gets_correct_steam_original_and_discount_price(html_object):
    """ Tests to see that the scraper can get a steam original and discount price. """
    url = "https://store.steampowered.com/app/1284190/The_Planet_Crafter/"
    test_product_info = scrape_from_html(html_object, url, 1)
    assert test_product_info.get("original_price") == "£19.99"
    assert test_product_info.get("discount_price") == "£11.99"
    assert test_product_info.get("game_title") == "The Planet Crafter"
    assert test_product_info.get(
        "website") == "https://store.steampowered.com"
