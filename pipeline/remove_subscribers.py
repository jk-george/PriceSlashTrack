"""Removing products data that no longer have active subscriptions in the RDS database."""
import logging
from datetime import datetime
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor
from dotenv import load_dotenv
from connect_to_database import configure_logging, get_connection


def get_product_ids_from_table(conn: connection, table_name: str, distinct: bool = False) -> set:
    """Returns a set of product IDs based on specified schema."""
    try:
        with conn.cursor() as cur:
            add_distinct = "DISTINCT" if distinct else ""
            query = f"""SELECT {add_distinct} product_id FROM {table_name};"""
            cur.execute(query)
            return {row[0] for row in cur.fetchall()}
    except Exception as e:
        logging.error(f"Error fetching from {table_name}: %s", e)
        return set()


def delete_from_table(cur: DictCursor, table_name: str, product_ids: list) -> None:
    """Deletes records from the RDS based on given schema name and product IDs."""
    query = f"""DELETE FROM {table_name} WHERE product_id = ANY(%s);"""
    cur.execute(query, (product_ids,))
    logging.info(f"Removed records from {table_name}: %s", product_ids)


def clean_websites(cur: DictCursor) -> None:
    """Removes websites not referenced in product table."""
    query = """DELETE FROM website
    WHERE website_id NOT IN (
        SELECT DISTINCT website_id
        FROM product);"""
    cur.execute(query)
    logging.info("Unused websites have been removed.")


def delete_unsubscribed_data(conn: connection, unsubscribed_product_ids: list) -> None:
    """Deletes data for unsubscribed products from price changes and product tables."""
    try:
        with conn.cursor() as cur:
            delete_from_table(cur, "price_changes", unsubscribed_product_ids)
            delete_from_table(cur, "product", unsubscribed_product_ids)
            clean_websites(cur)
        conn.commit()
    except Exception as e:
        conn.rollback()
        logging.error("Error deleting unsubscribed data: %s", e)


def main_remove_subscriptions() -> None:
    """Main function that removes unsubscribed products data."""
    with get_connection() as conn:
        active_subscriptions = get_product_ids_from_table(
            conn, "subscription", distinct=True)
        all_products = get_product_ids_from_table(
            conn, "product")
        unsubscribed_product_ids = list(all_products - active_subscriptions)

        if unsubscribed_product_ids:
            delete_unsubscribed_data(conn, unsubscribed_product_ids)
        else:
            logging.info("No unsubscribed products to remove.")

    logging.info("Connection to database successfully closed.")


def lambda_handler(event, context):
    """Lambda handler function """
    logging.info("Attempting to remove subscriptions at: ", datetime.now())
    try:
        main_remove_subscriptions()
        return {"status_code": 200, "message": "Successfully removed subscribers."}
    except:
        return {"status_code": 500, "message": "Execution of subscription removal process was not successful."}


if __name__ == "__main__":

    load_dotenv()
    configure_logging()
    main_remove_subscriptions()
