"""Script to notify users via email when the price of a product drops below a certain threshold."""

from os import environ as ENV
import logging

import boto3
from boto3.exceptions import Boto3Error
from psycopg2.extensions import connection

from connect_to_database import configure_logging, get_connection, get_cursor


def get_ses_client() -> boto3.client:
    """Returns the boto3 SES client to send emails with."""

    aws_access_key = ENV.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = ENV.get("AWS_SECRET_ACCESS_KEY")
    from_email = ENV.get("FROM_EMAIL")

    if not aws_access_key or not aws_secret_access_key or not from_email:
        raise RuntimeError("Required environment variables for AWS or email are missing. "
                           "Ensure AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, and FROM_EMAIL are set.")

    return boto3.client("ses", region_name="eu-west-2",
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_access_key)


def get_subscriptions_and_products(conn: connection) -> list[tuple[int, float, str, str]]:
    """Returns all active subscriptions along with product and user details."""

    with get_cursor(conn) as cur:
        cur.execute("""
            SELECT s.product_id, s.notification_price, p.product_name, u.email_address, u.first_name, u.last_name
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
            SELECT price FROM price_changes WHERE product_id = %s
        """, (product_id,))
        result = cur.fetchone()

    return float(result["price"]) if result else None


def has_notification_been_sent(conn: connection, user_id: int, product_id: int, price: float) -> bool:
    """Checks if a notification has already been sent for a given user, product, and price."""

    with get_cursor(conn) as cur:
        cur.execute("""
            SELECT 1 FROM notifications_sent
            WHERE user_id = %s AND product_id = %s AND price = %s
        """, (user_id, product_id, price))
        result = cur.fetchone()
    return result is not None


def log_notification_sent(conn: connection, user_id: int, product_id: int, price: float) -> None:
    """Logs a sent notification in the notifications_sent table."""

    with get_cursor(conn) as cur:
        cur.execute("""
            INSERT INTO notifications_sent (user_id, product_id, price, timestamp)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, product_id, price))


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


def calculate_percentage_decrease(initial: float, final: float) -> float:
    """Calculates the percentage decrease between two numbers."""
    return round(((initial - final)/initial)*100)


def determine_if_increase_or_decrease(percentage: float) -> str:
    """Determines if percentage is increase"""
    if percentage > 0:
        return "decreased"
    else:
        return "increased"


def check_and_notify() -> None:
    """Checks product prices and notifies users via email if the price
    drops below their notification threshold."""

    with get_connection() as conn:
        subscriptions = get_subscriptions_and_products(conn)

        for product_id, notification_price, product_name, customer_email, first_name, last_name in subscriptions:
            current_price = get_current_product_price(conn, product_id)

            if current_price is None:
                logging.warning("Product %s with ID %s not found.",
                                product_name, product_id)
                continue

            percentage_change = calculate_percentage_decrease(
                notification_price, current_price)
            change_type = determine_if_increase_or_decrease(percentage_change)

            if current_price < notification_price:
                with get_cursor(conn) as cur:
                    cur.execute("""
                        SELECT user_id FROM users 
                        WHERE email_address = %s
                    """, (customer_email,))
                    user_result = cur.fetchone()

                if not user_result:
                    logging.warning(
                        "No user found for email %s", customer_email)
                    continue

                user_id = user_result['user_id']

                if has_notification_been_sent(conn, user_id, product_id, current_price):
                    logging.info("Notification already sent for user %s and product %s at price %s.",
                                 user_id, product_name, current_price)
                    continue

                subject = f"Price Drop Alert: {product_name}"
                body = (f"Dear {first_name} {last_name},\n\n"
                        f"The price for {product_name} has "
                        f"{change_type} by {abs(percentage_change)}%!\n"
                        "It is now"
                        f" £{current_price}, dropping below your threshold of "
                        f"£{notification_price}."
                        " Hurry before this sale ends!\n"
                        "Best wishes and happy shopping,\n"
                        "The Price Slashers Team.")

                send_email(customer_email, subject, body)

                logging.info("Notified %s about price drop for %s.",
                             customer_email, product_name)


if __name__ == "__main__":
    configure_logging()
    check_and_notify()
