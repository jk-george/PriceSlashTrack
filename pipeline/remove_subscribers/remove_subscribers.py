"""Checks if any products no longer have users subscribed to them """
from psycopg2.extensions import connection
from dotenv import load_dotenv
from pipeline.connect_to_database import configure_logging, get_connection
"""
Query the product and subscription tables: Check each product_id in the product table to see if it has any corresponding rows in the subscription table.
Delete products without subscriptions for products with no active subscribers, remove their rows from the product table and any associated rows in price_changes.
"""


def check_subscription_schema(conn: connection):
    """Returns all of the product_ids from the subscription schema"""
    pass


def check_product_data(conn: connection):
    """returns all of the product_ids from """
    pass


def remove_unsubscribed_products():
    """returns all of the product_ids from """
    pass


if __name__ == "__main__":

    load_dotenv()
    connection = get_connection()
