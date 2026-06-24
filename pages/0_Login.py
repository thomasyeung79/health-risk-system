"""Login and registration page using backend API."""

import streamlit as st
from datetime import datetime

from modules.ui import apply_product_theme, render_topbar

st.set_page_config(page_title="Sign In", page_icon="W", layout="wide")
apply_product_theme()

language = st.session_state.get("language", "English")

TEXT = {
    "English": {
        "title": "Sign In",
        "subtitle": "Sign in to continue your wellness session.",
        "login_tab": "Sign In",
        "register_tab": "Create Account",
        "username": "Username",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "display_name": "Display Name",
        "login_btn": "Sign In",
        "register_btn": "Create Account",
        "logging_in": "Signing in...",
        "registering": "Creating account...",
        "login_success": "Signed in successfully!",
        "register_success": "Account created! You can now sign in.",
        "error_generic": "Something went wrong.",
        "error_connection": "Account services are currently running in local mode. Please return to Home and sign in there.",
        "error_auth": "Invalid username or password.",
        "error_exists": "Username already exists.",
        "password_short": "Password must be at least 6 characters.",
        "password_mismatch": "Passwords do not match.",
        "back_home": "Back to Home",
        "footer": "WellNest AI | Account Access",
    },
    "中文": {
        "title": "登录",
        "subtitle": "登录后继续你的健康会话。",
        "login_tab": "登录",
        "register_tab": "创建账号",
        "username": "用户名",
        "password": "密码",
        "confirm_password": "确认密码",
        "display_name": "显示名称",
        "login_btn": "登录",
        "register_btn": "创建账号",
        "logging_in": "正在登录...",
        "registering": "正在创建账号...",
        "login_success": "登录成功！",
        "register_success": "账号已创建！现在可以登录。",
        "error_generic": "发生错误。",
        "error_connection": "当前账号服务正在使用本地模式。请返回首页进行登录。",
        "error_auth": "用户名或密码不正确。",
        "error_exists": "该用户已存在。",
        "password_short": "密码至少需要6位。",
        "password_mismatch": "两次输入的密码不一致。",
        "back_home": "返回首页",
        "footer": "WellNest AI | 账号入口",
    },
}

t = TEXT[language]
user_name = st.session_state.get("user_name", "")

render_topbar(language, user_name)

st.title(t["title"])
st.markdown(t["subtitle"])

# Initialize API client if not present
if "api_client" not in st.session_state:
    try:
        from api_client.client import ApiClient
        from api_client.auth_client import AuthClient
        client = ApiClient()
        st.session_state["api_client"] = client
        st.session_state["auth_client"] = AuthClient(client)
    except Exception:
        st.info(t["error_connection"])
        if st.button(t["back_home"], use_container_width=True, key="api_unavailable_home"):
            st.switch_page("web_v1.py")
        st.stop()

client = st.session_state["api_client"]
auth = st.session_state["auth_client"]

login_tab, register_tab = st.tabs([t["login_tab"], t["register_tab"]])

with login_tab:
    login_username = st.text_input(t["username"], key="login_username")
    login_password = st.text_input(t["password"], type="password", key="login_password")

    if st.button(t["login_btn"], use_container_width=True, key="login_btn"):
        if not login_username.strip():
            st.error("Please enter your username." if language == "English" else "请输入用户名。")
            st.stop()

        with st.spinner(t["logging_in"]):
            try:
                result = auth.login(login_username.strip(), login_password)
                user = result["user"]
                st.session_state["access_token"] = client.access_token
                st.session_state["refresh_token"] = client.refresh_token
                st.session_state["api_user"] = user
                st.session_state["user_name"] = user["username"]
                st.session_state["authenticated"] = True
                st.session_state["session_start"] = datetime.now()
                st.session_state["language"] = language
                st.success(t["login_success"])
                st.switch_page("web_v1.py")
            except Exception as e:
                err_str = str(e)
                if "401" in err_str or "Invalid" in err_str:
                    st.error(t["error_auth"])
                elif "ConnectionError" in err_str or "connection" in err_str.lower():
                    st.error(t["error_connection"])
                else:
                    st.error(f"{t['error_generic']} {err_str[:100]}")

with register_tab:
    reg_username = st.text_input(t["username"], key="reg_username")
    reg_display = st.text_input(t["display_name"], key="reg_display")
    reg_password = st.text_input(t["password"], type="password", key="reg_password")
    reg_confirm = st.text_input(t["confirm_password"], type="password", key="reg_confirm")

    if st.button(t["register_btn"], use_container_width=True, key="register_btn"):
        if not reg_username.strip():
            st.error("Please enter a username." if language == "English" else "请输入用户名。")
            st.stop()

        if len(reg_password) < 6:
            st.error(t["password_short"])
            st.stop()

        if reg_password != reg_confirm:
            st.error(t["password_mismatch"])
            st.stop()

        with st.spinner(t["registering"]):
            try:
                auth.register(
                    username=reg_username.strip(),
                    password=reg_password,
                    display_name=reg_display.strip() or reg_username.strip(),
                    preferred_language=language,
                )
                st.success(t["register_success"])
            except Exception as e:
                err_str = str(e)
                if "409" in err_str or "exists" in err_str.lower():
                    st.error(t["error_exists"])
                elif "ConnectionError" in err_str or "connection" in err_str.lower():
                    st.error(t["error_connection"])
                else:
                    st.error(f"{t['error_generic']} {err_str[:100]}")

st.markdown("---")
if st.button(t["back_home"]):
    st.switch_page("web_v1.py")

st.caption(t["footer"])
