"""Script to notify users via email when the price of a product drops below a certain threshold."""

from os import environ as ENV
import logging

import boto3
from boto3.exceptions import Boto3Error
from psycopg2.extensions import connection

from connect_to_database import configure_logging, get_connection, get_cursor


def get_ses_client() -> boto3.client:
    """Returns the boto3 SES client to send emails with."""

    return boto3.client("ses", region_name="eu-west-2",
                        aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
                        aws_secret_access_key=ENV["AWS_ACCESS_SECRET_KEY"])


def get_subscriptions_and_products(conn: connection):
    """Returns all active subscriptions along with product and user details."""

    with get_cursor(conn) as cur:
        cur.execute("""
            SELECT s.product_id, s.notification_price, p.product_name, u.email_address
            FROM subscription s
            JOIN product p ON s.product_id = p.product_id
            JOIN users u ON s.user_id = u.user_id
        """)
        subscriptions = cur.fetchall()

    return subscriptions


def get_current_product_price(conn: connection, product_id: int) -> float:
    """Returns the current price of a specified product."""

    with get_cursor(conn) as cur:
        cur.execute("""
            SELECT original_price FROM product WHERE product_id = %s
        """, (product_id,))
        result = cur.fetchone()

    return float(result["original_price"]) if result else None


def send_email(to_address: str, subject: str, body: str) -> None:
    """Sends an email using SES."""

    ses_client = get_ses_client()

    try:
        response = ses_client.send_email(
            Source=ENV["FROM_EMAIL"],
            Destination={"ToAddresses": [to_address]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )
        logging.info(
            "Email sent to %s with status code %s.",
            to_address, response['ResponseMetadata']['HTTPStatusCode'])

    except Boto3Error as e:
        logging.error("Error sending email: %s", e)


def check_and_notify() -> None:
    """Checks product prices and notifies users via email if the price
    drops below their notification threshold."""

    with get_connection() as conn:
        subscriptions = get_subscriptions_and_products(conn)

        for subscription in subscriptions:
            product_id, notification_price, product_name, customer_email = subscription

            new_price = get_current_product_price(conn, product_id)

            if new_price is None:
                logging.warning("Product %s with ID %s not found.",
                                product_name, product_id)
                continue

            if new_price < notification_price:
                subject = f"Price Drop Alert: {product_name}"
                body = (f"The price for {product_name} has dropped below your threshold of "
                        f"{notification_price}! The current price is {new_price}. "
                        "Hurry before this sale ends!")

                send_email(customer_email, subject, body)

                logging.info("Notified %s about price drop for %s.",
                             customer_email, product_name)


if __name__ == "__main__":

    configure_logging()
    check_and_notify()
