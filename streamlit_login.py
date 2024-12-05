"""Runs the streamlit dashboard"""

import logging
import pandas as pd
import altair as alt
import streamlit as st
import requests
import psycopg2
from bs4 import BeautifulSoup
from streamlit_graphs import get_connection, get_cursor

headerSection = st.container()
mainSection = st.container()
loginSection = st.container()
logOutSection = st.container()


def get_html_from_url(web_page: str) -> bytes:
    """Gets the html content from a given URL"""
    try:
        html = requests.get(web_page, timeout=20)
    except requests.exceptions.MissingSchema:
        return "That URL does not exist."
    except requests.exceptions.ConnectionError:
        return "Cannot connect to that URL."
    if html.status_code > 299 or html.status_code < 200:
        return f"Error: {html.status_code}."
    return html.content


def get_website_from_url(url: str) -> str:
    """Gets a main website address from a given URL """
    website_url = url
    if ".com" in url:
        website_url = url.split(".com")[0] + ".com"
    elif ".co.uk" in url:
        website_url = url.split(".co.uk")[0] + ".co.uk"
    return website_url


def scrape_from_html(html_content: bytes, url: str) -> dict:
    """Scrapes from html to get a dictionary with the:
    - product_name
    - original_price
    - website
    """
    s = BeautifulSoup(html_content, 'html.parser')

    results = s.find(id="game_area_purchase")

    if not results:
        logging.error("Can't scrape that URL.")
        return None

    original_price = results.find_all(
        "div", class_="discount_original_price")[0]
    game_title = s.find(
        id="appHubAppName", class_="apphub_AppName")

    product_information = {"game_title": game_title.text,
                           "original_price": original_price.text,
                           "website": get_website_from_url(url)}

    return product_information


def clean_price(price_str: str) -> float:
    """Cleans current/discount price string to float"""
    try:
        cleaned_price = float(price_str.replace(
            "£", "").replace(",", "").strip())
        return cleaned_price if cleaned_price >= 0 else None
    except ValueError:
        return None


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


def get_product_subscription(user_id):
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


def get_product_info(product_id):
    """Returns all product info"""
    conn = get_connection()
    cursor = get_cursor(conn)
    try:
        query = """SELECT product_name, url, original_price FROM product WHERE product_id = %s"""
        cursor.execute(query, (product_id,))
        return cursor.fetchone()
    except Exception as e:
        st.error(f"Error getting the latest price: {e}")
        return None


def get_latest_price(product_id):
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


def display_charts(product_id):
    """Displays charts for a product"""
    conn = get_connection()
    cursor = get_cursor(conn)
    query = """SELECT price, timestamp FROM price_changes WHERE product_id = %s"""
    cursor.execute(query, (product_id,))
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['Price', 'Date'])
    return alt.Chart(df).mark_line().encode(
        x='Date:T', y='Price:Q')


def login(email: str, password: str) -> bool:
    """Checks if email and password are in the database"""
    conn = get_connection()
    cursor = get_cursor(conn)
    try:
        query = f"""
        SELECT EXISTS (
            SELECT 1
            FROM users
            WHERE email_address = %s AND password = %s
        );
        """
        cursor.execute(query, (email, password))
        user = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        if user:
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Error querying the database: {e}")
        return False


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
        else:
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
    product_info = scrape_from_html(get_html_from_url(url), url)
    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        if get_product_id(url):
            return get_product_id(url)
        else:
            cursor.execute(
                """INSERT INTO product (product_name, url, website_id, original_price) VALUES (%s, %s, %s, %s);""",
                (product_info.get("game_title"), url, website_id,
                 clean_price(product_info.get("original_price")),))
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
        else:
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


def track_product(user_id, url, notification_price):
    """Inserts product details into the database"""
    website_id = insert_into_website(get_website_from_url(url))
    product_id = insert_into_product(website_id, url)
    insert_into_subscription(user_id, product_id, notification_price)
    st.toast("New product successfully tracked!")


def show_main_page():
    """Displays the main page on the dashboard"""
    with mainSection:
        user_id = st.session_state.get('user_id')
        st.header("Track a new product")
        url = st.text_input("Enter a new product URL: ")
        notification_price = st.text_input(
            label="Enter the price threshold to receive email notifications about price drops: ")
        st.button("Track", on_click=track_clicked,
                  args=(user_id, url, notification_price))
        st.header("Current products")
        for product_id in get_product_subscription(user_id):
            product_name, url, original_price = get_product_info(product_id)
            latest_price = get_latest_price(product_id)
            st.subheader(f"{product_name}")
            st.markdown(f"""Current price: £{latest_price}""")
            st.markdown(f"""Original price: £{original_price}""")
            st.markdown(f"""Link: {url}""")
            st.altair_chart(display_charts(product_id))


def LoggedOut_Clicked():
    """Changes logged in state to false"""
    st.session_state['loggedIn'] = False


def show_logout_page():
    """Displays logout page"""
    loginSection.empty()
    with logOutSection:
        st.button("Log Out", key="logout", on_click=LoggedOut_Clicked)


def login_clicked(email, password):
    if login(email, password):
        st.session_state['loggedIn'] = True
        st.session_state['user_id'] = get_user_id(email)
        st.toast("Login successful!")
    else:
        st.session_state['loggedIn'] = False
        st.error("Invalid user name or password")


def create_account_clicked(first_name, last_name, new_email, new_password):
    """Verifies new account details and changes logged in state"""
    if not first_name or not last_name or not new_email or not new_password:
        st.error("All fields are required to create an account.")
        st.session_state['loggedIn'] = False
    elif create_account(first_name, last_name, new_email, new_password):
        st.session_state['loggedIn'] = True
        st.session_state['user_id'] = get_user_id(new_email)
        st.toast("Account successfully created!")
    else:
        st.session_state['loggedIn'] = False
        st.error("Error occurred when creating account")


def track_clicked(user_id, url, notification_price):
    if not url or not notification_price:
        st.error("All fields are required to track a product.")
    else:
        track_product(user_id, url, notification_price)


def show_login_page():
    with loginSection:
        if st.session_state['loggedIn'] == False:

            # Login to an existing account

            st.header("Existing users")
            email = st.text_input(
                label="Email address", value="", placeholder="Enter your email address", key="1")
            password = st.text_input(
                label="Password", value="", placeholder="Enter password", type="password", key="2")
            st.button("Login", on_click=login_clicked,
                      args=(email, password))

            # Account creation

            st.header("Create an account")
            first_name = st.text_input(
                label="First name", placeholder="Enter your first name")
            last_name = st.text_input(
                label="Last name", placeholder="Enter your last name")
            new_email = st.text_input(
                label="Email address", placeholder="Enter your email address")
            new_password = st.text_input(
                label="Password", placeholder="Enter password", type="password")
            st.button("Create", on_click=create_account_clicked,
                      args=(first_name, last_name, new_email, new_password))


if __name__ == "__main__":
    with headerSection:
        st.title("Sales Tracker")

        if 'loggedIn' not in st.session_state:
            st.session_state['loggedIn'] = False
            show_login_page()
        else:
            if st.session_state['loggedIn']:
                show_logout_page()
                show_main_page()
            else:
                show_login_page()
