# pylint: skip-file
import pytest
from unittest.mock import patch, MagicMock
from extract import (scrape_from_steam_html, get_html_from_url,
                     get_website_from_url, scrape_pricing_process,
                     extract_urls_from_db, get_html_with_age_gate_bypass,
                     scrape_from_debenhams_html)


def test_scrape_pricing_process_only_accepts_debenhams_and_steam():
    """Tests that scrape pricing process only accepts debenhams and steam."""
    assert scrape_pricing_process(
        "html_data", "https://unknown.co.uk/something-random", 1) == None


def test_get_website_from_url_com_websites():
    """Tests if .com websites gets replaced correctly."""
    result = get_website_from_url("https://store.steampowered.com/app/12345")
    assert result == "https://store.steampowered.com"

    result = get_website_from_url("https://www.debenhams.com/product")
    assert result == "https://www.debenhams.com"


def test_get_website_from_url_co_uk_websites():
    """Tests if website name is extracted correctly."""
    assert get_website_from_url(
        "something.co.uk/something-else") == "something.co.uk"


def test_get_website_from_url_edge_cases():
    """Test get_website_from_url with unusual input."""
    assert get_website_from_url(
        "https://example.com/") == "https://example.com"
    assert get_website_from_url("http://example.com") == "http://example.com"
    assert get_website_from_url("ftp://example.com") == "ftp://example.com"


def test_get_website_from_url_invalid():
    """Tests if an invalid URL gets caught."""
    assert get_html_from_url(
        "https://random_url") == "Cannot connect to that URL."
    assert get_html_from_url("random_url") == "That URL does not exist."
    assert get_html_from_url(
        "https://amazon.co.uk/something-random") == "Error: Something went wrong when trying to reach your webpage."


def test_get_website_from_url_empty():
    """Tests if no URL results in an error."""
    assert get_html_from_url("") == "That URL does not exist."


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


def test_scrape_from_steam_html_invalid():
    """Test scraping product info from Steam sample HTML with missing price elements."""
    steam_html = """
    <html>
      <div id="game_area_purchase"></div>
      <div id="appHubAppName" class="apphub_AppName">Test Game</div>
    </html>
    """
    html_content = steam_html.encode()
    url = "https://store.steampowered.com/app/12345/"
    product_id = 1
    result = scrape_from_steam_html(html_content, url, product_id=1)
    assert result == {
        "product_id": 1,
        "original_price": "N/A",
        "discount_price": "N/A",
        "game_title": "Test Game",
        "website": "https://store.steampowered.com"
    }


def test_scrape_from_steam_html_no_game_title():
    """Test scrape_from_steam_html when game title is missing."""
    steam_html = """
    <html>
      <div id="game_area_purchase">
        <div class="discount_original_price">£19.99</div>
        <div class="discount_final_price">£9.99</div>
      </div>
    </html>
    """
    result = scrape_from_steam_html(
        steam_html.encode(), "https://store.steampowered.com/app/12345", 1)
    assert result == None


def test_scrape_from_debenhams_html_valid():
    """Tests product information is scraped successfully for debenhams."""
    debenhams_html = """
    <html>
      <h1 class='text-xl'>Test Product</h1>
        <span data-test-id='product-price-current'>£320.00</span>
        <span data-test-id='product-price-was'>£330.00</span>
    </html>
    """

    result = scrape_from_debenhams_html(
        debenhams_html, "https://www.debenhams.com/product", 2)
    assert result == {
        "product_id": 2,
        "original_price": "£330.00",
        "discount_price": "£320.00",
        "product_title": "Test Product",
        "website": "https://www.debenhams.com"
    }


def test_scrape_from_debenhams_html_invalid():
    """Tests product information is scraped unsuccessfully for debenhams."""
    debenhams_html = """
    <html>
      <h1 class="text-xl">Test Product</h1>
    </html>
    """
    result = scrape_from_debenhams_html(
        debenhams_html, "https://www.debenhams.com/product", 2)
    assert result == None


def test_scrape_from_debenhams_html_no_prices():
    """Test scrape_from_debenhams_html when prices are missing."""
    debenhams_html = """
    <html>
      <h1 class="text-xl">Test Product</h1>
    </html>
    """
    result = scrape_from_debenhams_html(
        debenhams_html.encode(), "https://www.debenhams.com/product", 2)
    assert result is None


def test_scrape_pricing_process_empty_html():
    """Test scrape_pricing_process fails with empty HTML content."""
    result = scrape_pricing_process(
        "", "https://store.steampowered.com/app/12345", 1)
    assert result is None


def test_scrape_pricing_process_unsupported_url():
    """Test scrape_pricing_process fails with an unsupported URL."""
    result = scrape_pricing_process(
        "<html></html>", "https://unknownwebsite.com", 1)
    assert result is None


def test_extract_urls_from_db_valid():
    """Tests urls are extracted from the RDS database."""
    mock_url_list = [[1, "https://store.steampowered.com/app/12345"],
                     [2, "https://www.debenhams.com/product"]]
    with patch("extract.get_connection") as mock_get_connection, patch("extract.get_cursor") as mock_get_cursor:
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_url_list
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = extract_urls_from_db()
        assert result == mock_url_list


def test_extract_urls_from_db_empty():
    """Tests urls are extracted from the RDS database."""
    mock_url_list = []
    with patch("extract.get_connection") as mock_get_connection, patch("extract.get_cursor") as mock_get_cursor:
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_url_list
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = extract_urls_from_db()
        assert result == []


def test_get_html_with_age_gate_bypass_valid():
    """Tests age gate is bypassed successfully."""
    mock_steam_html = """
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

    with patch("extract.requests.Session") as mock_session:
        mock_session_instance = MagicMock()

        mock_session.return_value = mock_session_instance
        mock_session_instance.get.return_value.content = mock_steam_html
        mock_session_instance.get.return_value.status_code = 200

        result = get_html_with_age_gate_bypass(
            "https://store.steampowered.com/app/12345")
        assert result == mock_steam_html
