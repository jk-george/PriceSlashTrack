"""Unit Tests for (streamlit) dashboard.py."""
# pylint: skip-file
import unittest
import pytest
from unittest.mock import patch, Mock, MagicMock
from bs4 import BeautifulSoup
from dashboard import (
    get_html_with_age_gate_bypass,
    get_html_from_url,
    get_website_from_url,
    scrape_from_amazon_html,
    scrape_from_steam_html
)


def test_get_website_from_url_valid_1():
    """Returns valid website url that ends in .com"""
    test_website = "https://testingwebsite.com/app/01010/test_product/"
    assert get_website_from_url(
        test_website) == "https://testingwebsite.com"


def test_get_website_from_url_valid_2():
    """Returns valid website url that ends in .co.uk"""
    test_website = "https://test.testing.co.uk/app/01010/test_product/"
    assert get_website_from_url(
        test_website) == "https://test.testing.co.uk"


def test_get_website_from_url_invalid():
    """Returns valid website url that ends in .co.uk"""
    test_website = "https://test.testing/invalid"
    assert get_website_from_url(
        test_website) == "https://test.testing/invalid"


@patch('dashboard.requests.get')
def test_get_html_from_url_success(mock_get):
    """Test fetching HTML content from a valid URL."""
    mock_get.return_value = Mock(
        status_code=200, content=b"<html>Valid HTML</html>")
    url = "https://example.com"
    assert get_html_from_url(url) == b"<html>Valid HTML</html>"


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
    result = scrape_from_steam_html(html_content, url)
    assert result == {
        "original_price": "£19.99",
        "discount_price": "£9.99",
        "game_title": "Test Game",
        'image_url': None,
        'product_description': 'Testing Description',
        "website": "https://store.steampowered.com"
    }


def test_scrape_from_steam_html_invalid():
    """Test scraping product info from invalid or incomplete Steam HTML."""
    invalid_html = """
    <html>
      <! Missing discount price and game title elements
      <div id="game_area_purchase">
        <div class="discount_final_price">£9.99</div>
      </div>
    </html>
    """
    html_content = invalid_html.encode()
    url = "https://store.steampowered.com/app/12345/"
    result = scrape_from_steam_html(html_content, url)
    assert result == None


# def test_scrape_from_steam_html_invalid_url():
#     """Test scraping product info when provided an invalid URL."""
#     valid_html = """
#     <html>
#       <div id="game_area_purchase">
#         <div class="discount_original_price">£19.99</div>
#         <div class="discount_final_price">£9.99</div>
#       </div>
#       <div id="appHubAppName" class="apphub_AppName">Sample Game</div>
#     </html>
#     """
#     html_content = valid_html.encode()
#     invalid_url = "https://example.com/not_steam_url"
#     result = scrape_from_steam_html(html_content, invalid_url)
#     assert result is None
