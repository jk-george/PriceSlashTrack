"""Useful functions for connecting to the database."""

from datetime import datetime
import os
from dotenv import load_dotenv
import psycopg2
import streamlit as st
from dashboard_etl import (scrape_pricing_process,
                           clean_price,
                           get_html_from_url)

load_dotenv()


def get_connection():
    """Gets connection to the database"""
    try:
        connection = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"]
        )
        return connection
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


def get_cursor(conn):
    """Gets cursor to the database"""
    if conn:
        try:
            return conn.cursor()
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")
            return None
    return None


def execute_database_select_query_fetchall(query: str,
                                           var: tuple, error: str) -> list:
    """Executes database select query. Returns data as a list"""
    conn = get_connection()
    cursor = get_cursor(conn)
    cursor.execute(query, var)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    if not result:
        st.warning(error)
        return None
    return result


def execute_database_select_query_fetchone(query: str, var: tuple) -> list:
    """Executes database select query. Returns data as a list"""
    conn = get_connection()
    cursor = get_cursor(conn)
    cursor.execute(query, var)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def get_website_id(website: str) -> int:
    """Checks if website exists and returns website id"""
    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        query = "SELECT website_id FROM website WHERE website_name = %s"
        cursor.execute(query, (website,))
        result = cursor.fetchone()
        return result[0] if result else None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None


def get_user_id(email: str) -> int:
    """Checks if user exists and returns user_id"""
    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        query = "SELECT user_id FROM users WHERE email_address = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        return result[0] if result else None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None


def get_product_id(url: str) -> int:
    """Checks if product exists and returns product_id"""
    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        query = "SELECT product_id FROM product WHERE url = %s"
        cursor.execute(query, (url,))
        result = cursor.fetchone()
        return result[0] if result else None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None


def get_subscription_id(user_id: str, product_id: int) -> int:
    """Checks if subscription exists and returns subscription_id"""
    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        query = "SELECT subscription_id FROM subscription WHERE user_id = %s and product_id = %s"
        cursor.execute(query, (user_id, product_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None


def get_product_subscription(user_id) -> list:
    """Returns all product ids for a user"""
    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        query = "SELECT product_id FROM subscription WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        return result if result else None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None


def get_product_info(product_id) -> tuple:
    """Returns all product info"""
    conn = get_connection()
    cursor = get_cursor(conn)
    try:
        query = """SELECT product_name, url,
        original_price, product_description,
        image_url FROM product WHERE product_id = %s"""
        cursor.execute(query, (product_id,))
        return cursor.fetchone()
    except Exception as e:
        st.error(f"Error getting the latest price: {e}")
        return None


def get_latest_price(product_id) -> float:
    """Returns the latest price of a product"""
    conn = get_connection()
    cursor = get_cursor(conn)
    try:
        query = """SELECT price FROM price_changes WHERE product_id = %s
        AND timestamp = (SELECT MAX(timestamp) FROM price_changes WHERE product_id = %s)"""
        cursor.execute(query, (product_id, product_id,))
        return cursor.fetchone()[0]
    except Exception as e:
        st.error(f"Error getting the latest price: {e}")
        return None


def stop_tracking_product(user_id, product_id):
    """Unsubscribes user from a product"""
    conn = get_connection()
    cursor = get_cursor(conn)
    try:
        cursor.execute(
            """DELETE FROM subscription WHERE user_id = %s AND product_id = %s""", (user_id, product_id,))
        cursor.close()
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error unsubscribing from product tracking: {e}")


def create_account(first_name, last_name, new_email, new_password) -> bool:
    """Adds new user data to database"""
    conn = get_connection()
    cursor = get_cursor(conn)
    try:
        query = """INSERT INTO users (first_name, last_name, email_address, password)
        VALUES (%s, %s, %s, %s);"""
        cursor.execute(query, (first_name, last_name, new_email, new_password))
        cursor.close()
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error inserting into the database (users): {e}")
        return False


def insert_into_website(website: str) -> int:
    """Inserts new websites into the website table and returns the corresponding website id"""
    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        if get_website_id(website):
            return get_website_id(website)
        cursor.execute(
            "INSERT INTO website (website_name) VALUES (%s);", (website,))
        cursor.close()
        conn.commit()
        conn.close()
        return get_website_id(website)
    except Exception as e:
        st.error(f"Error inserting into the database (website): {e}")
        return None


def insert_into_product(website_id: int, url: str) -> int:
    """Inserts new products into the product table and returns the corresponding product id"""
    product_info = scrape_pricing_process(get_html_from_url(url), url)
    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        if get_product_id(url):
            return get_product_id(url)
        cursor.execute(
            """INSERT INTO product (product_name, url, website_id, original_price, image_url, product_description) VALUES (%s, %s, %s, %s, %s, %s);""",
            (product_info.get("game_title"), url, website_id,
             clean_price(product_info.get("original_price")), product_info.get("image_url"), product_info.get("product_description"),))
        cursor.close()
        conn.commit()
        conn.close()
        return get_product_id(url)
    except Exception as e:
        st.error(f"Error inserting into the database (product): {e}")
        return None


def insert_into_subscription(user_id, product_id, notification_price):
    """Inserts new subscriptions into the subscription table and returns the corresponding product id"""
    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        if get_subscription_id(user_id, product_id):
            return get_subscription_id(user_id, product_id)
        cursor.execute(
            """INSERT INTO subscription (user_id, product_id, notification_price) VALUES (%s, %s, %s);""",
            (user_id, product_id, notification_price,))
        cursor.close()
        conn.commit()
        conn.close()
        return get_subscription_id(user_id, product_id)
    except Exception as e:
        st.error(f"Error inserting into the database (subscription): {e}")
        return None


def insert_initial_price(price, product_id) -> None:
    """Inserts initial price data into the price_changes table"""
    conn = get_connection()
    cursor = get_cursor(conn)
    try:
        cursor.execute(
            """INSERT INTO price_changes (price, product_id, timestamp) VALUES (%s, %s, %s);""",
            (price, product_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        cursor.close()
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error inserting into the database (price_changes): {e}")


if __name__ == "__main__":
    print(get_connection())
