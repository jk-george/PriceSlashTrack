import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime
from load import (
    calculate_discount_percentage,
    get_current_timestamp,
    insert_price_change,
    update_subscription_discount,
    load_price_changes
)


@patch("load.datetime")
def test_get_current_timestamp(mock_datetime):
    """Test current timestamp generation."""
    mock_datetime.utcnow.return_value = datetime(2024, 11, 9, 18, 0)
    result = get_current_timestamp()
    assert result == "2024-11-09T18:00:00"


def test_calculate_discount_percentage_valid():
    """Test valid discount percentage calculation."""
    original_price = 100.0
    current_price = 75.0
    result = calculate_discount_percentage(original_price, current_price)
    assert result == 25.0


def test_calculate_discount_percentage_invalid():
    """Test discount calculation with invalid original price."""
    original_price = 0
    current_price = 50.0
    result = calculate_discount_percentage(original_price, current_price)
    assert result == 0.0


@patch("load.logging.error")
def test_insert_price_change_failure(mock_log_error):
    """Test price change insertion failure."""
    mock_conn = MagicMock()
    mock_conn.cursor.side_effect = Exception("Insertion error")
    try:
        insert_price_change(mock_conn, product_id=1,
                            price=50.0, timestamp="2024-11-09T18:00:00")
    except Exception:
        pass
    mock_log_error.assert_called_once_with(
        "Error inserting price change: Insertion error")


@patch("load.logging.error")
def test_update_subscription_discount_failure(mock_log_error):
    """Test subscription discount update failure."""
    mock_conn = MagicMock()
    mock_conn.cursor.side_effect = Exception("Update error")
    try:
        update_subscription_discount(
            mock_conn, product_id=1, discount_percentage=20.0)
    except Exception:
        pass
    mock_log_error.assert_called_once_with(
        "Error updating subscription discount: Update error")
