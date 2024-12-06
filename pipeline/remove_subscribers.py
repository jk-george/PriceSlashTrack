"""Removing products data that no longer have active subscriptions in the RDS database."""
import logging
from psycopg2.extensions import connection
from dotenv import load_dotenv
from connect_to_database import configure_logging, get_connection


def get_active_subscriptions(conn: connection) -> set:
    """Returns all product_ids that have users subscribed to it from subscription schema."""
    try:
        with conn.cursor() as cur:
            cur.execute("""SELECT DISTINCT product_id FROM subscription;""")
            active_subscriptions = cur.fetchall()
        return {row[0] for row in active_subscriptions}
    except Exception as e:
        logging.error("Error fetching active subscriptions: %s", e)
        return set()


def get_all_products(conn: connection) -> set:
    """Returns all product_ids from product table."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT product_id FROM product;")
            return {row[0] for row in cur.fetchall()}
    except Exception as e:
        logging.error("Error fetching all products: %s", e)
        return set()


def delete_price_changes(cur, unsubscribed_product_ids: list) -> None:
    """Deletes price changes for unsubscribed products."""
    query = """DELETE FROM price_changes WHERE product_id = ANY(%s);"""

    cur.execute(query, (unsubscribed_product_ids,))
    logging.info("Removed price changes for products: %s",
                 unsubscribed_product_ids)


def delete_products(cur, unsubscribed_product_ids: list) -> None:
    """Deletes unsubscribed products from product table."""
    query = """DELETE FROM product WHERE product_id = ANY(%s);"""
    cur.execute(query, (unsubscribed_product_ids,))
    logging.info("Removed unsubscribed products: %s", unsubscribed_product_ids)


def clean_websites(cur) -> None:
    """Removes websites not referenced in product table."""
    query = """DELETE FROM website
    WHERE website_id NOT IN (
        SELECT DISTINCT website_id
        FROM product);"""
    cur.execute(query)
    logging.info("Unused websites have been removed.")


def delete_unsubscribed_data(conn: connection, unsubscribed_product_ids: list) -> None:
    """Deletes data for unsubscribed products from all relevant tables."""
    try:
        with conn.cursor() as cur:
            delete_price_changes(cur, unsubscribed_product_ids)
            delete_products(cur, unsubscribed_product_ids)
            clean_websites(cur)
        conn.commit()
    except Exception as e:
        conn.rollback()
        logging.error("Error deleting unsubscribed data: %s", e)


def main_remove_subscriptions() -> None:
    """Main function that removes unsubscribed products data."""
    with get_connection() as conn:
        active_subscriptions = get_active_subscriptions(conn)
        all_products = get_all_products(conn)
        unsubscribed_product_ids = list(all_products - active_subscriptions)

        if unsubscribed_product_ids:
            delete_unsubscribed_data(conn, unsubscribed_product_ids)
        else:
            logging.info("No unsubscribed products to remove.")

    logging.info("Connection to database successfully closed.")


if __name__ == "__main__":
    load_dotenv()
    configure_logging()
    main_remove_subscriptions()
