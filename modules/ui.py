import base64
import hashlib
import html
import hmac
import json
import os
import secrets as py_secrets

import streamlit as st
import streamlit.components.v1 as components

from database import USERS_FILE


BRAND_NAME = {
    "English": "WellNest AI",
    "中文": "WellNest AI",
}


NAV_ITEMS = {
    "English": [
        ("🏠 Dashboard", "pages/0_Dashboard.py"),
        ("👤 Health Assessment", "pages/1_Health_Check.py"),
        ("💭 Reflection", "pages/2_Mind_Reset.py"),
        ("📈 Wellness History", "pages/3_Wellness_History.py"),
        ("📋 Insights Report", "pages/4_Final_Report.py"),
        ("🤖 AI Coach", "pages/5_AI_Coach.py"),
        ("⚙ Administration", "pages/7_Admin.py"),
    ],
    "中文": [
        ("🏠 看板", "pages/0_Dashboard.py"),
        ("👤 健康评估", "pages/1_Health_Check.py"),
        ("💭 反思", "pages/2_Mind_Reset.py"),
        ("📈 健康历程", "pages/3_Wellness_History.py"),
        ("📋 洞察报告", "pages/4_Final_Report.py"),
        ("🤖 AI 教练", "pages/5_AI_Coach.py"),
        ("⚙ 管理", "pages/7_Admin.py"),
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

/* ── Design System Components ──────────────────────── */

.section-head {
    margin: 8px 0 16px;
}
.section-title {
    color: var(--ink);
    font-size: 24px;
    font-weight: 850;
    margin: 0;
}
.section-sub {
    color: var(--muted);
    font-size: 14px;
    margin-top: 4px;
}

/* Metric Card */
.metric-card {
    text-align: center;
    padding: 20px 16px;
    border-top: 4px solid var(--brand);
}
.metric-icon {
    font-size: 28px;
    margin-bottom: 8px;
}
.metric-label {
    color: var(--muted);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.metric-value {
    color: var(--ink);
    font-size: 32px;
    font-weight: 900;
    line-height: 1.1;
}
.metric-delta {
    display: inline-block;
    font-size: 13px;
    font-weight: 700;
    margin-top: 6px;
    padding: 2px 8px;
    border-radius: 999px;
}
.delta-up {
    color: #15803d;
    background: #dcfce7;
}
.delta-down {
    color: #b91c1c;
    background: #fee2e2;
}

/* Insight Card */
.insight-card {
    display: flex;
    gap: 14px;
    background: #ffffff;
    border: 1px solid var(--line);
    border-left: 5px solid var(--brand);
    border-radius: 8px;
    padding: 18px 20px;
    margin: 8px 0;
    box-shadow: 0 4px 16px rgba(15,23,42,0.04);
}
.insight-icon {
    font-size: 24px;
    flex-shrink: 0;
}
.insight-content strong {
    display: block;
    color: var(--ink);
    margin-bottom: 4px;
}
.insight-content p {
    color: var(--muted);
    font-size: 14px;
    margin: 0;
    line-height: 1.5;
}

/* Achievement Card */
.achievement-card {
    display: flex;
    gap: 14px;
    background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 16px 18px;
    margin: 6px 0;
}
.achievement-icon {
    font-size: 26px;
    flex-shrink: 0;
}
.achievement-body strong {
    color: #166534;
    display: block;
    margin-bottom: 2px;
}
.achievement-body p {
    color: #15803d;
    font-size: 13px;
    margin: 0;
}

/* Risk Badge */
.risk-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 800;
    white-space: nowrap;
}

/* Timeline */
.timeline-connector {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 32px;
}
.timeline-dot {
    width: 10px;
    height: 10px;
    border-radius: 999px;
    background: var(--brand);
    border: 2px solid #ccfbf1;
    flex-shrink: 0;
}
.timeline-line {
    width: 2px;
    flex: 1;
    background: linear-gradient(180deg, var(--brand) 0%, transparent 100%);
    min-height: 20px;
}
.timeline-item {
    display: flex;
    gap: 14px;
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 14px 16px;
    margin: 4px 0;
    transition: 120ms ease;
}
.timeline-item:hover {
    border-color: var(--brand);
    box-shadow: 0 4px 12px rgba(15,23,42,0.06);
}
.timeline-icon {
    font-size: 22px;
    flex-shrink: 0;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f0fdfa;
    border-radius: 8px;
}
.timeline-date {
    color: var(--muted);
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.timeline-title {
    color: var(--ink);
    font-weight: 750;
    font-size: 15px;
}
.timeline-desc {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.5;
}

/* Pattern Card */
.pattern-card {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 18px;
    margin: 8px 0;
}
.pattern-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.pattern-header strong {
    color: var(--ink);
    font-size: 15px;
}
.pattern-confidence {
    font-weight: 800;
    font-size: 15px;
}
.pattern-bar-bg {
    height: 6px;
    background: #e5e7eb;
    border-radius: 999px;
    margin-bottom: 10px;
    overflow: hidden;
}
.pattern-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.4s ease;
}
.pattern-evidence {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.5;
    margin-bottom: 6px;
}
.pattern-rec {
    color: var(--ink);
    font-size: 14px;
    font-weight: 600;
}

/* Coach Card */
.coach-card {
    background: linear-gradient(135deg, #f0f9ff, #f5f3ff);
    border: 1px solid #c7d2fe;
    border-radius: 8px;
    padding: 22px;
    margin: 8px 0;
}
.coach-date {
    color: var(--muted);
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 6px;
}
.coach-title {
    color: var(--ink);
    font-size: 20px;
    font-weight: 850;
    margin-bottom: 14px;
}
.coach-lines {
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.coach-line {
    font-size: 15px;
    line-height: 1.6;
    color: var(--ink);
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: 48px 24px;
    background: #ffffff;
    border: 2px dashed var(--line);
    border-radius: 8px;
    margin: 12px 0;
}
.empty-icon {
    font-size: 48px;
    margin-bottom: 12px;
}
.empty-title {
    color: var(--ink);
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 8px;
}
.empty-desc {
    color: var(--muted);
    font-size: 14px;
    max-width: 400px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Loading State */
.loading-state {
    text-align: center;
    padding: 40px;
    color: var(--muted);
}
.loading-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--line);
    border-top: 3px solid var(--brand);
    border-radius: 999px;
    animation: spin 0.8s linear infinite;
    margin: 0 auto 12px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text {
    font-size: 14px;
}

/* Error State */
.error-state {
    text-align: center;
    padding: 32px 24px;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    margin: 12px 0;
}
.error-icon {
    font-size: 36px;
    margin-bottom: 8px;
}
.error-title {
    color: #991b1b;
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 4px;
}
.error-message {
    color: #b91c1c;
    font-size: 14px;
}
.error-detail {
    color: var(--muted);
    font-size: 12px;
    margin-top: 6px;
}

/* Top nav tabs */
.product-nav .stButton button {
    background: transparent;
    border: none;
    color: var(--muted);
    font-weight: 600;
    font-size: 14px;
    min-height: 36px;
    padding: 4px 8px;
    border-radius: 6px;
}
.product-nav .stButton button:hover {
    background: var(--brand-soft);
    color: var(--brand-strong);
}

/* Workspace tabs */
.workspace-tab {
    padding: 4px 0;
}

/* Two-column insight grid */
.insight-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}
@media (max-width: 760px) {
    .insight-grid {
        grid-template-columns: 1fr;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )
    hide_developer_alerts()


def hide_developer_alerts():
    """Remove development-only backend guidance from the product UI."""
    components.html(
        """
<script>
(() => {
  const blockedTerms = [
    "Backend API is not available",
    "Using legacy local login",
    "For full backend features",
    "uvicorn app.main",
    "docker compose up",
    "Health check: http://localhost:8000/health",
    "后端 API 不可用",
    "无法连接到后端服务器"
  ];

  const hideMatches = () => {
    const doc = window.parent.document;
    const candidates = doc.querySelectorAll('[data-testid="stAlert"], .stAlert');
    candidates.forEach((node) => {
      const text = node.innerText || "";
      if (blockedTerms.some((term) => text.includes(term))) {
        node.style.display = "none";
        node.setAttribute("aria-hidden", "true");
      }
    });
  };

  hideMatches();
  const observer = new MutationObserver(hideMatches);
  observer.observe(window.parent.document.body, { childList: true, subtree: true });
})();
</script>
        """,
        height=0,
        width=0,
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


# ═══════════════════════════════════════════════════════════════════
# Design System — Product Components
# ═══════════════════════════════════════════════════════════════════

def render_section(title, subtitle=None):
    """Standard section header used across all pages."""
    sub = f'<div class="section-sub">{escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f"""
<div class="section-head">
    <h2 class="section-title">{escape(title)}</h2>
    {sub}
</div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(icon, label, value, delta=None, color=None):
    """Product metric card with optional delta indicator."""
    delta_html = ""
    if delta is not None:
        arrow = "↑" if delta >= 0 else "↓"
        delta_cls = "delta-up" if delta >= 0 else "delta-down"
        delta_html = f'<span class="metric-delta {delta_cls}">{arrow} {abs(delta)}%</span>'
    accent = color or "var(--brand)"
    st.markdown(
        f"""
<div class="product-card metric-card" style="border-top-color: {accent};">
    <div class="metric-icon">{icon}</div>
    <div class="metric-label">{escape(label)}</div>
    <div class="metric-value">{escape(str(value))}</div>
    {delta_html}
</div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_card(title, body, icon="💡", color="var(--brand)"):
    """Insight card with icon and gradient accent."""
    st.markdown(
        f"""
<div class="insight-card" style="border-left-color: {color};">
    <div class="insight-icon">{icon}</div>
    <div class="insight-content">
        <strong>{escape(title)}</strong>
        <p>{escape(body)}</p>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_achievement_card(title, body, icon="🏆"):
    """Achievement card for positive milestones."""
    st.markdown(
        f"""
<div class="achievement-card">
    <div class="achievement-icon">{icon}</div>
    <div class="achievement-body">
        <strong>{escape(title)}</strong>
        <p>{escape(body)}</p>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_risk_badge(level):
    """Coloured risk badge — Low/Medium/High with appropriate colours."""
    colors = {"Low": "#15803d", "Medium": "#b45309", "High": "#b91c1c"}
    if level in ("低",):
        level, colors["低"] = "Low", "#15803d"
    elif level in ("中",):
        level, colors["中"] = "Medium", "#b45309"
    elif level in ("高",):
        level, colors["高"] = "High", "#b91c1c"
    bg = colors.get(level, "#6b7280")
    return f'<span class="risk-badge" style="background:{bg}20;color:{bg};border:1px solid {bg}40;">{escape(level)}</span>'


def render_timeline_connector():
    """Vertical connector line between timeline items."""
    st.markdown(
        """
<div class="timeline-connector">
    <div class="timeline-dot"></div>
    <div class="timeline-line"></div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_timeline_item(icon, date, title, description, event_type="default"):
    """A single visual timeline entry with icon, date, and description."""
    st.markdown(
        f"""
<div class="timeline-item {event_type}">
    <div class="timeline-icon">{icon}</div>
    <div class="timeline-body">
        <div class="timeline-date">{escape(date[:10]) if date else ""}</div>
        <div class="timeline-title">{escape(title)}</div>
        <div class="timeline-desc">{escape(description[:200]) if description else ""}</div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_pattern_card(title, confidence, evidence, recommendation):
    """Pattern discovery result card with confidence meter."""
    pct = int(confidence * 100)
    bar_color = "#15803d" if confidence >= 0.7 else "#b45309" if confidence >= 0.4 else "#6b7280"
    st.markdown(
        f"""
<div class="pattern-card">
    <div class="pattern-header">
        <strong>{escape(title)}</strong>
        <span class="pattern-confidence" style="color:{bar_color};">{pct}%</span>
    </div>
    <div class="pattern-bar-bg">
        <div class="pattern-bar-fill" style="width:{pct}%;background:{bar_color};"></div>
    </div>
    <div class="pattern-evidence">{escape(evidence)}</div>
    <div class="pattern-rec">💡 {escape(recommendation)}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_coach_card(date, title, content_lines):
    """AI Coach daily message card."""
    lines_html = "".join(
        f'<div class="coach-line">{escape(line)}</div>'
        for line in content_lines
    )
    st.markdown(
        f"""
<div class="coach-card">
    <div class="coach-date">{escape(date)}</div>
    <div class="coach-title">{escape(title)}</div>
    <div class="coach-lines">{lines_html}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(icon, title, description, action_label=None, action_key=None):
    """Beautiful empty state with optional action button."""
    btn = ""
    if action_label and action_key:
        if st.button(action_label, key=action_key, use_container_width=True):
            return True
    st.markdown(
        f"""
<div class="empty-state">
    <div class="empty-icon">{icon}</div>
    <div class="empty-title">{escape(title)}</div>
    <div class="empty-desc">{escape(description)}</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    return False


def render_loading_state(message="Loading..."):
    """Standard loading placeholder."""
    st.markdown(
        f"""
<div class="loading-state">
    <div class="loading-spinner"></div>
    <div class="loading-text">{escape(message)}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_error_state(message, details=None):
    """Standard error state with optional details."""
    detail_html = f'<div class="error-detail">{escape(details)}</div>' if details else ""
    st.markdown(
        f"""
<div class="error-state">
    <div class="error-icon">⚠️</div>
    <div class="error-title">Something went wrong</div>
    <div class="error-message">{escape(message)}</div>
    {detail_html}
</div>
        """,
        unsafe_allow_html=True,
    )
