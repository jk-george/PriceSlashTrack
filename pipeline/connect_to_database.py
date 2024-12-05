"""Establishes connection to RDS database"""
from os import environ
import logging
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor
from dotenv import load_dotenv


def configure_logging() -> None:
    """Configures logging in the terminal"""
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
        logging.error("Error connecting to the database: %s", e)
        raise


def get_cursor(conn: connection) -> DictCursor:
    """Returns cursor object"""
    try:
        return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    except psycopg2.Error as e:
        logging.error("Error creating cursor: %s", e)
        raise


if __name__ == "__main__":

    load_dotenv()
    configure_logging()

    connection = get_connection()
    get_cursor(connection)
