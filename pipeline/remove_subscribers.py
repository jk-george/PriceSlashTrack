"""Removing products data that no longer have active subscriptions in the RDS database."""
import logging
from datetime import datetime, timedelta
from psycopg2.extensions import connection
from dotenv import load_dotenv
from connect_to_database import configure_logging, get_connection


def get_active_subscriptions(conn: connection) -> set:
    """Returns all product_ids that have users subscribed to it from subscription schema."""
    try:
        with conn.cursor() as cur:
            cur.execute("""SELECT DISTINCT product_id
                FROM subscription;""")
            active_subscriptions = cur.fetchall()
        print(f"1: {active_subscriptions}")
        return {row[0] for row in active_subscriptions}
    except Exception as e:
        logging.error("Error fetching active subscriptions: %s", e)
        return set()


def get_recent_products_data(conn: connection) -> set:
    """Returns all product_ids within the last 24 hours."""
    try:
        yesterday_timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") - timedelta(days=1)
        print(yesterday_timestamp)
        with conn.cursor() as cur:
            cur.execute("""SELECT DISTINCT product_id
                FROM price_changes
                WHERE timestamp >= %s;""",
                        (yesterday_timestamp,))
            recent_products = cur.fetchall()
        print(f"2: {recent_products}")
        return {row[0] for row in recent_products}
    except Exception as e:
        logging.error("Error fetching recent products: %s", e)
        return set()


def delete_unsubscribed_data(conn: connection, unsubscribed_product_ids: list) -> None:
    """Returns data for product and price changes schema for products with no active subscriptions."""
    try:
        with conn.cursor() as cur:
            cur.execute("""DELETE FROM price_changes
                WHERE product_id = ANY(%s);""",
                        (unsubscribed_product_ids,))
            logging.info("Removed price changes for products: %s",
                         unsubscribed_product_ids)

            cur.execute(
                """
                DELETE FROM product
                WHERE product_id = ANY(%s);
                """,
                (unsubscribed_product_ids,)
            )
            logging.info("Removed unsubscribed products: %s",
                         unsubscribed_product_ids)

            cur.execute(
                """
                DELETE FROM website
                WHERE website_id NOT IN (SELECT DISTINCT website_id FROM product);
                """
            )
            logging.info("Cleaned up unused websites.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        logging.error("Error deleting unsubscribed data: %s", e)


def main_remove_subscriptions() -> None:
    """Main function that removes unsubscribed products data from product, price_changes and website schema."""
    with get_connection() as conn:
        active_subscriptions = get_active_subscriptions(conn)
        recent_products = get_recent_products_data(conn)
        print(f"3:active_subscriptions: {active_subscriptions}")
        print(f"4:recent_products: {recent_products}")

        with conn.cursor() as cur:
            cur.execute("SELECT product_id FROM product;")
            all_products = {row[0] for row in cur.fetchall()}

        valid_product_ids = active_subscriptions | recent_products
        unsubscribed_product_ids = list(all_products - valid_product_ids)

        if unsubscribed_product_ids:
            delete_unsubscribed_data(conn, unsubscribed_product_ids)
        else:
            logging.info("No unsubscribed products to remove.")

    logging.info("Connection to database successfully closed.")


if __name__ == "__main__":
    load_dotenv()
    configure_logging()
    main_remove_subscriptions()
