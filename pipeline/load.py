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


def configure_logging() -> None:
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_connection() -> connection:
    """Returns connection object"""
    try:
        conn = psycopg2.connect(
            user=environ["DB_USER"],
            password=environ["DB_PASSWORD"],
            host=environ["DB_HOST"],
            port=environ["DB_PORT"],
            database=environ["DB_NAME"]
        )
        logging.info("Connected to the database successfully.")
        return conn
    except psycopg2.Error as e:
        logging.error(f"Error connecting to the database: {e}")
        raise


def get_cursor(conn: connection) -> DictCursor:
    """Returns cursor object"""
    try:
        return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    except psycopg2.Error as e:
        logging.error(f"Error creating cursor: {e}")
        raise


def calculate_discount_percentage(original_price: float, current_price: float) -> float:
    """Calculates the discount percentage for the subscription table"""
    if original_price <= 0:
        logging.warning(f"""Invalid original price: {
                        original_price}. Returning 0% discount.""")
        return 0.0
    return max(0, ((original_price - current_price) / original_price) * 100)


def get_current_timestamp() -> str:
    """Generates the current timestamp in UTC format"""
    return datetime.utcnow().isoformat()


def insert_price_change(conn: connection, product_id: int, price: float, timestamp: str) -> None:
    """Inserts a price change record into the price_changes table."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO price_changes (price, product_id, timestamp)
                VALUES (%s, %s, %s);
                """,
                (price, product_id, timestamp)
            )
        logging.info(f"Inserted price change for product_id {product_id}.")
    except Exception as e:
        logging.error(f"Error inserting price change: {e}")


def update_subscription_discount(conn: connection, product_id: int, discount_percentage: float) -> None:
    """Updates the discount percentage in the subscription table."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE subscription
                SET discount_percentage = %s
                WHERE product_id = %s;
                """,
                (discount_percentage, product_id)
            )
        logging.info(
            f"Updated subscription discount for product_id {product_id}.")
    except Exception as e:
        logging.error(f"Error updating subscription discount: {e}")


def load_price_changes(df: list[dict], conn: connection) -> None:
    """Loads cleaned data into the price_changes and subscription tables in the RDS database."""
    try:
        for product_data in df:
            product_id = product_data["product_id"]
            price = product_data["price"]

            with conn.cursor() as cur:
                cur.execute(
                    "SELECT original_price FROM product WHERE product_id = %s;",
                    (product_id,)
                )
                result = cur.fetchone()
                if not result:
                    logging.warning(
                        f"No original price found for product_id {product_id}.")
                    continue
                original_price = result[0]

            # Gets discount and current timestamp
            discount_percentage = calculate_discount_percentage(
                original_price, price)
            timestamp = get_current_timestamp()

            # Insert into price_changes and update subscription table
            insert_price_change(conn, product_id, price, timestamp)
            update_subscription_discount(conn, product_id, discount_percentage)

        conn.commit()
        logging.info("Data successfully loaded.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error loading data: {e}")


if __name__ == "__main__":

    load_dotenv()
    configure_logging()

    # fake data
    data = {
        "price": [49.99, 79.99],
        "product_id": [1, 2]
    }
    df_cleaned = pd.DataFrame(data)

    connection = get_connection()
    get_cursor(connection)
