import streamlit as st
import requests
from constants import ROLES_LIST, BACKEND_URL
from pages.login import controller


def show_profile_page():
    user = st.session_state.get("current_user")
    if not user:
        st.warning("Пожалуйста, войдите в систему.")
        return

    if "is_editing" not in st.session_state:
        st.session_state.is_editing = False

    if st.session_state.is_editing:
        render_edit_form(user)
    else:
        render_profile_view(user)


def render_profile_view(user):
    col_name, col_btns = st.columns([3, 1])
    with col_name:
        st.header(f"{user.get('last_name')} {user.get('first_name')}")

    with col_btns:
        if st.button("Изменить", use_container_width=True):
            st.session_state.is_editing = True
            st.rerun()

        if st.button("Выйти", use_container_width=True, key="logout_btn"):
            try:
                if controller.get('user_id'):
                    controller.remove('user_id', path='/')
            except Exception:
                pass

            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.page = "main"
            st.rerun()

        st.markdown("""
            <style>
            div[data-testid="stButton"] button:has(div:contains("Выйти")) {
                background-color: #ff4b4b !important;
                color: white !important;
            }
            </style>
        """, unsafe_allow_html=True)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Контактная информация**")
        contacts = user.get('contacts', [])
        st.write(f"Телефон: `{contacts[0] if contacts else 'Не указан'}`")
        st.write(f"Категория: `{user.get('category', 'Студент')}`")

    with c2:
        st.write("**Профессиональные роли**")
        for r in user.get('roles', []):
            st.info(r)

    st.divider()
    st.write("**Описание**")
    st.write(user.get('desc') or "Описание отсутствует.")


def render_edit_form(user):
    st.subheader("Редактирование профиля")
    with st.form("profile_edit_form"):
        new_desc = st.text_area("О себе", value=user.get('desc', ""))
        new_roles = st.multiselect("Ваши роли", ROLES_LIST, default=user.get('roles', []))
        new_ln = st.text_input("Фамилия", value=user.get('last_name'))
        new_fn = st.text_input("Имя", value=user.get('first_name'))

        if st.form_submit_button("Сохранить", type="primary"):
            payload = {
                "last_name": new_ln,
                "first_name": new_fn,
                "desc": new_desc,
                "roles": new_roles
            }
            res = requests.put(f"{BACKEND_URL}/users/{user['id']}", json=payload)
            if res.status_code == 200:
                st.session_state.current_user = res.json()
                st.session_state.is_editing = False
                st.success("Данные обновлены!")
                st.rerun()

    if st.button("Отмена"):
        st.session_state.is_editing = False
        st.rerun()