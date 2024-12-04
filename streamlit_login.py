import streamlit as st

headerSection = st.container()
mainSection = st.container()
loginSection = st.container()
logOutSection = st.container()


def login(userName: str, password: str) -> bool:
    if (userName is None):
        return False
    args = [userName, password, 0]
    result_args = execute_sql_query("CheckUser", args)
    return (result_args[2] == 1)


def execute_sql_query(query, args):
    global CNX
    if (CNX is None):
        config = ConfigParser()
        config. read("config.ini")
        _host = config.get('MySQL', 'host')
        _port = config.get('MySQL', 'port')
        _database = config.get('MySQL', 'database')
        _user = config.get('MySQL', 'user')
        _password = config.get('MySQL', 'password')
        CNX = mysql.connector.connect(host=_host, database=_database,
                                      user=_user, passwd=_password, port=_port)

    with CNX.cursor() as cur:
        return cur.callproc(query, args)


def show_main_page():
    with mainSection:
        dataFile = st.text_input("Enter your Test file name: ")
        Topics = st.text_input("Enter your Model Name: ")
        ModelVersion = st.text_input("Enter your Model Version: ")
        processingClicked = st.button("Start Processing", key="processing")
        if processingClicked:
            st.balloons()


def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False


def show_logout_page():
    loginSection.empty()
    with logOutSection:
        st.button("Log Out", key="logout", on_click=LoggedOut_Clicked)


def LoggedIn_Clicked(userName, password):
    if login(userName, password):
        st.session_state['loggedIn'] = True
    else:
        st.session_state['loggedIn'] = False
        st.error("Invalid user name or password")


def show_login_page():
    with loginSection:
        if st.session_state['loggedIn'] == False:
            userName = st.text_input(
                label="", value="", placeholder="Enter your user name")
            password = st.text_input(
                label="", value="", placeholder="Enter password", type="password")
            st.button("Login", on_click=LoggedIn_Clicked,
                      args=(userName, password))


if __name__ == "__main__":

    with headerSection:
        st.title("Streamlit Application")

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

# - inserts new users - add to

# when logged in

# - inserts new URLs
# - remove subscription
