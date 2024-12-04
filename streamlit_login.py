import streamlit as st

from streamlit_graphs import get_connection, get_cursor

headerSection = st.container()
mainSection = st.container()
loginSection = st.container()
logOutSection = st.container()


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
        st.error(f"Error inserting into the database: {e}")
        return False


def show_main_page():
    with mainSection:
        st.header("Track a new product")
        product = st.text_input("Enter a new product URL: ")
        notification_price = st.text_input(
            label="Enter the price threshold to receive email notifications about price drops: ")
        processingClicked = st.button("Start Processing", key="processing")
        if processingClicked:
            st.balloons()
        st.header("Current products")


def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False


def show_logout_page():
    loginSection.empty()
    with logOutSection:
        st.button("Log Out", key="logout", on_click=LoggedOut_Clicked)


def login_clicked(email, password):
    if login(email, password):
        st.session_state['loggedIn'] = True
    else:
        st.session_state['loggedIn'] = False
        st.error("Invalid user name or password")


def create_account_clicked(first_name, last_name, new_email, new_password):
    """Verifies new account details and changes logged in state"""
    if not first_name or not last_name or not new_email or not new_password:
        st.error("All fields are required to create an account.")
    if create_account(first_name, last_name, new_email, new_password):
        st.session_state['loggedIn'] = True
    else:
        st.session_state['loggedIn'] = False
        st.error("Error occurred when creating account")


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

# functions to add:

# when on homepage

# - inserts new users -

# when logged in

# - inserts new URLs
# - remove subscription
