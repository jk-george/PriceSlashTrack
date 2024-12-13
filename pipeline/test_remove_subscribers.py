"""Unit Tests for removing subscribers script."""
# pylint: skip-file
import pytest
from unittest.mock import Mock, patch
from remove_subscribers import (get_product_ids_from_table, delete_from_table,
                                delete_unsubscribed_data, main_remove_subscriptions, clean_websites, lambda_handler)


@pytest.fixture
def mock_conn():
    """Mocks connection."""
    return Mock()


@pytest.fixture
def mock_cursor():
    """Mocks cursor."""
    cursor = Mock()
    cursor.__enter__ = Mock(return_value=cursor)
    cursor.__exit__ = Mock(return_value=None)
    return cursor


def test_get_product_ids_from_table_success(mock_conn, mock_cursor):
    """Returns product ids from a table using distinct query is successfully ran."""
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1,), (2,), (3,)]

    result = get_product_ids_from_table(
        mock_conn, "subscription", distinct=True)

    assert result == {1, 2, 3}
    mock_cursor.execute.assert_called_once_with(
        "SELECT DISTINCT product_id FROM subscription;"
    )


def test_get_product_ids_from_table_no_distinct(mock_conn, mock_cursor):
    """Returns product ids without using distinction query."""
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1,), (2,), (2,), (3,)]

    result = get_product_ids_from_table(mock_conn, "product")

    assert result == {1, 2, 3}
    mock_cursor.execute.assert_called_once_with(
        "SELECT  product_id FROM product;"
    )


def test_get_product_ids_from_table_error(mock_conn, mock_cursor):
    """Returns an error and returns empty set if invalid."""
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Database error")

    result = get_product_ids_from_table(mock_conn, "subscription")

    assert result == set()


def test_delete_unsubscribed_data(mock_conn, mock_cursor):
    """Tests deletion of data with unsubscribed product ids."""
    mock_conn.cursor.return_value = mock_cursor
    unsubscribed_ids = [1, 2, 3]

    delete_unsubscribed_data(mock_conn, unsubscribed_ids)

    assert mock_cursor.execute.call_count == 3
    mock_conn.commit.assert_called_once()


def test_delete_unsubscribed_data_error(mock_conn, mock_cursor):
    """Rollback called if an error is raised during deletion of unsubscribed products."""
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Database error")

    delete_unsubscribed_data(mock_conn, [1, 2, 3])

    mock_conn.rollback.assert_called_once()


@patch('remove_subscribers.get_connection')
def test_main_remove_subscriptions_valid(mock_get_connection, mock_conn, mock_cursor):
    """Tests main function for cleaning the product, price changes and websites schema successfully."""
    mock_conn.cursor.return_value = mock_cursor
    mock_get_connection.return_value.__enter__.return_value = mock_conn

    mock_cursor.fetchall.side_effect = [
        [(1,), (2,)],
        [(2,), (3,)],
        [(1,), (2,), (3,), (4,)]]

    main_remove_subscriptions()
    mock_cursor.execute.assert_called()


@patch('remove_subscribers.get_connection')
def test_main_remove_subscriptions_no_unsubscribed(mock_get_connection, mock_conn, mock_cursor):
    """Tests main_remove_subscriptions when there are no unsubscribed products."""
    mock_conn.cursor.return_value = mock_cursor
    mock_get_connection.return_value.__enter__.return_value = mock_conn

    mock_cursor.fetchall.side_effect = [
        [(1,), (2,)],
        [(1,), (2,)]]

    main_remove_subscriptions()

    mock_cursor.execute.assert_any_call(
        "SELECT DISTINCT product_id FROM subscription;")
    mock_cursor.execute.assert_any_call("SELECT  product_id FROM product;")

    assert mock_cursor.execute.call_count == 2


def test_delete_from_table_valid(mock_cursor):
    """Tests delete_from_table constructs and executes correct query with parameters."""
    table_name = "price_changes"
    product_ids = [1, 2, 3]

    expected_query = "DELETE FROM price_changes WHERE product_id = ANY(%s);"
    expected_params = (product_ids,)

    delete_from_table(mock_cursor, table_name, product_ids)

    mock_cursor.execute.assert_called_once_with(
        expected_query, expected_params)


def test_delete_from_price_changes_empty_product_ids(mock_cursor):
    """Tests delete_from_table with an empty list of product_ids."""
    table_name = "price_changes"
    product_ids = []

    expected_query = "DELETE FROM price_changes WHERE product_id = ANY(%s);"
    expected_params = (product_ids,)

    delete_from_table(mock_cursor, table_name, product_ids)

    mock_cursor.execute.assert_called_once_with(
        expected_query, expected_params
    )


@patch('remove_subscribers.main_remove_subscriptions', side_effect=Exception("Error"))
def test_lambda_handler_exception(mock_main_remove_subscriptions):
    """Tests Lambda handler when an exception is raised."""
    result = lambda_handler(event={}, context={})

    mock_main_remove_subscriptions.assert_called_once()
    assert result == {
        "status_code": 500,
        "message": "Execution of subscription removal process was not successful."
    }
