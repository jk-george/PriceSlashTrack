"""Unit Tests for connecting to database script"""
# pylint: skip-file
import pytest
from unittest.mock import patch, MagicMock
import psycopg2
from connect_to_database import get_connection, get_cursor


@patch("connect_to_database.psycopg2.connect")
@patch("connect_to_database.environ", {
    "DB_USER": "test_user",
    "DB_PASSWORD": "test_password",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "test_db"
})
def test_get_connection_valid(mock_connect):
    """Test valid database connection."""
    mock_connect.return_value = MagicMock()

    connection = get_connection()
    mock_connect.assert_called_once_with(
        user="test_user",
        password="test_password",
        host="localhost",
        port="5432",
        database="test_db"
    )
    assert connection is not None


@patch("connect_to_database.psycopg2.connect", side_effect=psycopg2.Error("Connection error"))
@patch("connect_to_database.environ", {
    "DB_USER": "test_user",
    "DB_PASSWORD": "test_password",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "test_db"
})
def test_get_connection_error_invalid(mock_connect):
    """Test invalid database connection raises error."""
    with pytest.raises(psycopg2.Error, match="Connection error"):
        get_connection()


def test_get_cursor_valid():
    """Test getting a cursor is valid."""
    mock_connection = MagicMock()
    cursor = get_cursor(mock_connection)
    mock_connection.cursor.assert_called_once_with(
        cursor_factory=psycopg2.extras.DictCursor)
    assert cursor is not None


def test_get_cursor_invalid():
    """Test invalid cursor creation raises error."""
    mock_connection = MagicMock()
    mock_connection.cursor.side_effect = psycopg2.Error("Cursor error")
    with pytest.raises(psycopg2.Error, match="Cursor error"):
        get_cursor(mock_connection)
