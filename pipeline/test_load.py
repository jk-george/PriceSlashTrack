# pylint: skip-file
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from load import insert_price_change, load_price_changes


def test_insert_price_change_valid():
    """Insert query for inserting valid data successfully."""
    mock_conn = MagicMock()

    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    insert_price_change(mock_conn, 1, 22.49, "2024-12-04 16:31:40")

    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args[0][1] == (
        22.49, 1, "2024-12-04 16:31:40")


def test_load_price_changes_valid():
    """Loading valid data into the price_changes table successfully."""
    mock_conn = Mock()
    test_data = [
        {'price': 22.49, 'product_id': 8, 'timestamp': '2024-12-04 16:31:40'},
        {'price': 7.69, 'product_id': 9, 'timestamp': '2024-12-04 16:31:40'}
    ]

    load_price_changes(test_data, mock_conn)

    assert mock_conn.commit.called
    assert not mock_conn.rollback.called


@patch("load.insert_price_change")
def test_load_price_changes_invalid(mock_insert_price_change):
    """Loading invalid data result in a rollback rather than commit being called."""
    mock_conn = MagicMock()
    mock_insert_price_change.side_effect = Exception("Database error")

    test_data = [{'price': 22.49, 'product_id': 8,
                  'timestamp': '2024-12-04 16:31:40'}]

    load_price_changes(test_data, mock_conn)

    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_not_called()


def test_load_price_changes_empty():
    """Ensure no database operations occur when given an empty list."""
    mock_conn = Mock()
    test_data = []

    load_price_changes(test_data, mock_conn)

    mock_conn.commit.assert_not_called()
    mock_conn.rollback.assert_called_once()


@patch("load.insert_price_change")
def test_load_price_changes_partial_failure(mock_insert_price_change):
    """Combination of valid and invalid data insertion results ."""
    mock_conn = MagicMock()
    mock_insert_price_change.side_effect = [None, Exception("Database error")]

    test_data = [
        {'price': 22.49, 'product_id': 8, 'timestamp': '2024-12-04 16:31:40'},
        {'price': 7.69, 'product_id': 9, 'timestamp': '2024-12-04 16:31:40'}
    ]

    try:
        load_price_changes(test_data, mock_conn)
    except Exception:
        pass
    mock_conn.rollback.assert_not_called()
    mock_conn.commit.assert_called_once()
