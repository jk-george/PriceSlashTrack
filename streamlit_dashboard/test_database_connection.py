# pylint: skip-file
from unittest.mock import patch, MagicMock
import psycopg2
from database_connection import (get_connection, get_cursor,
                                 execute_database_select_query_fetchall,
                                 execute_database_select_query_fetchone,
                                 get_website_id, get_user_id, get_product_id,
                                 get_subscription_id, get_product_subscription,
                                 get_product_info, get_latest_price,
                                 stop_tracking_product, create_account,
                                 insert_into_website, insert_into_product,
                                 insert_into_subscription, insert_initial_price)


def test_get_connection_valid():
    """Returns successful database connection."""
    with patch('psycopg2.connect') as mock_connect:
        mock_connect.return_value = MagicMock()
        connection = get_connection()
        assert connection != None


def test_get_connection_invalid():
    """Returns None when database connection fails."""
    with patch('psycopg2.connect') as mock_connect:
        mock_connect.side_effect = psycopg2.Error("Connection failed")
        connection = get_connection()
        assert connection == None


def test_get_cursor_valid():
    """Returns cursor successfully."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    cursor = get_cursor(mock_connection)
    assert cursor != None


def test_get_cursor_with_none_connection():
    """Returns no cursor object upon failure."""
    cursor = get_cursor(None)
    assert cursor == None


def test_get_cursor_failure():
    """Returns None when the connection fails."""
    mock_connection = MagicMock()
    mock_connection.cursor.side_effect = psycopg2.Error("Cursor failed")
    cursor = get_cursor(mock_connection)
    assert cursor == None


def test_execute_select_query_fetchall_valid():
    """Returns results when select query is successful"""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = [(1, 'test')]

            result = execute_database_select_query_fetchall(
                "SELECT * FROM test", ('test',), "Error message")
            assert result == [(1, 'test')]


def test_execute_select_query_fetchall_no_results():
    """Returns None when there are no results."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = []

            result = execute_database_select_query_fetchall(
                "SELECT * FROM test", ('test',), "Error message")
            assert result == None


def test_execute_select_query_fetchone():
    """Tests returns one result after calling fetchone."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = [(1,)]

            result = execute_database_select_query_fetchone(
                "SELECT * FROM test", ('test',))
            assert result == [(1,)]


def test_get_product_subscription_valid():
    """Returns list of product IDs successfully."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = [(1,), (2,)]

            result = get_product_subscription(1)
            assert result == [(1,), (2,)]


def test_get_product_subscription_none():
    """Tests doesn't return list of product IDs when there are no subscriptions"""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = None

            result = get_product_subscription(1)
            assert result == None


def test_get_product_info_valid():
    """Returns information about of product as a tuple successfully."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            expected_result = ('Product', 'url', 10.99,
                               'description', 'image_url')
            mock_cursor.fetchone.return_value = expected_result

            result = get_product_info(1)
            assert result == expected_result


def test_get_latest_price_valid():
    """Returns the latest price successfully."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (10.99,)

            result = get_latest_price(1)
            assert result == 10.99


def test_stop_tracking_product_valid():
    """Tests stop_tracking_product is called successfully once."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor

            stop_tracking_product(1, 1)
            mock_cursor.execute.assert_called_once()
            mock_connection.commit.assert_called_once()


def test_get_website_id_valid():
    """Returns correct website ID."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1,)

            result = get_website_id("test_website")
            assert result == 1


def test_insert_into_website_valid():
    """Returns new website ID inserted."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            with patch('database_connection.get_website_id') as mock_get_website_id:
                mock_connection = MagicMock()
                mock_cursor = MagicMock()
                mock_get_conn.return_value = mock_connection
                mock_get_cursor.return_value = mock_cursor
                mock_get_website_id.side_effect = [None, 1]

                result = insert_into_website("test_website")
                assert result == 1


def test_insert_initial_price_valid():
    """Returns successful insertion of initial price."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor

            insert_initial_price(10.99, 1)
            mock_cursor.execute.assert_called_once()
            mock_connection.commit.assert_called_once()


def test_insert_into_subscription_new_valid():
    """Tests successful insertion of new subscriptions after none."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            with patch('database_connection.get_subscription_id') as mock_get_sub_id:
                mock_connection = MagicMock()
                mock_cursor = MagicMock()
                mock_get_conn.return_value = mock_connection
                mock_get_cursor.return_value = mock_cursor
                mock_get_sub_id.side_effect = [None, 1]

                result = insert_into_subscription(1, 1, 10.99)
                assert result == 1


def test_get_user_id_valid():
    """Returns correct user ID."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1,)

            result = get_user_id("test@email.com")
            assert result == 1


def test_create_account_valid():
    """Tests account is created successfully."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor

            result = create_account(
                "John", "Doe", "john@email.com", "password123")
            assert result is True


def test_create_account_invalid():
    """Tests failed account creation."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Insert failed")

            result = create_account(
                "John", "Doe", "john@email.com", "password123")
            assert result is False


def test_get_product_info_error():
    """Returns None upon error when getting invalid product"""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Database error")

            result = get_product_info(1)
            assert result == None


def test_get_latest_price_error():
    """Returns None upon error for retrieving latest price."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Database error")

            result = get_latest_price(1)
            assert result == None


def test_stop_tracking_product_error():
    """Error unsubscribing product doesn't result in a crash."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Database error")

            stop_tracking_product(1, 1)


def test_get_website_id_error():
    """Tests returns None when there is a database error."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = psycopg2.Error("Database error")

            result = get_website_id("test_website")
            assert result == None


def test_get_user_id_error():
    """Returns None when there is a database error."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = psycopg2.Error("Database error")

            result = get_user_id("test@email.com")
            assert result == None


def test_get_product_id_error():
    """Returns None when there is a database error."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = psycopg2.Error("Database error")

            result = get_product_id("test_url")
            assert result == None


def test_get_subscription_id_error():
    """Returns None when there is a database error."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = psycopg2.Error("Database error")

            result = get_subscription_id(1, 1)
            assert result is None


def test_insert_into_website_existing_valid():
    """Returns a valid existing website ID."""
    with patch('database_connection.get_website_id') as mock_get_website_id:
        mock_get_website_id.return_value = 1

        result = insert_into_website("test_website")
        assert result == 1


def test_insert_into_website_invalid():
    """Returns None when there is an error inserting into website"""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            with patch('database_connection.get_website_id') as mock_get_website_id:
                mock_connection = MagicMock()
                mock_cursor = MagicMock()
                mock_get_conn.return_value = mock_connection
                mock_get_cursor.return_value = mock_cursor
                mock_get_website_id.return_value = None
                mock_cursor.execute.side_effect = Exception("Insert failed")

                result = insert_into_website("test_website")
                assert result == None


def test_insert_into_product_existing_valid():
    """Return existing product ID successfully."""
    with patch('database_connection.get_product_id') as mock_get_product_id:
        mock_get_product_id.return_value = 1

        result = insert_into_product(1, "test_url")
        assert result == 1


@patch('database_connection.scrape_pricing_process')
@patch('database_connection.get_html_from_url')
def test_insert_into_product_new_valid(mock_get_html, mock_scrape):
    """Tests returns new product ID after a None result beforehand"""
    mock_get_html.return_value = "<html>test</html>"
    mock_scrape.return_value = {
        "game_title": "Test Game",
        "original_price": "10.99",
        "image_url": "test.jpg",
        "product_description": "Test description"
    }

    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            with patch('database_connection.get_product_id') as mock_get_product_id:
                mock_connection = MagicMock()
                mock_cursor = MagicMock()
                mock_get_conn.return_value = mock_connection
                mock_get_cursor.return_value = mock_cursor
                mock_get_product_id.side_effect = [None, 1]

                result = insert_into_product(1, "test_url")
                assert result == 1


def test_insert_initial_price_error():
    """Tests failure inserting initial price when error occurs."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Insert failed")

            insert_initial_price(10.99, 1)


def test_get_subscription_id_invalid():
    """Tests returns None when no subscriptions are found."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None

            result = get_subscription_id(1, 1)
            assert result == None


def test_get_product_subscription_invalid():
    """Should return a None on database error."""
    with patch('database_connection.get_connection') as mock_get_conn:
        with patch('database_connection.get_cursor') as mock_get_cursor:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_get_conn.return_value = mock_connection
            mock_get_cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = psycopg2.Error("Database error")

            result = get_product_subscription(1)
            assert result == None


# 95% - %75
