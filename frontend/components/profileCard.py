import streamlit as st


def render_profile_card(user_data, is_recommended=False, key_prefix=""):
    with st.container(border=True):
        col_name, col_badge = st.columns([3, 1])

        with col_name:
            st.subheader(f"{user_data.get('last_name')} {user_data.get('first_name')}")

        if is_recommended:
            with col_badge:
                st.markdown(":orange[**РЕКОМЕНДОВАН**]")

        c1, c2 = st.columns(2)
        with c1:
            st.write("**Информация**")
            st.write(f"Категория: `{user_data.get('category', 'Студент')}`")

        with c2:
            st.write("**Роли**")
            for r in user_data.get('roles', []):
                st.info(r)

        st.divider()
        st.write("**Описание / Анкета**")
        st.write(user_data.get('desc') or "Описание отсутствует")

        if st.button("Пригласить в проект", key=f"{key_prefix}_inv_{user_data['id']}", use_container_width=True):
            st.toast(f"Приглашение отправлено пользователю {user_data['first_name']}")