"""

Creating a home page to greet customers for our dashboard. 

"""
import streamlit as st


def home_page() -> None:
    """ Function that runs the whole home page. """
    initial_banner()
    st.container(height=2, border=False)
    # information_section()


def information_section():
    """Adding size to buttons"""
    st.markdown("""
    <style>
                
    .stButton>button {
    color: #30693e;
    border-radius: 10%;
    height: 5em;
    width: 10em;
                
    }
    </style>""", unsafe_allow_html=True)
    c = st.columns(7)
    with c[1]:
        st.button("Meet Us")
    with c[5]:
        st.button("Get Started!")


def initial_banner() -> None:
    """ Top Banner """
    page_bg_img = '''
    <style>
    [data-testid="stAppViewContainer"] {
    background-image: url("https://i.imgur.com/iN0Mejm.jpeg");
    background-size: cover;
    }

    [data-testid="stHeader"] {
    background-color: rgba(0, 0, 0, 0);
    }

    [data-testid="stVerticalBorderWrapper"] {
    background-image: url("https://cdn.corporatefinanceinstitute.com/assets/cash-ratio.jpg");
    background-size: cover;
    }

    .border-class {
        border: 2px solid #555
    }

    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

    st.markdown("""
                <head>
                <img src='https://i.imgur.com/7e0ou9L.png' class="border-class">
                </head>
                """,
                unsafe_allow_html=True)


if __name__ == "__main__":
    st.set_page_config(page_title="Price Slashers - Sales Tracker",
                       page_icon="💸", layout="wide")
    home_page()
