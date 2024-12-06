# pylint: skip-file
import unittest
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from remove_subscribers import (get_active_subscriptions,
                                delete_unsubscribed_data, main_remove_subscriptions)


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


def test_get_active_subscriptions_success(mock_conn, mock_cursor):
    """Tests returns product ids from subscriptions schema is successfully ran."""
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1,), (2,), (3,)]

    result = get_active_subscriptions(mock_conn)

    assert result == {1, 2, 3}
    mock_cursor.execute.assert_called_once()


def test_get_active_subscriptions_error(mock_conn, mock_cursor):
    """Tests an error is raised and returns empty set if invalid."""
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Database error")

    result = get_active_subscriptions(mock_conn)

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
    """Tests main function for cleaning the product, price changes and websites schema sucessfully"""
    mock_conn.cursor.return_value = mock_cursor
    mock_get_connection.return_value.__enter__.return_value = mock_conn

    mock_cursor.fetchall.side_effect = [
        [(1,), (2,)],
        [(2,), (3,)],
        [(1,), (2,), (3,), (4,)]
    ]

    main_remove_subscriptions()
    mock_cursor.execute.assert_called()
