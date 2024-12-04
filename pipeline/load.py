"""Uploads current price data to the RDS database triggered every 3 minutes"""
import pandas as pd
from os import environ
import logging
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor
from datetime import datetime
from dotenv import load_dotenv
from connect_to_database import get_connection, get_cursor


def configure_logging() -> None:
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


# def calculate_discount_percentage(original_price: float, current_price: float) -> float:
#     """Calculates the discount percentage for the subscription table"""
#     if original_price <= 0:
#         logging.warning(f"""Invalid original price: {
#                         original_price}. Returning 0% discount.""")
#         return 0.0
#     return max(0, ((original_price - current_price) / original_price) * 100)


# def get_current_timestamp() -> str:
#     """Generates the current timestamp in UTC format"""
#     return datetime.utcnow().isoformat()

def insert_price_change(conn: connection, product_id: int, price: float, timestamp: str) -> None:
    """Inserts values into price_changes schema"""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO price_changes (price, product_id, timestamp)
                VALUES (%s, %s, %s);
                """,
                (price, product_id, timestamp)
            )
        logging.info(f"Inserted price for product_id {product_id}")
    except Exception as e:
        logging.error(f"Error inserting price: {e}")

# def update_subscription_discount(conn: connection, product_id: int, discount_percentage: float) -> None:
#     """Updates the discount percentage in the subscription table."""
#     try:
#         with conn.cursor() as cur:
#             cur.execute(
#                 """
#                 UPDATE subscription
#                 SET discount_percentage = %s
#                 WHERE product_id = %s;
#                 """,
#                 (discount_percentage, product_id)
#             )
#         logging.info(
#             f"Updated subscription discount for product_id {product_id}.")
#     except Exception as e:
#         logging.error(f"Error updating subscription discount: {e}")


# def load_price_changes(products_data: list[dict], conn: connection) -> None:
#     """Loads cleaned price data into database"""
#     try:
#         for product in products_data:
#             insert_price_change(
#                 conn,
#                 product["product_id"],
#                 product["price"],
#                 product["timestamp"]
#             )
#         conn.commit()
#         logging.info("Data loaded successfully")
#     except Exception as e:
#         conn.rollback()
#         logging.error(f"Load error: {e}")


def load_price_changes(products_data: list[dict], conn: connection) -> None:
    """Loads cleaned price data into database."""
    successfully_inserted = 0

    for product in products_data:
        try:
            insert_price_change(
                conn,
                product["product_id"],
                product["price"],
                product["timestamp"]
            )
            successfully_inserted += 1
        except Exception as e:
            logging.error(f"""Failed to insert product: {
                          product['product_id']}. Error: {e}""")

    try:
        if successfully_inserted > 0:
            conn.commit()
            logging.info(f"""Data loaded successfully. {
                         successfully_inserted}/{len(products_data)} rows committed.""")
        else:
            raise Exception("No valid rows to commit.")
    except Exception as commit_error:
        conn.rollback()
        logging.error(f"Load error during commit: {commit_error}")


if __name__ == "__main__":

    load_dotenv()
    configure_logging()

    connection = get_connection()
    cursor = get_cursor(connection)
    cleaned_data = [{'product_id': 8, 'timestamp': '2024-12-04 16:31:40'}, {'price': 7.69, 'product_id': 9,
                                                                            'timestamp': '2024-12-04 16:31:40'}, {'price': 129.99, 'product_id': 5, 'timestamp': '2024-12-04 16:31:40'}]

    load_price_changes(cleaned_data, connection)
    connection.close()
