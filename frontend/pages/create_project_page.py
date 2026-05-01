import streamlit as st
import requests
from constants import ROLES_LIST, BACKEND_URL


def show_create_form():
    st.markdown("<h2 style='text-align: center;'>Создание нового проекта</h2>", unsafe_allow_html=True)
    user = st.session_state.current_user

    with st.form("create_project_form"):
        title = st.text_input("Название проекта")
        desc = st.text_area("Описание")
        creator_role = st.selectbox("Ваша роль в проекте", ROLES_LIST)
        req_roles = st.multiselect("Кого ищем? (Если оставить пустым, статус будет 'Набор завершен')", ROLES_LIST)

        submitted = st.form_submit_button("Опубликовать проект", type="primary", use_container_width=True)

        if submitted:
            if not title or not desc:
                st.error("Заполните название и описание!")
                return

            payload = {
                "title": title,
                "desc": desc,
                "creator_id": user["id"],
                "creator_role": creator_role,
                "req_roles": req_roles
            }

            res = requests.post(f"{BACKEND_URL}/projects/", json=payload)
            if res.status_code == 200:
                st.success("Проект успешно создан!")
                st.session_state.page = "Мои проекты"
                st.rerun()
            else:
                st.error("Ошибка при создании.")

    if st.button("Назад"):
        st.session_state.page = "Мои проекты"
        st.rerun()