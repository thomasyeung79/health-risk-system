"""User Dashboard — landing page after login showing wellness overview."""

from datetime import datetime

import streamlit as st

from modules.dashboard_insights import build_trend_insights
from modules.emotion_localization import localize_emotion
from modules.ui import (
    apply_product_theme,
    render_medical_disclaimer,
    render_section_label,
    render_topbar,
)

st.set_page_config(page_title="Dashboard", page_icon="W", layout="wide")
apply_product_theme()

language = st.session_state.get("language", "English")
user_name = st.session_state.get("user_name", "")

TEXT = {
    "English": {
        "welcome": "Welcome back",
        "welcome_new": "Welcome to WellNest AI",
        "subtitle": "Your personal wellness overview",
        "today": "Today",
        "no_data_title": "Let's get started!",
        "no_data_body": "Complete your first health check and emotion analysis to unlock your personalized wellness dashboard.",
        "start_health": "Start Health Check",
        "start_emotion": "Start Emotion Analysis",
        "health_snapshot": "Latest Health",
        "emotion_snapshot": "Latest Emotion",
        "no_health": "No health data yet.",
        "no_emotion": "No emotion data yet.",
        "health_score": "Health Score",
        "risk_level": "Risk Level",
        "risk_percent": "Risk %",
        "stress": "Stress",
        "energy": "Energy",
        "pattern": "Pattern",
        "last_check": "Last check",
        "last_analysis": "Last analysis",
        "trends": "Wellness Trends",
        "trend_health": "Health",
        "trend_stress": "Stress",
        "trend_energy": "Energy",
        "key_insights": "Key Insights",
        "no_insights": "Complete more assessments to unlock personalised insights.",
        "improving": "Improving",
        "stable": "Stable",
        "declining": "Declining",
        "insufficient": "Not enough data",
        "quick_actions": "Quick Actions",
        "health_check": "Health Check",
        "mind_reset": "Mind Reset",
        "history": "History",
        "final_report": "Final Report",
        "go": "Go",
        "logout": "Log out",
        "logout_yes": "Yes, log out",
        "logout_no": "Cancel",
        "footer": "WellNest AI | Dashboard",
    },
    "中文": {
        "welcome": "欢迎回来",
        "welcome_new": "欢迎来到 WellNest AI",
        "subtitle": "你的个人健康概览",
        "today": "今天",
        "no_data_title": "开始使用！",
        "no_data_body": "完成首次健康检测和情绪分析，解锁你的个性化健康看板。",
        "start_health": "开始健康检测",
        "start_emotion": "开始情绪分析",
        "health_snapshot": "最新健康",
        "emotion_snapshot": "最新情绪",
        "no_health": "暂无健康数据。",
        "no_emotion": "暂无情绪数据。",
        "health_score": "健康评分",
        "risk_level": "风险等级",
        "risk_percent": "风险比例",
        "stress": "压力",
        "energy": "能量",
        "pattern": "模式",
        "last_check": "最近检测",
        "last_analysis": "最近分析",
        "trends": "健康趋势",
        "trend_health": "健康",
        "trend_stress": "压力",
        "trend_energy": "能量",
        "key_insights": "关键洞察",
        "no_insights": "完成更多评估后可解锁个性化洞察。",
        "improving": "改善中",
        "stable": "稳定",
        "declining": "下降中",
        "insufficient": "数据不足",
        "quick_actions": "快捷操作",
        "health_check": "健康检测",
        "mind_reset": "情绪重整",
        "history": "历史记录",
        "final_report": "综合报告",
        "go": "进入",
        "logout": "退出登录",
        "logout_yes": "确认退出",
        "logout_no": "取消",
        "footer": "WellNest AI | 看板",
    },
}

if not language:
    language = "English"
t = TEXT.get(language, TEXT["English"])

render_topbar(language, user_name)

# ── Logout button ─────────────────────────────────
lc1, lc2 = st.columns([6, 1])
with lc2:
    if st.button(f"🚪 {t['logout']}", use_container_width=True, key="dash_logout"):
        st.session_state["confirm_dash_logout"] = True

if st.session_state.get("confirm_dash_logout"):
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button(t["logout_yes"], use_container_width=True, key="dash_logout_yes"):
            for key in ["access_token", "refresh_token", "api_user", "user_name", "authenticated"]:
                st.session_state.pop(key, None)
            st.session_state["confirm_dash_logout"] = False
            st.switch_page("web_v1.py")
    with c2:
        if st.button(t["logout_no"], use_container_width=True, key="dash_logout_no"):
            st.session_state["confirm_dash_logout"] = False
            st.rerun()

# ── API client init ────────────────────────────────
BACKEND_AVAILABLE = False
try:
    from api_client.client import ApiClient
    from api_client.health_client import HealthClient
    from api_client.emotion_client import EmotionClient
    from api_client.report_client import ReportClient
    from api_client.trend_client import TrendClient

    if "api_client" in st.session_state:
        _client = st.session_state["api_client"]
    else:
        _client = ApiClient()
        st.session_state["api_client"] = _client

    if st.session_state.get("access_token"):
        _client.set_tokens(
            st.session_state["access_token"],
            st.session_state.get("refresh_token", ""),
        )

    _health = _client.get("/health")
    if _health.get("status") == "ok" and _client.is_authenticated:
        BACKEND_AVAILABLE = True
        health_api = HealthClient(_client)
        emotion_api = EmotionClient(_client)
        trend_api = TrendClient(_client)
except Exception:
    pass

# ── Data loading ───────────────────────────────────
def load_dashboard_data():
    data = {
        "health": None,
        "emotion": None,
        "health_stats": None,
        "emotion_stats": None,
        "trends": None,
    }
    if not BACKEND_AVAILABLE:
        return data
    try:
        health_records = health_api.list_records(limit=1)
        items = health_records.get("items", [])
        if items:
            data["health"] = items[0]
        data["health_stats"] = health_api.stats()
    except Exception:
        pass
    try:
        emotion_records = emotion_api.list_records(limit=1)
        items = emotion_records.get("items", [])
        if items:
            data["emotion"] = items[0]
        data["emotion_stats"] = emotion_api.stats()
    except Exception:
        pass
    try:
        data["trends"] = trend_api.summary(days=7, language=language)
    except Exception:
        pass
    return data


data = load_dashboard_data()
has_health = data["health"] is not None
has_emotion = data["emotion"] is not None
has_data = has_health or has_emotion

# ══════════════════════════════════════════════════
# Welcome Card
# ══════════════════════════════════════════════════
today_str = datetime.now().strftime("%A, %B %d, %Y" if language == "English" else "%Y年%m月%d日 %A")

welcome_text = t["welcome"] if has_data else t["welcome_new"]

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
    border-radius: 12px;
    padding: 32px 40px;
    margin-bottom: 24px;
    color: white;
">
    <div style="font-size: 28px; font-weight: 800; margin-bottom: 4px;">
        {welcome_text}, {user_name}!
    </div>
    <div style="font-size: 15px; opacity: 0.85;">
        {t["today"]}: {today_str}
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
render_medical_disclaimer(language)

# Empty State
# ══════════════════════════════════════════════════
if not has_data:
    st.markdown(f"""
    <div style="text-align: center; padding: 60px 20px;">
        <div style="font-size: 48px; margin-bottom: 16px;">🌱</div>
        <div style="font-size: 24px; font-weight: 700; color: #172026; margin-bottom: 8px;">
            {t["no_data_title"]}
        </div>
        <div style="font-size: 16px; color: #667085; max-width: 480px; margin: 0 auto 32px;">
            {t["no_data_body"]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, _ = st.columns([1, 1, 2])
    with c1:
        if st.button(f"🩺 {t['start_health']}", use_container_width=True):
            st.switch_page("pages/1_Health_Check.py")
    with c2:
        if st.button(f"🧠 {t['start_emotion']}", use_container_width=True):
            st.switch_page("pages/2_Mind_Reset.py")
    st.stop()

# ══════════════════════════════════════════════════
# Snapshot Cards Row
# ══════════════════════════════════════════════════
sc1, sc2 = st.columns(2)

with sc1:
    st.markdown(f"""
    <div style="
        background: white;
        border: 1px solid #d9e2e7;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(15,23,42,0.04);
    ">
        <div style="font-size: 13px; font-weight: 800; color: #667085; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px;">
            🩺 {t["health_snapshot"]}
        </div>
    """, unsafe_allow_html=True)

    if has_health:
        h = data["health"]
        score = h.get("health_score", "—")
        risk = h.get("risk_level", "—")
        pct = h.get("risk_percent", "—")
        created = (h.get("created_at") or "")[:10]

        score_color = "#22c55e" if (score or 0) >= 70 else ("#eab308" if (score or 0) >= 40 else "#ef4444")

        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 13px; color: #667085;">{t["health_score"]}</div>
                <div style="font-size: 36px; font-weight: 900; color: {score_color};">{score}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 13px; color: #667085;">{t["risk_level"]}</div>
                <div style="font-size: 16px; font-weight: 700; color: #172026;">{risk}</div>
                <div style="font-size: 13px; color: #667085; margin-top: 4px;">{pct}% {t["risk_percent"]}</div>
            </div>
        </div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 12px;">
            {t["last_check"]}: {created}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(t["no_health"])

    st.markdown("</div>", unsafe_allow_html=True)

with sc2:
    st.markdown(f"""
    <div style="
        background: white;
        border: 1px solid #d9e2e7;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(15,23,42,0.04);
    ">
        <div style="font-size: 13px; font-weight: 800; color: #667085; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px;">
            🧠 {t["emotion_snapshot"]}
        </div>
    """, unsafe_allow_html=True)

    if has_emotion:
        e = data["emotion"]
        stress = e.get("stress", "—")
        energy = e.get("energy", "—")
        pattern = e.get("pattern_key", "—")
        mood = localize_emotion(e.get("mood_key", "—"), language)
        created_e = (e.get("created_at") or "")[:10]

        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 13px; color: #667085;">{t["stress"]}</div>
                <div style="font-size: 28px; font-weight: 900; color: {'#22c55e' if (stress or 5) <= 4 else '#eab308' if (stress or 5) <= 6 else '#ef4444'};">{stress}/10</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 13px; color: #667085;">{t["energy"]}</div>
                <div style="font-size: 28px; font-weight: 900; color: {'#22c55e' if (energy or 5) >= 7 else '#eab308' if (energy or 5) >= 4 else '#ef4444'};">{energy}/10</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 13px; color: #667085;">{t["pattern"]}</div>
                <div style="font-size: 14px; font-weight: 700; color: #172026;">{pattern}</div>
                <div style="font-size: 12px; color: #667085; margin-top: 4px;">{mood}</div>
            </div>
        </div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 12px;">
            {t["last_analysis"]}: {created_e}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(t["no_emotion"])

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# Trend Cards
# ══════════════════════════════════════════════════
render_section_label(t["trends"])

trends = data.get("trends", {})
metrics = trends.get("metrics", []) if trends else []
trend_map = {
    m.get("metric"): m
    for m in metrics
    if isinstance(m, dict) and m.get("metric")
}


def _dash_number(value):
    try:
        if value is None:
            return "—"
        number = float(value)
        if number.is_integer():
            return str(int(number))
        return str(round(number, 1))
    except (TypeError, ValueError):
        return "—"


def _dash_change_text(value):
    try:
        if value is None:
            return "—"
        number = float(value)
        sign = "+" if number > 0 else ""
        if number.is_integer():
            return f"{sign}{int(number)}"
        return f"{sign}{round(number, 1)}"
    except (TypeError, ValueError):
        return "—"

trend_configs = [
    ("trend_health", "health_score", "🟢" if language == "English" else "🟢"),
    ("trend_stress", "stress", "🔴" if language == "English" else "🔴"),
    ("trend_energy", "energy", "🔵" if language == "English" else "🔵"),
]

tc1, tc2, tc3, _ = st.columns([1, 1, 1, 1])

for idx, (label_key, metric_key, icon) in enumerate(trend_configs):
    col = [tc1, tc2, tc3][idx]
    with col:
        tm = trend_map.get(metric_key, {})
        direction = tm.get("direction", "insufficient_data")
        dir_icon = {"improving": "↑", "stable": "→", "declining": "↓"}.get(direction, "·")
        dir_label = t.get(direction, t["insufficient"])
        current_value = _dash_number(tm.get("current"))
        change_value = _dash_change_text(tm.get("change"))
        change_label = (
            f"{change_value} this week"
            if language == "English" and change_value != "—"
            else f"本周 {change_value}"
            if language == "中文" and change_value != "—"
            else t["insufficient"]
        )

        color_map = {
            "improving": {"health_score": "#22c55e", "stress": "#22c55e", "energy": "#22c55e"},
            "declining": {"health_score": "#ef4444", "stress": "#ef4444", "energy": "#ef4444"},
        }
        if direction == "improving":
            txt_color = "#22c55e"
        elif direction == "declining":
            txt_color = "#ef4444"
        else:
            txt_color = "#667085"

        st.markdown(f"""
        <div style="
            background: white;
            border: 1px solid #d9e2e7;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
            margin-bottom: 12px;
        ">
            <div style="font-size: 13px; color: #667085; font-weight: 700;">{t[label_key]}</div>
            <div style="font-size: 30px; font-weight: 900; color: {txt_color}; margin: 4px 0;">
                {dir_icon} {current_value}
            </div>
            <div style="font-size: 13px; color: {txt_color}; font-weight: 700;">
                {change_label}
            </div>
            <div style="font-size: 12px; color: #667085; margin-top: 4px;">
                {dir_label}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# Key Insights
# ══════════════════════════════════════════════════
render_section_label(t["key_insights"])

insights = build_trend_insights(data, language)

if insights:
    insight_cols = st.columns(min(len(insights), 4))
    for idx, insight in enumerate(insights):
        with insight_cols[idx % len(insight_cols)]:
            st.markdown(f"""
            <div style="
                background: white;
                border: 1px solid #d9e2e7;
                border-radius: 10px;
                padding: 16px;
                min-height: 132px;
                margin-bottom: 18px;
                box-shadow: 0 4px 12px rgba(15,23,42,0.04);
            ">
                <div style="font-size: 24px; margin-bottom: 10px;">{insight.get("icon", "•")}</div>
                <div style="font-size: 14px; color: #172026; line-height: 1.55; font-weight: 600;">
                    {insight.get("text", "")}
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info(t["no_insights"])

# ══════════════════════════════════════════════════
# Local AI Wellness Summary (rule-based, no API call)
# ══════════════════════════════════════════════════
render_section_label("AI Wellness Summary" if language == "English" else "AI 健康摘要")

# Compute strongest/weakest areas from latest health record
module_scores = {}
if has_health:
    h = data["health"]
    module_labels_en = {
        "bmi_score": "BMI", "water_score": "Water", "sleep_score": "Sleep",
        "activity_score": "Activity", "diet_score": "Diet", "mental_score": "Mental",
        "screen_score": "Screen", "habit_score": "Habit",
    }
    module_labels_cn = {
        "bmi_score": "BMI", "water_score": "饮水", "sleep_score": "睡眠",
        "activity_score": "运动", "diet_score": "饮食", "mental_score": "心理",
        "screen_score": "屏幕", "habit_score": "习惯",
    }
    labels = module_labels_cn if language == "中文" else module_labels_en
    for key, label in labels.items():
        val = h.get(key)
        if val is not None:
            module_scores[label] = val

    if module_scores:
        sorted_modules = sorted(module_scores.items(), key=lambda x: x[1])
        strongest = sorted_modules[0]
        weakest = sorted_modules[-1]

        if language == "中文":
            summary_text = f"最强模块：{strongest[0]}（评分 {strongest[1]}/3），建议继续保持。需关注：{weakest[0]}（评分 {weakest[1]}/3）。"
        else:
            summary_text = f"Strongest: {strongest[0]} (score {strongest[1]}/3). Needs attention: {weakest[0]} (score {weakest[1]}/3)."

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f0fdf4 0%, #f0f9ff 100%);
            border: 1px solid #bbf7d0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        ">
            <div style="font-size: 15px; color: #172026; line-height: 1.6;">{summary_text}</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# Quick Actions
# ══════════════════════════════════════════════════
st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
render_section_label(t["quick_actions"])

qa1, qa2, qa3, qa4 = st.columns(4)

with qa1:
    if st.button(f"🩺 {t['health_check']}", use_container_width=True):
        st.switch_page("pages/1_Health_Check.py")
with qa2:
    if st.button(f"🧠 {t['mind_reset']}", use_container_width=True):
        st.switch_page("pages/2_Mind_Reset.py")
with qa3:
    if st.button(f"📊 {t['history']}", use_container_width=True):
        st.switch_page("pages/3_Wellness_History.py")
with qa4:
    if st.button(f"📋 {t['final_report']}", use_container_width=True):
        st.switch_page("pages/4_Final_Report.py")

st.divider()
st.caption(t["footer"])
