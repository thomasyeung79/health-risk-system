import base64
import hashlib
import html
import hmac
import json
import os
import secrets as py_secrets

import streamlit as st

from database import USERS_FILE


BRAND_NAME = {
    "English": "WellNest AI",
    "中文": "WellNest AI",
}


NAV_ITEMS = {
    "English": [
        ("Home", "web_v1.py"),
        ("Dashboard", "pages/0_Dashboard.py"),
        ("AI Coach", "pages/5_AI_Coach.py"),
        ("Health Check", "pages/1_Health_Check.py"),
        ("Mind Reset", "pages/2_Mind_Reset.py"),
        ("History", "pages/3_Wellness_History.py"),
        ("Final Report", "pages/4_Final_Report.py"),
    ],
    "中文": [
        ("首页", "web_v1.py"),
        ("看板", "pages/0_Dashboard.py"),
        ("AI 教练", "pages/5_AI_Coach.py"),
        ("健康检测", "pages/1_Health_Check.py"),
        ("情绪重整", "pages/2_Mind_Reset.py"),
        ("历史记录", "pages/3_Wellness_History.py"),
        ("综合报告", "pages/4_Final_Report.py"),
    ],
}




DISCLAIMER = {
    "English": "This self-assessment tool is for informational and educational purposes only. "
               "It does not provide medical diagnosis, treatment, or therapy. "
               "If you have health concerns, consult a qualified healthcare professional.",
    "中文": "本健康自评工具仅供信息参考和教育目的使用。"
           "它不提供医疗诊断、治疗或心理治疗。"
           "如有健康问题，请咨询合格的专业医疗人员。",
}


def get_disclaimer_text(language="English") -> str:
    """Return the localized disclaimer text without rendering.

    Args:
        language: "English" or "中文"

    Returns:
        The disclaimer string for the given language, falling back to English.
    """
    return DISCLAIMER.get(language, DISCLAIMER["English"])


def render_medical_disclaimer(language="English"):
    """Render a bilingual medical disclaimer panel via st.warning().

    Args:
        language: "English" or "中文"
    """
    text = get_disclaimer_text(language)
    st.warning(text)


def apply_product_theme():
    st.markdown(
        """
<style>
:root {
    --brand: #0f766e;
    --brand-strong: #115e59;
    --brand-soft: #ccfbf1;
    --aqua: #0f766e;
    --blue: #2563eb;
    --violet: #7c3aed;
    --rose: #e11d48;
    --amber: #d97706;
    --ink: #172026;
    --muted: #4A5568;
    --line: #d9e2e7;
    --panel: #ffffff;
    --canvas: #f5f8f7;
    --success: #15803d;
    --warning: #b45309;
    --danger: #b91c1c;
}


[data-testid="stSidebar"],
[data-testid="collapsedControl"],
#MainMenu,
footer,
header,
[data-testid="stToolbar"] {
    display: none;
    visibility: hidden;
}

.stApp {
    background:
        linear-gradient(135deg, rgba(15, 118, 110, 0.12), transparent 34%),
        linear-gradient(225deg, rgba(37, 99, 235, 0.10), transparent 32%),
        linear-gradient(180deg, #f8fbfa 0%, #eef5f3 48%, #f7f3f5 100%);
}

.block-container {
    max-width: 1180px;
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
}

h1, h2, h3 {
    color: var(--ink);
    letter-spacing: 0;
}

p, li, label, .stMarkdown, .stCaption {
    color: var(--ink);
}

div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 16px 18px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
}

div[data-testid="stMetric"] label {
    color: var(--muted);
}

.stButton > button {
    min-height: 44px;
    border-radius: 8px;
    border: 1px solid #0f766e;
    background: #0f766e;
    color: #ffffff;
    font-weight: 700;
}

.stButton > button:hover {
    border-color: #115e59;
    background: #115e59;
    color: #ffffff;
}

.stTextInput input,
.stNumberInput input,
div[data-baseweb="select"] > div,
textarea {
    border-radius: 8px;
}

.app-shell {
    background: rgba(255, 255, 255, 0.70);
    border: 1px solid rgba(217, 226, 231, 0.85);
    border-radius: 8px;
    padding: 18px;
    box-shadow: 0 18px 48px rgba(15, 23, 42, 0.07);
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    margin-bottom: 14px;
    padding: 12px 14px;
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid rgba(217, 226, 231, 0.85);
    border-radius: 8px;
    backdrop-filter: blur(12px);
}

.brand-lockup {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 850;
    color: var(--brand-strong);
    font-size: 19px;
}

.brand-mark {
    width: 34px;
    height: 34px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #0f766e;
    color: #ffffff;
    font-weight: 900;
}

.topbar-meta {
    color: var(--muted);
    font-size: 14px;
    text-align: right;
}

.hero-card {
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(238, 250, 247, 0.96) 54%, rgba(245, 243, 255, 0.96) 100%);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 34px;
    margin-bottom: 22px;
    box-shadow: 0 18px 44px rgba(15, 23, 42, 0.08);
}

.hero-card:before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 7px;
    background: linear-gradient(180deg, var(--aqua), var(--blue), var(--violet), var(--rose));
}

.hero-kicker {
    color: var(--brand-strong);
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.hero-title {
    color: var(--ink);
    font-size: 42px;
    line-height: 1.08;
    font-weight: 900;
    margin-bottom: 12px;
}

.hero-subtitle {
    color: var(--muted);
    font-size: 17px;
    line-height: 1.65;
    max-width: 760px;
}

.hero-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 20px;
    align-items: end;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(230, 255, 251, 0.92);
    color: var(--brand-strong);
    border: 1px solid #99f6e4;
    font-size: 13px;
    font-weight: 800;
    white-space: nowrap;
}

.module-card:focus-visible,
.product-card:focus-visible,
.hero-card:focus-visible,
.insight-panel:focus-visible,
.status-pill:focus-visible {
    outline: 2px solid var(--brand);
    outline-offset: 2px;
}

.module-card,
.product-card {
    position: relative;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 22px;
    min-height: 170px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
    transition: 160ms ease;
}

.module-card:before,
.product-card:before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--aqua), var(--blue), var(--violet), var(--rose));
}

.module-card {
    margin-bottom: 14px;
}

.module-icon {
    width: 38px;
    height: 38px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #e6fffb;
    color: var(--brand-strong);
    font-weight: 900;
    margin-bottom: 14px;
}

.module-card:hover,
.product-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 38px rgba(15, 23, 42, 0.08);
}

.module-title {
    color: var(--ink);
    font-size: 21px;
    font-weight: 850;
    margin-bottom: 8px;
}

.module-desc,
.card-copy {
    color: var(--muted);
    font-size: 15px;
    line-height: 1.65;
}

.section-label {
    color: var(--muted);
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 8px 0 12px;
}

.insight-panel {
    background: #ffffff;
    border: 1px solid var(--line);
    border-left: 5px solid var(--brand);
    border-radius: 8px;
    padding: 20px 22px;
    margin: 12px 0 18px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
}

.risk-panel {
    padding: 24px;
    border-radius: 8px;
    border: 1px solid var(--line);
    text-align: center;
    background: #ffffff;
}

.feature-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin: 14px 0 24px;
}

.feature-tile {
    background: rgba(255, 255, 255, 0.86);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 16px;
    min-height: 112px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.045);
}

.feature-tile strong {
    display: block;
    color: var(--ink);
    font-size: 22px;
    line-height: 1;
    margin-bottom: 8px;
}

.feature-tile span {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.45;
}

.feature-tile:nth-child(1) { border-top: 4px solid var(--aqua); }
.feature-tile:nth-child(2) { border-top: 4px solid var(--blue); }
.feature-tile:nth-child(3) { border-top: 4px solid var(--violet); }
.feature-tile:nth-child(4) { border-top: 4px solid var(--amber); }

.journey-panel {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin: 6px 0 22px;
}

.journey-step {
    background: rgba(23, 32, 38, 0.94);
    color: #ffffff;
    border-radius: 8px;
    padding: 16px;
    min-height: 118px;
}

.journey-step b {
    display: inline-flex;
    width: 28px;
    height: 28px;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.16);
    margin-bottom: 12px;
}

.journey-step strong {
    display: block;
    color: #ffffff;
    margin-bottom: 6px;
}

.journey-step span {
    color: rgba(255, 255, 255, 0.72);
    font-size: 13px;
    line-height: 1.45;
}

@media (max-width: 1024px) and (min-width: 761px) {
    .feature-strip,
    .journey-panel {
        grid-template-columns: repeat(2, 1fr);
    }
    .hero-title {
        font-size: 36px;
    }
}

@media (max-width: 760px) {
    .topbar,
    .hero-row {
        display: block;
    }

    .topbar-meta {
        text-align: left;
        margin-top: 8px;
    }

    .hero-card {
        padding: 22px;
    }

    .hero-title {
        font-size: 28px;
    }

    .status-pill {
        margin-top: 16px;
    }

    .feature-strip,
    .journey-panel {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .hero-title {
        font-size: 24px;
    }
    .hero-card {
        padding: 16px;
    }
    .module-card {
        min-height: 140px;
        padding: 16px;
    }
    .feature-tile {
        min-height: 90px;
        padding: 12px;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("dark_mode"):
        st.markdown(
            """
<style>
:root {
    --brand: #14b8a6;
    --brand-strong: #5eead4;
    --brand-soft: #134e4a;
    --aqua: #14b8a6;
    --blue: #60a5fa;
    --violet: #a78bfa;
    --rose: #fb7185;
    --amber: #fbbf24;
    --ink: #f1f5f9;
    --muted: #94a3b8;
    --line: #334155;
    --panel: #1e293b;
    --canvas: #0f172a;
    --success: #4ade80;
    --warning: #facc15;
    --danger: #f87171;
}
</style>
        """,
            unsafe_allow_html=True,
        )


def escape(value):
    return html.escape(str(value))



def normalize_username(username):
    return str(username).strip().lower()


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=2)


def hash_password(password, salt=None):
    salt_bytes = (
        base64.b64decode(salt.encode("utf-8"))
        if salt
        else py_secrets.token_bytes(16)
    )
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        str(password).encode("utf-8"),
        salt_bytes,
        120000,
    )
    return {
        "salt": base64.b64encode(salt_bytes).decode("utf-8"),
        "hash": base64.b64encode(digest).decode("utf-8"),
    }


def register_user(username, password):
    users = load_users()
    user_key = normalize_username(username)

    if user_key in users:
        return False

    password_record = hash_password(password)
    users[user_key] = {
        "display_name": str(username).strip(),
        "salt": password_record["salt"],
        "password_hash": password_record["hash"],
    }
    save_users(users)
    return True


def authenticate_user(username, password):
    users = load_users()
    user_key = normalize_username(username)
    user = users.get(user_key)

    if not user:
        return False

    password_record = hash_password(password, user.get("salt", ""))
    return hmac.compare_digest(
        password_record["hash"],
        user.get("password_hash", ""),
    )


def is_authenticated():
    if not st.session_state.get("authenticated"):
        return False
    session_start = st.session_state.get("session_start")
    if session_start:
        from datetime import datetime as dt
        elapsed = (dt.now() - session_start).total_seconds()
        if elapsed > 3600:  # 1 hour timeout
            logout()
            return False
    return True


def require_auth(language):
    if is_authenticated():
        return

    st.warning(
        "Please sign in from the homepage first."
        if language == "English"
        else "请先返回首页并输入密码登录。"
    )

    if st.button(
        "Back to Home" if language == "English" else "返回首页",
        key="auth_back_home",
    ):
        st.switch_page("web_v1.py")

    st.stop()


def require_user(language):
    """Check that a user_name exists in session state; redirect if not."""
    user_name = st.session_state.get("user_name")
    if user_name:
        return

    st.warning(
        "Please return to the homepage first."
        if language == "English"
        else "请先返回首页输入用户名。"
    )

    if st.button(
        "🏠 Back to Home" if language == "English" else "🏠 返回首页",
        key="no_user_back_home",
    ):
        st.switch_page("web_v1.py")

    st.stop()


def logout():
    for key in ["authenticated", "password_verified", "assessment_completed"]:
        st.session_state.pop(key, None)


def render_topbar(language, user_name=None):
    user_label = user_name if user_name else (
        "Guest" if language == "English" else "访客"
    )
    if is_authenticated():
        session_label = "Signed in as" if language == "English" else "当前用户"
    else:
        session_label = "Locked session for" if language == "English" else "未登录用户"

    dark_label = "🌙" if language == "English" else "🌙"
    st.markdown(
        f"""
<div class="topbar">
    <div class="brand-lockup">
        <span class="brand-mark">W</span>
        <span>{BRAND_NAME.get(language, BRAND_NAME["English"])}</span>
    </div>
    <div class="topbar-meta" style="display:flex;align-items:center;gap:12px;">
        <span>{session_label} <strong>{escape(user_label)}</strong></span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_nav(language, current_page):
    items = NAV_ITEMS.get(language, NAV_ITEMS["English"])
    cols = st.columns(len(items))
    for col, (label, page) in zip(cols, items):
        with col:
            button_label = label if page != current_page else f"{label} ·"
            if st.button(button_label, key=f"nav_{current_page}_{page}", use_container_width=True):
                if page != current_page:
                    st.switch_page(page)


def render_hero(title, subtitle, kicker=None, badge=None):
    kicker_html = f'<div class="hero-kicker">{escape(kicker)}</div>' if kicker else ""
    badge_html = f'<div class="status-pill">{escape(badge)}</div>' if badge else ""
    st.markdown(
        f"""
<div class="hero-card">
    <div class="hero-row">
        <div>
            {kicker_html}
            <div class="hero-title">{escape(title)}</div>
            <div class="hero-subtitle">{escape(subtitle)}</div>
        </div>
        {badge_html}
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_module_card(icon, title, description):
    st.markdown(
        f"""
<div class="module-card">
    <div class="module-icon">{escape(icon)}</div>
    <div class="module-title">{escape(title)}</div>
    <div class="module-desc">{escape(description)}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_strip(items):
    cards = "".join(
        f"""
<div class="feature-tile">
    <strong>{escape(value)}</strong>
    <span>{escape(label)}</span>
</div>
        """
        for value, label in items
    )
    st.markdown(f'<div class="feature-strip">{cards}</div>', unsafe_allow_html=True)


def render_journey_steps(items):
    cards = "".join(
        f"""
<div class="journey-step">
    <b>{index}</b>
    <strong>{escape(title)}</strong>
    <span>{escape(description)}</span>
</div>
        """
        for index, title, description in items
    )
    st.markdown(f'<div class="journey-panel">{cards}</div>', unsafe_allow_html=True)


def render_section_label(label):
    st.markdown(
        f'<div class="section-label">{escape(label)}</div>',
        unsafe_allow_html=True,
    )


def render_panel(title, body=None):
    body_html = f'<div class="card-copy">{escape(body)}</div>' if body else ""
    st.markdown(
        f"""
<div class="insight-panel">
    <h3>{escape(title)}</h3>
    {body_html}
</div>
        """,
        unsafe_allow_html=True,
    )
