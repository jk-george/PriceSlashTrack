"""Uploads current price data to the RDS database triggered every 3 minutes"""
import logging
from psycopg2.extensions import connection
from dotenv import load_dotenv
from connect_to_database import get_connection


def configure_logging() -> None:
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


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
        logging.info("Inserted price for product_id %s", product_id)
    except Exception as e:
        logging.error("Error inserting price: %s", e)


def load_price_changes(products_data: list[dict], conn: connection) -> None:
    """Loads cleaned price data into database."""
    successfully_inserted = 0

    for product in products_data:
        try:
            if not all(key in product for key in ["product_id", "price", "timestamp"]):
                logging.error("Invalid product values: %s", product)
                continue

            insert_price_change(
                conn,
                product["product_id"],
                product["price"],
                product["timestamp"]
            )
            successfully_inserted += 1
        except Exception as e:
            logging.error(
                "Failed to insert product: %s. Error: %s", product, e)

    try:
        if successfully_inserted > 0:
            conn.commit()
            logging.info(
                "Data loaded successfully. %s rows committed.", successfully_inserted)
        else:
            raise Exception("No valid rows to commit.")
    except Exception as commit_error:
        conn.rollback()
        logging.error("Load error during commit: %s", commit_error)


def main_load():
    """Main function for loading price_changes values"""
    connection = get_connection()
    try:
        cleaned_data = [
            {"price": 22.49, "timestamp": "2024-12-04 16:31:40"},
            {"product_id": 9, "price": 7.69, "timestamp": "2024-12-04 16:31:40"},
            {"product_id": 5, "price": 129.99,
             "timestamp": "2024-12-04 16:31:40"}
        ]

        load_price_changes(cleaned_data, connection)
    finally:
        connection.close()
        logging.info("Connection to database closed.")


if __name__ == "__main__":
    load_dotenv()
    configure_logging()

    main_load()
