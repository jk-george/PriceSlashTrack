"""Runs the streamlit dashboard"""

from datetime import timedelta
import pandas as pd
import altair as alt
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_card import card
from database_connection import (get_connection, get_cursor,
                                 insert_initial_price, insert_into_product,
                                 insert_into_subscription, insert_into_website,
                                 get_latest_price, get_product_info,
                                 create_account, get_user_id, get_product_subscription,
                                 stop_tracking_product, execute_database_select_query_fetchall)
from dashboard_etl import (get_html_from_url, get_website_from_url,
                           scrape_pricing_process, clean_price)


st.set_page_config(
    layout="wide"
)

header_section = st.container()
main_section = st.container()
login_section = st.container()
logout_section = st.container()
product_section = st.container()


def display_charts(product_id) -> alt.Chart:
    """Displays charts for a product"""
    if not product_id:
        st.warning("Please select a valid product.")
        return None

    query = """
    SELECT price, timestamp 
    FROM price_changes 
    WHERE product_id = %s
    ORDER BY timestamp
    """
    result = execute_database_select_query_fetchall(
        query, (product_id,), f"No price data available for Product ID {product_id}.")

    df = pd.DataFrame(result, columns=['Price', 'Date'])

    df['Date'] = pd.to_datetime(df['Date'], utc=True)

    current_time = pd.Timestamp.now(tz='UTC')
    time_ranges = {
        "Last 3 Days": timedelta(days=3),
        "Last 24 Hours": timedelta(hours=24),
        "Last 30 Minutes": timedelta(minutes=30),
    }

    time_range = st.selectbox(
        "Select Time Range", list(time_ranges.keys()))

    most_recent_timestamp = df['Date'].max()

    if time_range == "Last 30 Minutes" or time_range == "Last 24 Hours":
        filtered_df = df[df['Date'] >= (
            most_recent_timestamp - time_ranges[time_range])].copy()

        filtered_df.loc[:, 'FormattedDate'] = filtered_df['Date'].dt.strftime(
            '%H:%M')
    else:
        filtered_df = df[df["Date"] >= (
            current_time - time_ranges[time_range])].copy()

        filtered_df.loc[:, 'FormattedDate'] = filtered_df['Date'].dt.strftime(
            '%Y-%m-%d %H:%M:%S')

    if filtered_df.empty:
        st.warning("No price data available for the selected time range.")
        return None

    chart = alt.Chart(filtered_df).mark_line().encode(
        x=alt.X('FormattedDate:N',
                title='Timestamp',
                axis=alt.Axis(
                    labelAngle=-45,
                    tickCount=10
                )),
        y=alt.Y('Price:Q', title='Price'),
        tooltip=['Date:T', 'Price:Q']
    ).properties(
        width=500,
        height=400,
        title=f"Price Changes - {time_range}"
    )

    return chart


def login(email: str, password: str) -> bool:
    """Checks if email and password are in the database"""
    conn = get_connection()
    cursor = get_cursor(conn)
    try:
        query = """
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


def track_product(user_id, url, notification_price):
    """Inserts product details into the database"""
    website_id = insert_into_website(get_website_from_url(url))
    product_id = insert_into_product(website_id, url)
    insert_into_subscription(user_id, product_id, notification_price)
    price = (scrape_pricing_process(get_html_from_url(url), url)).get(
        "discount_price")
    insert_initial_price(clean_price(price), product_id)
    st.toast("New product successfully tracked!")


def show_about_page():
    """Displays the About page with project overview and instructions."""
    st.header("📖 About")
    st.markdown("""
    ### 🛒 **Welcome to Price Tracker!**

    Price Tracker is a tool designed to help you monitor the prices of your favorite products, track price changes over time, and get notified when prices drop below your desired threshold. 

    ### 🎯 Dashboard Features:
    - **Current Products**: View the products you are tracking, their current prices, and price trends over time.
    - **Track New Products**: Add a new product URL and set a price threshold to receive notifications about price drops.
    - **Unsubscribe From Product Tracking**: Manage your tracked products by unsubscribing from the ones you no longer wish to monitor.

    ### 🤝 How to Use:
    1. **Log In or Create an Account**:
        - If you are a returning user, log in with your email and password.
        - New users can create an account by providing their details.
    2. **Track a Product**:
        - Navigate to **Track New Products**.
        - Enter the product URL and set a notification price.
    3. **Monitor Your Products**:
        - Check **Current Products** to view the latest prices and trends.
    4. **Unsubscribe**:
        - Use **Unsubscribe From Product Tracking** to stop tracking products.

    We hope this tool makes it easier for you to save money and stay informed about the best deals!
    """)


def view_product(product_id, user_id):
    """Views product info"""
    with product_section:
        product_name, url, original_price, product_description, image_url = get_product_info(
            product_id)
        latest_price = get_latest_price(product_id)
        st.header(f"{product_name}")
        c1, c2 = st.columns(2)
        with c1:
            if image_url:
                st.container(height=1, border=False)
                st.image(image_url)
            if product_description:
                st.markdown(f"**Description:** {product_description}")
            st.markdown(f"""**Current price:** £{latest_price}""")
            st.markdown(f"""**Original price:** £{original_price}""")
            st.markdown(f"""[**Link to product**]({url})""")
        with c2:
            st.altair_chart(display_charts(product_id))
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(
            8, gap="small")
        with col1:
            if st.button("Back"):
                del st.session_state["current_product"]
                st.rerun()
        with col2:
            if st.button("Unsubscribe"):
                stop_tracking_product(user_id, product_id)
                st.toast(f"""You unsubscribed from tracking {product_name}""")


def get_user_name(user_id: int):
    """Returns the first and last name of the user from the database."""

    conn = get_connection()
    cursor = get_cursor(conn)
    cursor.execute(
        """
        SELECT first_name
        FROM users
        WHERE user_id = %s;
        """, (user_id,)
    )
    result = cursor.fetchone()
    if result:
        first_name = result[0]
        return first_name
    else:
        return None


def show_track_page():
    """Displays the new product tracking page"""
    user_id = st.session_state.get('user_id')
    st.session_state["Track new products"] = True
    st.header("Track a new product")
    url = st.text_input("Enter a new product URL: ")
    notification_price = st.text_input(
        label="Enter the price threshold to receive email notifications about price drops: ")
    st.button("Track", on_click=track_clicked,
              args=(user_id, url, notification_price))


def show_current_products_page():
    """Displays the current products"""
    user_id = st.session_state.get('user_id')
    user_name = get_user_name(user_id)

    if user_name:
        st.title(f"{user_name}'s Current Products")
    else:
        st.title("Current Products")
    product_subscriptions = get_product_subscription(user_id)
    if not product_subscriptions:
        st.markdown("You are not currently tracking anything!")
    else:
        cols = st.columns(3, gap="small")
        product_info = []
        for product_id in product_subscriptions:
            extracted_info = list(get_product_info(product_id))
            extracted_info.append(product_id[0])
            product_info.append(extracted_info)
        for i, product in enumerate(product_info):
            product_name = product[0]
            latest_price = get_latest_price(product[-1])
            image = product[4]
            with cols[i % 3]:
                card(

                    title=f"{product_name}",
                    text=f"""£{latest_price}""",
                    image=image,
                    styles={"card": {
                        "margin": "0px",
                        "padding": "0px",
                        "box-shadow": "0 0"
                    }, "div": {
                        "background": "#0000000"
                    }},
                    on_click=lambda: set_product(product[-1])
                )


def show_main_page():
    """Displays the main page on the dashboard"""
    with main_section:
        with st.sidebar:
            st.title("Price Slasher Sales Tracker")
            page = option_menu(
                menu_title="", options=["About", "Current products", "Track new products"], icons=["question-circle", "bag", "plus-lg"])
            st.button("Log Out", key="logout", on_click=logged_out_clicked)
        user_id = st.session_state.get('user_id')
        if "current_product" in st.session_state:
            view_product(st.session_state.current_product, user_id)
            return
        if page == "About":
            show_about_page()
        elif page == "Track new products":
            show_track_page()
        elif page == "Current products":
            show_current_products_page()


def set_product(product_id):
    """Changes session state to current product"""
    st.session_state["current_product"] = product_id
    st.rerun()


def logged_out_clicked() -> None:
    """Changes logged in state to false"""
    st.session_state['logged_in'] = False


def show_logout_page() -> None:
    """Displays logout page"""
    login_section.empty()
    with logout_section:
        st.button("Log Out", key="logout", on_click=logged_out_clicked)


def login_clicked(email, password) -> None:
    """Logins into account"""
    if login(email, password):
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = get_user_id(email)
        st.toast("Login successful!")
    else:
        st.session_state['logged_in'] = False
        st.error("Invalid user name or password")


def create_account_clicked(first_name, last_name, new_email, new_password) -> None:
    """Verifies new account details and changes logged in state"""
    if not first_name or not last_name or not new_email or not new_password:
        st.error("All fields are required to create an account.")
        st.session_state['logged_in'] = False
    elif create_account(first_name, last_name, new_email, new_password):
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = get_user_id(new_email)
        st.toast("Account successfully created!")
    else:
        st.session_state['logged_in'] = False
        st.error("Error occurred when creating account")


def track_clicked(user_id, url, notification_price) -> None:
    """Tracks product"""
    error_present = False
    if not url or not notification_price:
        st.error("All fields are required to track a product.")
        error_present = True
    elif not scrape_pricing_process(get_html_from_url(url), url):
        st.error("Cannot fetch data from that link.")
        error_present = True
    try:
        notification_price = float(notification_price)
        if notification_price <= 0:
            st.error("Notification price must be a positive number.")
            error_present = True
    except ValueError:
        st.error("Notification price must be a valid number.")
        error_present = True
    if error_present:
        return None
    else:
        track_product(user_id, url, notification_price)


def show_login_page() -> None:
    """Displays streamlit main page"""
    with login_section:
        if st.session_state['logged_in'] == False:

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

    with header_section:

        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False
            show_login_page()
        else:
            if st.session_state['logged_in']:
                show_main_page()
            else:
                show_login_page()
