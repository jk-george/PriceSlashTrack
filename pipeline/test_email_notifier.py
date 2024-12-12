"""Tests for email_notifier.py"""
# pylint: skip-file
from time import sleep
from unittest import mock
from unittest.mock import MagicMock, patch
import pytest
from boto3.exceptions import Boto3Error
from email_notifier import (
    get_ses_client,
    get_subscriptions_and_products,
    send_email,
    check_and_notify,
    has_notification_been_sent,
    log_notification_sent
)


def test_get_ses_client_missing_env_variables():
    """Test if an exception is raised when required environment variables are missing."""
    with mock.patch.dict("os.environ", {}, clear=True):
        with pytest.raises(RuntimeError, match="Required environment variables for AWS or email are missing"):
            get_ses_client()


def test_get_ses_client_success():
    """Test the successful creation of an SES client."""
    with mock.patch.dict("os.environ", {
        "AWS_ACCESS_KEY_ID": "fake_key_id",
        "AWS_SECRET_ACCESS_KEY": "fake_secret_key",
        "FROM_EMAIL": "test@example.com"
    }), mock.patch("boto3.client") as mock_boto_client:

        mock_ses_client = MagicMock()
        mock_boto_client.return_value = mock_ses_client
        ses_client = get_ses_client()

        assert ses_client is mock_ses_client
        mock_boto_client.assert_called_once_with(
            "ses", region_name="eu-west-2", aws_access_key_id="fake_key_id",
            aws_secret_access_key="fake_secret_key"
        )


def test_get_subscriptions_and_products():
    """Test the subscription retrieval logic."""

    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, 10.0, "Product A", "user@example.com")]

    with patch("email_notifier.get_cursor") as mock_get_cursor:
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        subscriptions = get_subscriptions_and_products(mock_connection)

    assert len(subscriptions) == 1
    assert subscriptions[0] == (1, 10.0, "Product A", "user@example.com")


def test_send_email_success():
    """Test sending an email using SES."""
    mock_ses_client = MagicMock()
    mock_ses_client.send_email.return_value = {
        "ResponseMetadata": {"HTTPStatusCode": 200}
    }

    with mock.patch.dict("os.environ", {
        "FROM_EMAIL": "test@example.com",
        "AWS_ACCESS_KEY_ID": "fake_key_id",
        "AWS_SECRET_ACCESS_KEY": "fake_secret_key"
    }), mock.patch("email_notifier.get_ses_client", return_value=mock_ses_client):
        send_email("user@example.com", "Subject", "Body")

    mock_ses_client.send_email.assert_called_once_with(
        Source="test@example.com",
        Destination={"ToAddresses": ["user@example.com"]},
        Message={
            "Subject": {"Data": "Subject"},
            "Body": {"Text": {"Data": "Body"}}
        }
    )


def test_send_email_failure():
    """Test error handling when sending an email fails."""
    mock_ses_client = mock.MagicMock()
    mock_ses_client.send_email.side_effect = Boto3Error("SES error")

    with mock.patch.dict("os.environ", {
        "FROM_EMAIL": "test@example.com",
        "AWS_ACCESS_KEY_ID": "fake_key_id",
        "AWS_SECRET_ACCESS_KEY": "fake_secret_key"
    }), mock.patch("email_notifier.get_ses_client", return_value=mock_ses_client), \
            mock.patch("email_notifier.logging.error") as mock_error:
        send_email("user@example.com", "Subject", "Body")
        sleep(0.1)

    mock_error.assert_called_once()


def test_check_and_notify_price_drop():
    """Test that a user is notified when the price drops below their threshold."""
    mock_cursor = MagicMock()
    mock_cursor.__enter__.return_value = mock_cursor
    mock_cursor.__exit__.return_value = None

    mock_connection = MagicMock()
    mock_connection.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        (1, 10.0, "Product A", "user@example.com", "John", "Doe")
    ]
    mock_cursor.fetchone.side_effect = [
        {"price": 5.0},
        {"user_id": 1}
    ]

    mock_ses_client = MagicMock()

    with mock.patch.dict("os.environ", {
        "FROM_EMAIL": "test@example.com",
        "AWS_ACCESS_KEY_ID": "fake_key_id",
        "AWS_SECRET_ACCESS_KEY": "fake_secret_key"
    }), mock.patch("email_notifier.get_connection", return_value=mock_connection), \
            mock.patch("email_notifier.get_ses_client", return_value=mock_ses_client), \
            mock.patch("email_notifier.has_notification_been_sent", return_value=False):

        check_and_notify()

    expected_subject = "Price Drop Alert: Product A"
    expected_body = (
        "Dear John Doe,\n\n"
        "The price for Product A has decreased by 50%!\n"
        "It is now £5.0, dropping below your threshold of £10.0. "
        "Hurry before this sale ends!\n"
        "Best wishes and happy shopping,\n"
        "The Price Slashers Team."
    )

    mock_ses_client.send_email.assert_called_once_with(
        Source="test@example.com",
        Destination={"ToAddresses": ["user@example.com"]},
        Message={
            "Subject": {"Data": expected_subject},
            "Body": {"Text": {"Data": expected_body}}
        }
    )


def test_check_and_notify_no_price_drop():
    """Test that no email is sent if the price doesn't drop below the threshold."""
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        (1, 10.0, "Product A", "user@example.com")]
    mock_cursor.fetchone.return_value = {
        "price": 15.0}

    mock_ses_client = MagicMock()

    with mock.patch.dict("os.environ", {
        "FROM_EMAIL": "test@example.com",
        "AWS_ACCESS_KEY_ID": "fake_key_id",
        "AWS_SECRET_ACCESS_KEY": "fake_secret_key"
    }), mock.patch("email_notifier.get_connection", return_value=mock_connection), \
            mock.patch("email_notifier.get_ses_client", return_value=mock_ses_client), \
            mock.patch("email_notifier.logging.info") as mock_info:
        check_and_notify()

    mock_ses_client.send_email.assert_not_called()


def test_has_notification_been_sent_true():
    """Test when a notification has been sent previously."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = {"exists": 1}

    with patch("email_notifier.get_cursor") as mock_get_cursor:
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = has_notification_been_sent(mock_connection, 1, 2, 9.99)

    assert result is True
    mock_cursor.execute.assert_called_once()


def test_has_notification_been_sent_false():
    """Test when no previous notification has been sent."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None

    with patch("email_notifier.get_cursor") as mock_get_cursor:
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = has_notification_been_sent(mock_connection, 1, 2, 9.99)

    assert result is False
    mock_cursor.execute.assert_called_once()


def test_log_notification_sent():
    """Test logging a sent notification."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    with patch("email_notifier.get_cursor") as mock_get_cursor:
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        log_notification_sent(mock_connection, 1, 2, 9.99)

    mock_cursor.execute.assert_called_once()
    mock_cursor.execute.assert_called_with(
        """
            INSERT INTO notifications_sent (user_id, product_id, price, timestamp)
            VALUES (%s, %s, %s, NOW())
        """,
        (1, 2, 9.99)
    )
