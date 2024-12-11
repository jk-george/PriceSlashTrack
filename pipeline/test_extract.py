# pylint: skip-file
import pytest
from extract import scrape_from_steam_html, get_html_from_url, get_website_from_url, scrape_pricing_process


def test_scrape_pricing_process_only_accepts_amazon_and_steam():
    """Tests that scrape pricing process only accepts amazon and steam"""
    assert scrape_pricing_process(
        "html_data", "https://unknown.co.uk/something-random", 1) == None


def test_website_finder_finds_com_websites():
    """Tests if .com/asdasf gets replaced correctly."""
    assert get_website_from_url(
        "something.com/something-else") == "something.com"


def test_website_finder_finds_co_uk_websites():
    """Tests if .co.uk/sasda gets replaced correctly."""
    assert get_website_from_url(
        "something.co.uk/something-else") == "something.co.uk"


def test_url_is_not_valid_returns_error_message():
    """Tests if an invalid URL gets caught."""
    assert get_html_from_url(
        "https://random_url") == "Cannot connect to that URL."
    assert get_html_from_url("random_url") == "That URL does not exist."
    assert get_html_from_url(
        "https://amazon.co.uk/something-random") == "Error: Something went wrong when trying to reach your webpage."


def test_scrape_from_steam_html_valid():
    """Test scraping product info from Steam sample HTML."""
    steam_html = """
    <html>
      <div id="game_area_purchase">
        <div class="discount_original_price">£19.99</div>
        <div class="discount_final_price">£9.99</div>
        <div class="game_header_image_full">https://testing.com/storage/image/test.jpg</div>
        <div class="game_description_snippet">Testing Description</div>
      </div>
      <div id="appHubAppName" class="apphub_AppName">Test Game</div>
    </html>
    """
    html_content = steam_html.encode()
    url = "https://store.steampowered.com/app/12345/"
    product_id = 1
    result = scrape_from_steam_html(html_content, url, product_id=1)
    assert result == {
        "product_id": 1,
        "original_price": "£19.99",
        "discount_price": "£9.99",
        "game_title": "Test Game",
        "website": "https://store.steampowered.com"
    }
