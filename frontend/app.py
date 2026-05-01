import streamlit as st
from streamlit_cookies_controller import CookieController

st.set_page_config(page_title="Collabrix", layout="wide", page_icon="💼")

if "cookie_controller" not in st.session_state:
    st.session_state.cookie_controller = CookieController()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "main"

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 30px; 
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 22px; 
        font-weight: 600;
        padding: 12px 30px;
    }
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

from pages import login, profile, projects, create_project_page


def main():
    if not st.session_state.logged_in:
        login.check_auth_cookies()

    if not st.session_state.logged_in:
        login.show_login_page()
    else:
        c1, c_logo, c2 = st.columns([2, 1, 2])
        with c_logo:
            st.image("assets/logo.svg", width=200)

        if st.session_state.page == "create_project":
            create_project_page.show_create_form()
        else:
            tabs = st.tabs(["Лента", "Мои проекты", "Профиль"])
            with tabs[0]:
                projects.show_projects_page(is_my=False)
            with tabs[1]:
                projects.show_projects_page(is_my=True)
            with tabs[2]:
                profile.show_profile_page()


if __name__ == "__main__":
    main()