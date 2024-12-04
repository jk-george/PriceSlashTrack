import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from load import insert_price_change, load_price_changes


# @patch("load.datetime")
# def test_get_current_timestamp(mock_datetime):
#     """Test current timestamp generation."""
#     mock_datetime.utcnow.return_value = datetime(2024, 11, 9, 18, 0)
#     result = get_current_timestamp()
#     assert result == "2024-11-09T18:00:00"


# def test_calculate_discount_percentage_valid():
#     """Test valid discount percentage calculation."""
#     original_price = 100.0
#     current_price = 75.0
#     result = calculate_discount_percentage(original_price, current_price)
#     assert result == 25.0


# def test_calculate_discount_percentage_invalid():
#     """Test discount calculation with invalid original price."""
#     original_price = 0
#     current_price = 50.0
#     result = calculate_discount_percentage(original_price, current_price)
#     assert result == 0.0


# @patch("load.logging.error")
# def test_insert_price_change_failure(mock_log_error):
#     """Test price change insertion failure."""
#     mock_conn = MagicMock()
#     mock_conn.cursor.side_effect = Exception("Insertion error")
#     try:
#         insert_price_change(mock_conn, product_id=1,
#                             price=50.0, timestamp="2024-11-09T18:00:00")
#     except Exception:
#         pass
#     mock_log_error.assert_called_once_with(
#         "Error inserting price change: Insertion error")


# @patch("load.logging.error")
# def test_update_subscription_discount_failure(mock_log_error):
#     """Test subscription discount update failure."""
#     mock_conn = MagicMock()
#     mock_conn.cursor.side_effect = Exception("Update error")
#     try:
#         update_subscription_discount(
#             mock_conn, product_id=1, discount_percentage=20.0)
#     except Exception:
#         pass
#     mock_log_error.assert_called_once_with(
#         "Error updating subscription discount: Update error")


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
    """Combination of valid and invalid data insertion """
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
