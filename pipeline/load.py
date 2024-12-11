"""Uploads current price data to the RDS database triggered every 3 minutes"""
import logging
from psycopg2.extensions import connection
from dotenv import load_dotenv
from connect_to_database import configure_logging, get_connection


def insert_price_change(conn: connection, product_id: int, price: float, timestamp: str) -> None:
    """Inserts values into price_changes schema"""

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO price_changes (price, product_id, timestamp)
            VALUES (%s, %s, %s);
            """,
            (price, product_id, timestamp)
        )
    logging.info("Inserted price for product_id %s", product_id)


def product_id_exists(conn: connection, product_id: int) -> bool:
    """Checks products table to see if product_id exists."""
    with conn.cursor() as db_cursor:
        db_cursor.execute(
            "SELECT * FROM product WHERE product_id = %s", (product_id,))
        if db_cursor.fetchone():
            return True
        return False


def load_price_changes(products_data: list[dict], conn: connection) -> None:
    """Loads cleaned price data into database."""
    successfully_inserted = 0

    for product in products_data:
        if not all(key in product for key in ["product_id", "price", "timestamp"]):
            logging.error("Invalid product values: %s", product)
            continue

        try:
            insert_price_change(
                conn,
                product["product_id"],
                product["price"],
                product["timestamp"]
            )
            successfully_inserted += 1
        except Exception as e:
            logging.error("Failed to insert product data: %s", product)
            continue

    try:
        if successfully_inserted > 0:
            conn.commit()
            logging.info(
                "Data loaded successfully. %s rows committed.", successfully_inserted)
        else:
            raise ValueError("No valid rows to commit.")
    except ValueError as commit_error:
        conn.rollback()
        logging.error("Load error during commit: %s", commit_error)


def main_load(cleaned_data: list[dict]) -> None:
    """Main function for loading price_changes values"""

    with get_connection() as connection:
        load_price_changes(cleaned_data, connection)

    logging.info("Connection to database successfully closed.")


if __name__ == "__main__":
    load_dotenv()
    configure_logging()
    main_load()
