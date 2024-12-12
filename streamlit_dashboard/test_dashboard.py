"""Unit Tests for (streamlit) dashboard.py."""
# pylint: skip-file
import unittest
import pytest
from unittest.mock import patch, Mock, MagicMock
import pandas as pd
from datetime import datetime, timedelta
import altair as alt
from bs4 import BeautifulSoup
from dashboard import (
    get_html_from_url,
    get_website_from_url,
    display_charts, login, track_product, login_clicked
)


@pytest.fixture
def mock_db_connection():
    """Mocking the connection and cursor."""
    with patch('dashboard.get_connection') as mock_conn:
        with patch('dashboard.get_cursor') as mock_cursor:
            conn = MagicMock()
            cursor = MagicMock()
            mock_conn.return_value = conn
            mock_cursor.return_value = cursor
            yield cursor


@pytest.fixture
def mock_streamlit():
    """Mocking the streamlit dashboard."""
    with patch('streamlit.error') as mock_error:
        with patch('streamlit.toast') as mock_toast:
            yield {'error': mock_error, 'toast': mock_toast}


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


# @patch('dashboard.requests.get')
# def test_get_html_from_url_success(mock_get):
#     """Test fetching HTML content from a valid URL."""
#     mock_get.return_value = Mock(
#         status_code=200, content=b"<html>Valid HTML</html>")
#     url = "https://example.com"
#     assert get_html_from_url(url) == b"<html>Valid HTML</html>"


# def test_scrape_from_steam_html_valid():
#     """Test scraping product info from Steam sample HTML."""
#     steam_html = """
#     <html>
#       <div id="game_area_purchase">
#         <div class="discount_original_price">£19.99</div>
#         <div class="discount_final_price">£9.99</div>
#         <div class="game_header_image_full">https://testing.com/storage/image/test.jpg</div>
#         <div class="game_description_snippet">Testing Description</div>
#       </div>
#       <div id="appHubAppName" class="apphub_AppName">Test Game</div>
#     </html>
#     """
#     html_content = steam_html.encode()
#     url = "https://store.steampowered.com/app/12345/"
#     result = scrape_from_steam_html(html_content, url)
#     assert result == {
#         "original_price": "£19.99",
#         "discount_price": "£9.99",
#         "game_title": "Test Game",
#         'image_url': None,
#         'product_description': 'Testing Description',
#         "website": "https://store.steampowered.com"
#     }


# def test_scrape_from_steam_html_invalid():
#     """Test scraping product info from invalid or incomplete Steam HTML."""
#     invalid_html = """
#     <html>
#       <! Missing discount price and game title elements
#       <div id="game_area_purchase">
#         <div class="discount_final_price">£9.99</div>
#       </div>
#     </html>
#     """
#     html_content = invalid_html.encode()
#     url = "https://store.steampowered.com/app/12345/"
#     result = scrape_from_steam_html(html_content, url)
#     assert result == None


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


@patch('dashboard.st')
def test_display_charts_no_product_id(mock_st):
    """Returns None if there is an empty product_id"""
    mock_st.warning = MagicMock()

    result = display_charts(None)

    mock_st.warning.assert_called_once_with("Please select a valid product.")
    assert result is None


@patch('dashboard.st')
@patch('dashboard.execute_database_select_query_fetchall')
def test_display_charts_valid_product_id_24_hours(mock_db_function, mock_st):
    """Test with a valid product_id and mock database results."""
    mock_db_function.return_value = [
        (10.99, '2023-10-10T12:00:00Z'),
        (11.49, '2023-10-10T13:00:00Z'),
        (11.99, '2023-10-11T11:20:00Z')
    ]

    mock_st.selectbox.return_value = "Last 24 Hours"

    result = display_charts(1)

    assert isinstance(result, alt.Chart)
    mock_st.selectbox.assert_called_once_with(
        "Select Time Range", ["Last 3 Days",
                              "Last 24 Hours", "Last 30 Minutes"]
    )


@patch('dashboard.st')
@patch('dashboard.execute_database_select_query_fetchall')
def test_display_charts_valid_product_id_30_mins(mock_db_function, mock_st):
    """Test with a valid product_id and mock database results."""
    mock_db_function.return_value = [
        (10.99, '2023-10-10T12:00:00Z'),
        (11.49, '2023-10-10T13:00:00Z'),
        (11.99, '2023-10-11T11:20:00Z')
    ]

    mock_st.selectbox.return_value = "Last 30 Minutes"

    result = display_charts(1)

    assert isinstance(result, alt.Chart)
    mock_st.selectbox.assert_called_once_with(
        "Select Time Range", ["Last 3 Days",
                              "Last 24 Hours", "Last 30 Minutes"]
    )


# @patch('dashboard.st')
# @patch('dashboard.execute_database_select_query_fetchall')
# def test_display_charts_valid_product_id_3_days(mock_db_function, mock_st):
#     """Test with a valid product_id and mock database results."""
#     mock_db_function.return_value = [
#         (10.99, '2023-10-10T12:00:00Z'),
#         (11.49, '2023-10-10T13:00:00Z'),
#         (11.99, '2023-10-12T11:20:00Z')
#     ]

#     mock_st.selectbox.return_value = "Last 3 Days"

#     result = display_charts(1)

#     assert isinstance(result, alt.Chart)
#     mock_st.selectbox.assert_called_once_with(
#         "Select Time Range", ["Last 3 Days",
#                               "Last 24 Hours", "Last 30 Minutes"]
#     )


@patch('dashboard.st')
@patch('dashboard.execute_database_select_query_fetchall')
def test_empty_filtered_df(mock_db_function, mock_st):
    """Test when the filtered DataFrame is empty."""
    mock_db_function.return_value = [
    ]

    mock_st.selectbox.return_value = "Last 24 Hours"

    mock_st.warning = MagicMock()

    result = display_charts(1)

    mock_st.warning.assert_called_once_with(
        "No price data available for the selected time range.")
    assert result is None


def test_login_successful(mock_db_connection):
    """Tests successful connection with correct login credentials."""
    mock_db_connection.fetchone.return_value = [True]

    result = login('test@example.com', 'password123')

    assert result is True
    mock_db_connection.execute.assert_called_once_with(
        """
        SELECT EXISTS (
            SELECT 1
            FROM users
            WHERE email_address = %s AND password = %s
        );
        """,
        ('test@example.com', 'password123')
    )


def test_login_failed_incorrect_username(mock_db_connection):
    """Tests login failure if incorrect password is entered."""
    mock_db_connection.fetchone.return_value = [False]

    result = login('testuser@example.com', 'wrong_password')

    assert result is False


def test_login_failed_incorrect_username(mock_db_connection):
    """Tests login failure if incorrect password is entered."""
    mock_db_connection.fetchone.return_value = [False]

    result = login('incorrectusername', 'password123')

    assert result is False
