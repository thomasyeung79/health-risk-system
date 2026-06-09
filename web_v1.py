import streamlit as st
from datetime import datetime

from modules.ui import (
    apply_product_theme,
    is_authenticated,
    render_hero,
    render_feature_strip,
    render_journey_steps,
    render_module_card,
    render_nav,
    render_section_label,
    render_topbar,
)

# Try to initialize API client for backend connection
BACKEND_AVAILABLE = False
try:
    from api_client.client import ApiClient
    from api_client.auth_client import AuthClient as ApiAuthClient

    if "api_client" not in st.session_state:
        _client = ApiClient()
        st.session_state["api_client"] = _client
        st.session_state["api_auth_client"] = ApiAuthClient(_client)
        # Try connecting
        _health = _client.get("/health")
        if _health.get("status") == "ok":
            BACKEND_AVAILABLE = True
    else:
        BACKEND_AVAILABLE = True
except Exception:
    # Backend not available — will use legacy mode
    pass

# Restore tokens to API client from session state on page reload
if BACKEND_AVAILABLE and st.session_state.get("access_token"):
    client = st.session_state["api_client"]
    client.set_tokens(
        st.session_state["access_token"],
        st.session_state.get("refresh_token", ""),
    )

st.set_page_config(
    page_title="WellNest AI",
    page_icon="W",
    layout="wide"
)

apply_product_theme()

# Redirect authenticated users to dashboard
if st.session_state.get("authenticated"):
    st.switch_page("pages/0_Dashboard.py")

TEXT = {
    "English": {
        "title": "WellNest AI",
        "subtitle": "A bilingual wellness dashboard for daily health checks, emotional resets, habit history, and integrated AI reports.",
        "badge": "Personal wellness cockpit",
        "intro": "Start by choosing a language and entering your name. Your records stay connected across all modules.",
        "health_title": "Health Check",
        "health_desc": "Assess BMI, hydration, sleep, activity, diet, screen time, habits, and health risk.",
        "mind_title": "Mind Reset",
        "mind_desc": "Check mood, stress, energy, reflection topic, and receive structured emotional guidance.",
        "history_title": "Wellness History",
        "history_desc": "View saved health and emotional records over time.",
        "report_title": "Final Wellness Report",
        "report_desc": "Generate a combined physical and emotional wellness summary.",
        "open": "Open",
        "footer": "WellNest AI | Product demo v3.0",
        "name_input": "User name",
        "password_input": "Password",
        "confirm": "Start wellness session",
        "name_error": "Please enter your name first.",
        "password_error": "Username or password is incorrect.",
        "saved": "Signed in. You can now continue.",
        "logout": "Log out",
        "locked": "Sign in to unlock all modules.",
        "login_tab": "Sign in",
        "register_tab": "Create account",
        "create_account": "Create account",
        "confirm_password": "Confirm password",
        "register_success": "Account created. You can sign in now.",
        "user_exists": "This user already exists.",
        "password_short": "Password must be at least 6 characters.",
        "password_mismatch": "Passwords do not match.",
        "snapshot_label": "Today at a glance",
        "path_label": "Product flow",
        "modules_label": "Core modules",
        "features": [
            ("8", "health signals combined into one score"),
            ("2", "physical and emotional data tracks"),
            ("4", "guided steps from check-in to report"),
            ("AI", "coach-style reflection and summary")
        ],
        "journey": [
            ("1", "Register", "Create a private account with your name and password."),
            ("2", "Check health", "Log body, sleep, movement, diet, screen, and habit signals."),
            ("3", "Reset mind", "Record mood, stress, energy, and emotional context."),
            ("4", "Review report", "Use history and AI analysis to decide tomorrow's focus.")
        ]
    },
    "中文": {
        "title": "WellNest AI",
        "subtitle": "一个面向日常使用的双语健康产品，整合身体检测、情绪重整、历史追踪与 AI 综合报告。",
        "badge": "个人健康工作台",
        "intro": "先选择语言并输入姓名。之后你的健康记录、情绪记录和报告会自动关联到同一个用户。",
        "health_title": "健康检测",
        "health_desc": "评估 BMI、饮水、睡眠、运动、饮食、屏幕时间、生活习惯与健康风险。",
        "mind_title": "情绪重整",
        "mind_desc": "记录情绪、压力、能量状态，并获得结构化情绪引导。",
        "history_title": "历史记录",
        "history_desc": "查看健康与情绪记录的长期变化。",
        "report_title": "综合报告",
        "report_desc": "生成身体健康与情绪状态的综合 AI 报告。",
        "open": "进入",
        "footer": "WellNest AI | 产品演示 v3.0",
        "name_input": "用户姓名",
        "password_input": "密码",
        "confirm": "开始健康会话",
        "name_error": "请先输入姓名。",
        "password_error": "用户名或密码不正确。",
        "saved": "已登录，现在可以继续。",
        "logout": "退出登录",
        "locked": "登录后可使用全部模块。",
        "login_tab": "登录",
        "register_tab": "注册",
        "create_account": "创建账号",
        "confirm_password": "确认密码",
        "register_success": "账号已创建，现在可以登录。",
        "user_exists": "该用户已存在。",
        "password_short": "密码至少需要6位。",
        "password_mismatch": "两次输入的密码不一致。",
        "snapshot_label": "今日概览",
        "path_label": "产品流程",
        "modules_label": "核心模块",
        "features": [
            ("8", "类健康信号整合为一个评分"),
            ("2", "身体与情绪两条数据线"),
            ("4", "从检测到报告的完整步骤"),
            ("AI", "教练式反思与总结")
        ],
        "journey": [
            ("1", "注册", "用姓名和密码创建私密账号。"),
            ("2", "健康检测", "记录身体、睡眠、运动、饮食、屏幕和习惯信号。"),
            ("3", "情绪重整", "记录情绪、压力、能量和今天发生的事。"),
            ("4", "查看报告", "结合历史和 AI 分析，决定明天优先改善什么。")
        ]
    }
}

user_name = st.session_state.get("user_name", "")
language = st.session_state.get("language", "English")

top_col1, top_col2, _ = st.columns([1, 1, 2])

with top_col1:
    language = st.selectbox(
        "Language / 语言",
        ["English", "中文"],
        index=["English", "中文"].index(language)
    )

with top_col2:
    st.toggle(
        "Dark Mode" if language == "English" else "深色模式",
        value=st.session_state.get("dark_mode", False),
        key="dark_mode_toggle",
        help="Toggle dark mode" if language == "English" else "切换深色模式"
    )
    st.session_state["dark_mode"] = st.session_state["dark_mode_toggle"]

t = TEXT[language]

render_topbar(language, user_name)
render_nav(language, "web_v1.py")

st.session_state["language"] = language

render_hero(t["title"], t["subtitle"], t["intro"], t["badge"])

render_section_label(t["snapshot_label"])
render_feature_strip(t["features"])

render_section_label(t["path_label"])
render_journey_steps(t["journey"])

render_section_label("Workspace" if language == "English" else "工作台")

if not is_authenticated():
    st.info(t["locked"])

    if BACKEND_AVAILABLE:
        # New backend login flow
        login_tab, register_tab = st.tabs([t["login_tab"], t["register_tab"]])

        with login_tab:
            login_name = st.text_input(
                t["name_input"],
                value=user_name,
                key="login_user_name",
            )
            login_password = st.text_input(
                t["password_input"],
                type="password",
                key="login_password",
            )

            if st.button(t["confirm"], use_container_width=True, key="login_button"):
                if not login_name.strip():
                    st.error(t["name_error"])
                    st.stop()

                auth = st.session_state["api_auth_client"]
                try:
                    result = auth.login(login_name.strip(), login_password)
                    user = result["user"]
                    st.session_state["access_token"] = st.session_state["api_client"].access_token
                    st.session_state["refresh_token"] = st.session_state["api_client"].refresh_token
                    st.session_state["api_user"] = user
                    st.session_state["user_name"] = user["username"]
                    st.session_state["authenticated"] = True
                    st.session_state["session_start"] = datetime.now()
                    st.session_state["language"] = language
                    st.success(t["saved"])
                    st.rerun()
                except Exception:
                    st.error(t["password_error"])

        with register_tab:
            register_name = st.text_input(
                t["name_input"],
                key="register_user_name",
            )
            register_password = st.text_input(
                t["password_input"],
                type="password",
                key="register_password",
            )
            register_password_confirm = st.text_input(
                t["confirm_password"],
                type="password",
                key="register_password_confirm",
            )

            if st.button(t["create_account"], use_container_width=True, key="register_button"):
                if not register_name.strip():
                    st.error(t["name_error"])
                    st.stop()

                if len(register_password) < 6:
                    st.error(t["password_short"])
                    st.stop()

                if register_password != register_password_confirm:
                    st.error(t["password_mismatch"])
                    st.stop()

                auth = st.session_state["api_auth_client"]
                try:
                    auth.register(
                        username=register_name.strip(),
                        password=register_password,
                        display_name=register_name.strip(),
                        preferred_language=language,
                    )
                    st.success(t["register_success"])
                except Exception:
                    st.error(t["user_exists"])
    else:
        # Legacy fallback login (no backend available)
        st.warning(
            "⚠️ Backend server not detected. Using legacy local login."
            if language == "English"
            else "⚠️ 未检测到后端服务器，使用本地登录模式。"
        )
        from modules.ui import authenticate_user, register_user

        login_tab, register_tab = st.tabs([t["login_tab"], t["register_tab"]])

        with login_tab:
            login_name = st.text_input(
                t["name_input"],
                value=user_name,
                key="login_user_name_legacy",
            )
            login_password = st.text_input(
                t["password_input"],
                type="password",
                key="login_password_legacy",
            )

            if st.button(t["confirm"], use_container_width=True, key="login_button_legacy"):
                if not login_name.strip():
                    st.error(t["name_error"])
                    st.stop()

                if not authenticate_user(login_name, login_password):
                    st.error(t["password_error"])
                    st.stop()

                st.session_state["language"] = language
                st.session_state["user_name"] = login_name.strip()
                st.session_state["authenticated"] = True
                st.session_state["session_start"] = datetime.now()
                st.session_state["assessment_completed"] = True
                st.session_state["assessment_data"] = {
                    "user_name": login_name.strip(),
                    "language": language,
                }
                st.success(t["saved"])
                st.rerun()

        with register_tab:
            register_name = st.text_input(
                t["name_input"],
                key="register_user_name_legacy",
            )
            register_password = st.text_input(
                t["password_input"],
                type="password",
                key="register_password_legacy",
            )
            register_password_confirm = st.text_input(
                t["confirm_password"],
                type="password",
                key="register_password_confirm_legacy",
            )

            if st.button(t["create_account"], use_container_width=True, key="register_button_legacy"):
                if not register_name.strip():
                    st.error(t["name_error"])
                    st.stop()

                if len(register_password) < 6:
                    st.error(t["password_short"])
                    st.stop()

                if register_password != register_password_confirm:
                    st.error(t["password_mismatch"])
                    st.stop()

                if not register_user(register_name, register_password):
                    st.error(t["user_exists"])
                    st.stop()

                st.success(t["register_success"])
else:
    if st.button(t["logout"], use_container_width=True, key="main_logout"):
        st.session_state["confirm_logout"] = True

    if st.session_state.get("confirm_logout"):
        st.warning(
            "Are you sure you want to log out?" if language == "English" else "确认退出登录？"
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes" if language == "English" else "确认", use_container_width=True, key="confirm_logout_yes"):
                # Prefer API logout if available
                if BACKEND_AVAILABLE and st.session_state.get("api_refresh_token"):
                    try:
                        auth = st.session_state.get("api_auth_client")
                        if auth:
                            auth.logout()
                    except Exception:
                        pass
                st.session_state.pop("api_client", None)
                st.session_state.pop("api_auth_client", None)
                st.session_state.pop("access_token", None)
                st.session_state.pop("refresh_token", None)
                st.session_state.pop("api_user", None)
                for key in ["authenticated", "password_verified", "assessment_completed"]:
                    st.session_state.pop(key, None)
                st.session_state["confirm_logout"] = False
                st.rerun()
        with c2:
            if st.button("Cancel" if language == "English" else "取消", use_container_width=True, key="confirm_logout_no"):
                st.session_state["confirm_logout"] = False
                st.rerun()

st.divider()

render_section_label(t["modules_label"])

col1, col2 = st.columns(2)

with col1:
    render_module_card("HC", t["health_title"], t["health_desc"])

    if st.button(f"{t['open']} {t['health_title']}", use_container_width=True):
        if is_authenticated():
            st.switch_page("pages/1_Health_Check.py")
        else:
            st.warning(t["locked"])

with col2:
    render_module_card("MR", t["mind_title"], t["mind_desc"])

    if st.button(f"{t['open']} {t['mind_title']}", use_container_width=True):
        if is_authenticated():
            st.switch_page("pages/2_Mind_Reset.py")
        else:
            st.warning(t["locked"])

col3, col4 = st.columns(2)

with col3:
    render_module_card("WH", t["history_title"], t["history_desc"])

    if st.button(f"{t['open']} {t['history_title']}", use_container_width=True):
        if is_authenticated():
            st.switch_page("pages/3_Wellness_History.py")
        else:
            st.warning(t["locked"])

with col4:
    render_module_card("FR", t["report_title"], t["report_desc"])

    if st.button(f"{t['open']} {t['report_title']}", use_container_width=True):
        if is_authenticated():
            st.switch_page("pages/4_Final_Report.py")
        else:
            st.warning(t["locked"])

col5, col6 = st.columns(2)

with col5:
    render_module_card("DB", "Dashboard" if language == "English" else "看板",
                       "View your personalised wellness dashboard." if language == "English" else "查看个性化健康看板。")

    if st.button("Open Dashboard" if language == "English" else "打开看板", use_container_width=True):
        if is_authenticated():
            st.switch_page("pages/0_Dashboard.py")
        else:
            st.warning(t["locked"])

with col6:
    render_module_card("AI", "AI Coach" if language == "English" else "AI 教练",
                       "Chat with your AI wellness coach." if language == "English" else "与 AI 健康教练对话。")

    if st.button("Open AI Coach" if language == "English" else "打开 AI 教练", use_container_width=True):
        if is_authenticated():
            st.switch_page("pages/5_AI_Coach.py")
        else:
            st.warning(t["locked"])

st.divider()

st.caption(t["footer"])
