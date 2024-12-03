"""Establishes connection to RDS database"""
from os import environ
import logging
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv


def configure_logging() -> None:
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_connection():
    """Connect to RDS database"""
    try:
        connection = psycopg2.connect(
            user=environ["DB_USER"],
            password=environ["DB_PASSWORD"],
            host=environ["DB_HOST"],
            port=environ["DB_PORT"],
            database=environ["DB_NAME"]
        )
        print("Connected to RDS database")
        return connection
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        raise


def get_cursor(connection):
    """Returns cursor"""
    try:
        return connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    except psycopg2.Error as e:
        print("Error creating cursor:", e)
        raise


if __name__ == "__main__":

    load_dotenv()

    conn = get_connection()
    get_cursor(conn)
