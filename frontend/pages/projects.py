import streamlit as st
import requests
import time
from constants import ROLES_LIST, BACKEND_URL
from components.profileCard import render_profile_card


def show_projects_page(is_my=True):
    user = st.session_state.get("current_user")
    prefix = "my" if is_my else "feed"
    view_key = f"{prefix}_active_proj"
    search_key = f"view_search_{prefix}"

    if st.session_state.get(search_key):
        render_search_members_page(prefix)
        return

    if st.session_state.get(view_key):
        render_project_detail(is_my, prefix)
        return

    if is_my:
        c1, c2, c3 = st.columns([1, 2, 1])
        if c2.button("Создать новый проект", type="primary", use_container_width=True, key=f"{prefix}_create_main"):
            st.session_state.page = "create_project"
            st.rerun()

    try:
        res = requests.get(f"{BACKEND_URL}/projects/")
        if res.status_code == 200:
            all_projects = res.json()

            if is_my:
                projs = [
                    p for p in all_projects
                    if p['creator_id'] == user['id'] or any(m['id'] == user['id'] for m in p.get('members', []))
                ]
            else:
                projs = [
                    p for p in all_projects
                    if p['creator_id'] != user['id'] and not any(m['id'] == user['id'] for m in p.get('members', []))
                ]

            if not projs:
                st.info("Проектов пока нет")
                return

            for p in projs:
                with st.container(border=True):
                    c_title, c_status = st.columns([3, 1])
                    c_title.subheader(p['title'])

                    if is_my and p['creator_id'] == user['id']:
                        st.caption("Вы создатель")
                    elif is_my:
                        st.caption("Вы участник")

                    status = p.get('status', 'Поиск участников')
                    if status == "Поиск участников":
                        c_status.markdown(":green[● Поиск участников]")
                    else:
                        c_status.markdown(":red[● Набор завершен]")

                    if st.button("Открыть", key=f"open_{prefix}_{p['id']}", use_container_width=True):
                        st.session_state[view_key] = p
                        st.rerun()
    except Exception as e:
        st.error(f"Ошибка: {e}")


def render_project_detail(is_my, prefix):
    view_key = f"{prefix}_active_proj"
    search_key = f"view_search_{prefix}"
    p = st.session_state[view_key]
    user = st.session_state.current_user
    p_id = p['id']
    is_creator = (p['creator_id'] == user['id'])

    if st.button("Назад", key=f"back_detail_{prefix}_{p_id}"):
        st.session_state[view_key] = None
        st.rerun()

    st.title(p['title'])

    status = p.get('status', 'Поиск участников')
    is_member = any(m['id'] == user['id'] for m in p.get('members', []))

    if not is_my and not is_member and status == "Поиск участников":
        if st.button("Подать заявку в проект", type="primary", use_container_width=True, key=f"apply_{prefix}_{p_id}"):
            res = requests.post(f"{BACKEND_URL}/projects/{p_id}/apply?user_id={user['id']}")
            if res.status_code == 200:
                st.success("Заявка отправлена")
                time.sleep(0.5)
                st.rerun()

    tab_titles = ["Описание", "Команда"]
    if is_creator:
        tab_titles.append("Заявки")

    tabs = st.tabs(tab_titles)

    with tabs[0]:
        st.write(f"**Описание:** {p['desc']}")
        st.write(f"**Нужные роли:** {', '.join(p.get('req_roles', [])) or 'Команда собрана'}")

    with tabs[1]:
        col_h, col_add = st.columns([3, 1])
        col_h.subheader("Состав команды")
        if is_creator:
            if col_add.button("Добавить", use_container_width=True, key=f"add_mem_btn_{prefix}_{p_id}"):
                st.session_state[search_key] = p_id
                st.rerun()

        for m in p.get('members', []):
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{m['last_name']} {m['first_name']}**")
                c1.caption(f"Роль: {m.get('project_role', 'Участник')}")
                if is_creator and m['id'] != p['creator_id']:
                    if c2.button("Удалить", key=f"kick_{prefix}_{m['id']}_{p_id}"):
                        res = requests.delete(f"{BACKEND_URL}/projects/{p_id}/members/{m['id']}")
                        if res.status_code == 200:
                            st.warning(f"Пользователь {m['first_name']} удален из проекта")
                            time.sleep(1)
                            st.rerun()

    if is_creator:
        with tabs[2]:
            render_requests_section(p, prefix)


def render_requests_section(p, prefix):
    st.subheader("Входящие заявки")
    try:
        res = requests.get(f"{BACKEND_URL}/users/{st.session_state.current_user['id']}/notifications")
        if res.status_code == 200:
            notifs = [n for n in res.json() if n['project_title'] == p['title']]
            if not notifs:
                st.info("Новых заявок нет")
                return
            for r in notifs:
                with st.container(border=True):
                    st.markdown(f"### {r['user_name']}")
                    st.info(f"**Анкета:** {r.get('user_desc', 'Описание отсутствует')}")
                    role = st.selectbox("Назначить роль", ROLES_LIST, key=f"role_sel_{prefix}_{r['id']}")
                    c1, c2 = st.columns(2)
                    if c1.button("Принять", key=f"acc_{prefix}_{r['id']}", type="primary", use_container_width=True):
                        requests.post(f"{BACKEND_URL}/requests/{r['id']}/handle?accept=true&role={role}")
                        st.rerun()
                    if c2.button("Отклонить", key=f"rej_{prefix}_{r['id']}", use_container_width=True):
                        requests.post(f"{BACKEND_URL}/requests/{r['id']}/handle?accept=false")
                        st.rerun()
    except:
        st.error("Ошибка загрузки заявок")


def render_search_members_page(prefix):
    search_key = f"view_search_{prefix}"
    project_id = st.session_state[search_key]
    if st.button("Вернуться к проекту", key=f"back_to_p_{prefix}_{project_id}"):
        st.session_state[search_key] = None
        st.rerun()
    st.title("Рекомендованные участники")
    try:
        res = requests.get(f"{BACKEND_URL}/recommendations/{project_id}")
        if res.status_code == 200:
            users = res.json()
            for i, u_data in enumerate(users):
                render_profile_card(u_data, is_recommended=(i < 5), key_prefix=f"search_{prefix}")
    except:
        st.error("Ошибка рекомендаций")