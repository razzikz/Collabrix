import streamlit as st
import requests
import time
from streamlit_cookies_controller import CookieController
from constants import ROLES_LIST, BACKEND_URL

controller = CookieController()

def restore_session_from_cookie(user_id):
    try:
        response = requests.get(f"{BACKEND_URL}/users/{user_id}")
        if response.status_code == 200:
            user_data = response.json()
            st.session_state.current_user = user_data
            st.session_state.logged_in = True
            return True
    except Exception as e:
        print(f"Ошибка восстановления сессии: {e}")
    return False

def check_auth_cookies():
    uid = controller.get('user_id')
    if uid and "current_user" not in st.session_state:
        try:
            res = requests.get(f"{BACKEND_URL}/users/{uid}", timeout=2)
            if res.status_code == 200:
                st.session_state.current_user = res.json()
                st.session_state.logged_in = True
                st.rerun()
        except Exception:
            pass

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

def show_login_page():
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    _, col, _ = st.columns([1, 2, 1])
    with col:
       st.image("assets/logo.svg", use_container_width=True)

    if st.session_state.auth_mode == "login":
        render_login_form()
    else:
        render_reg_form()

def render_login_form():
    st.header("Вход в аккаунт")
    login = st.text_input("Логин", key="l_f")
    password = st.text_input("Пароль", type="password", key="p_f")

    if st.button("Войти", type="primary", use_container_width=True):
        if not login or not password:
            st.error("Введите логин и пароль")
            return

        try:
            res = requests.post(f"{BACKEND_URL}/login/", json={"login": login, "password": password})
            if res.status_code == 200:
                user = res.json()
                st.session_state.current_user = user
                st.session_state.logged_in = True
                st.session_state.cookie_controller.set('user_id', str(user['id']), path='/')
                st.toast("Авторизация успешна")
                time.sleep(0.6)
                st.rerun()
            else:
                st.error("Неверный логин или пароль")
        except Exception as e:
            st.error(f"Ошибка подключения к серверу: {e}")

    st.write("---")
    if st.button("Регистрация", use_container_width=True):
        st.session_state.auth_mode = "reg"
        st.rerun()

def render_reg_form():
    st.header("Регистрация")
    with st.form("reg_form_standard"):
        l = st.text_input("Логин *")
        p = st.text_input("Пароль *", type="password")
        ln = st.text_input("Фамилия *")
        fn = st.text_input("Имя *")
        ph = st.text_input("Телефон *")
        r = st.multiselect("Роли *", ROLES_LIST)

        submit = st.form_submit_button("Зарегистрироваться", type="primary", use_container_width=True)
        if submit:
            if all([l, p, ln, fn, ph, r]):
                payload = {
                    "login": l, "password": p, "last_name": ln, "first_name": fn,
                    "category": "Студент", "roles": r, "contacts": [ph], "desc": ""
                }
                try:
                    res = requests.post(f"{BACKEND_URL}/register/", json=payload)
                    if res.status_code == 200:
                        st.success("Регистрация завершена. Теперь вы можете войти.")
                        time.sleep(1.2)
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error("Ошибка регистрации (возможно, логин занят)")
                except Exception as e:
                    st.error(f"Ошибка сервера: {e}")
            else:
                st.warning("Заполните все обязательные поля")

    if st.button("Назад к входу", use_container_width=True):
        st.session_state.auth_mode = "login"
        st.rerun()