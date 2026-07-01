"""Dashboard — insights-first landing page for the product experience."""

from datetime import datetime

import streamlit as st

from modules.dashboard_insights import build_trend_insights
from modules.emotion_localization import localize_emotion
from modules.ui import (
    apply_product_theme,
    render_metric_card,
    render_insight_card,
    render_achievement_card,
    render_section,
    render_empty_state,
    render_topbar,
)

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
apply_product_theme()

language = st.session_state.get("language", "English")
user_name = st.session_state.get("user_name", "")

T = {
    "English": {
        "welcome": "Welcome back",
        "welcome_new": "Welcome to WellNest AI",
        "today": "Today",
        "health_score": "Wellness Score",
        "risk_level": "Risk Level",
        "stress": "Stress",
        "energy": "Energy",
        "pattern": "Pattern",
        "mood": "Mood",
        "no_health": "Complete a health assessment to see your score",
        "no_emotion": "Record your first emotion check-in",
        "trends": "Wellness Trends",
        "trend_health": "Health",
        "trend_stress": "Stress",
        "trend_energy": "Energy",
        "key_insights": "Key Insights",
        "no_insights": "Complete more assessments to unlock personalised insights",
        "quick_actions": "Quick Actions",
        "health_check": "Health Assessment",
        "reflection": "Reflection",
        "history": "Wellness History",
        "report": "Insights Report",
        "coach": "AI Coach",
        "go": "Open",
        "activity": "Recent Activity",
        "no_activity": "Start tracking to see your wellness story",
        "start_health": "Start Health Assessment",
        "start_reflection": "Start Reflection",
    },
    "中文": {
        "welcome": "欢迎回来",
        "welcome_new": "欢迎来到 WellNest AI",
        "today": "今天",
        "health_score": "健康评分",
        "risk_level": "风险等级",
        "stress": "压力",
        "energy": "精力",
        "pattern": "模式",
        "mood": "心情",
        "no_health": "完成健康评估以查看评分",
        "no_emotion": "记录首次情绪检测",
        "trends": "健康趋势",
        "trend_health": "健康",
        "trend_stress": "压力",
        "trend_energy": "精力",
        "key_insights": "关键洞察",
        "no_insights": "完成更多评估后可解锁个性化洞察",
        "quick_actions": "快捷操作",
        "health_check": "健康评估",
        "reflection": "反思",
        "history": "健康历程",
        "report": "洞察报告",
        "coach": "AI 教练",
        "go": "进入",
        "activity": "最近动态",
        "no_activity": "开始记录以查看你的健康故事",
        "start_health": "开始健康评估",
        "start_reflection": "开始反思",
    },
}

t = T.get(language, T["English"])
today_str = datetime.now().strftime(
    "%A, %B %d, %Y" if language == "English" else "%Y年%m月%d日 %A"
)

render_topbar(language, user_name)

# ── Logout ──────────────────────────────────────────
with st.sidebar:
    st.markdown("### " + ("" if language == "English" else ""))
    if st.button("🚪 " + ("Sign Out" if language == "English" else "退出"), use_container_width=True):
        for k in ["access_token", "refresh_token", "api_user", "user_name", "authenticated"]:
            st.session_state.pop(k, None)
        st.switch_page("web_v1.py")

# ── API client ──────────────────────────────────────
BACKEND = False
try:
    from api_client.client import ApiClient
    from api_client.health_client import HealthClient
    from api_client.emotion_client import EmotionClient
    from api_client.trend_client import TrendClient

    if "api_client" in st.session_state:
        _c = st.session_state["api_client"]
    else:
        _c = ApiClient()
        st.session_state["api_client"] = _c
    if st.session_state.get("access_token"):
        _c.set_tokens(st.session_state["access_token"], st.session_state.get("refresh_token", ""))
    if _c.get("/health").get("status") == "ok" and _c.is_authenticated:
        BACKEND = True
        health_api = HealthClient(_c)
        emotion_api = EmotionClient(_c)
        trend_api = TrendClient(_c)
except Exception:
    pass


def load_data():
    d = {"health": None, "emotion": None, "health_stats": None, "emotion_stats": None, "trends": None}
    if not BACKEND:
        return d
    try:
        hr = health_api.list_records(limit=1)
        items = hr.get("items", [])
        if items:
            d["health"] = items[0]
        d["health_stats"] = health_api.stats()
    except Exception:
        pass
    try:
        er = emotion_api.list_records(limit=1)
        items = er.get("items", [])
        if items:
            d["emotion"] = items[0]
        d["emotion_stats"] = emotion_api.stats()
    except Exception:
        pass
    try:
        d["trends"] = trend_api.summary(days=7, language=language)
    except Exception:
        pass
    return d


data = load_data()
has_health = data["health"] is not None
has_emotion = data["emotion"] is not None
has_data = has_health or has_emotion

# ══════════════════════════════════════════════════════
# TOP SECTION — Welcome + Score + Risk
# ══════════════════════════════════════════════════════

welcome = t["welcome"] if has_data else t["welcome_new"]
st.markdown(f"""
<div class="hero-card" style="margin-bottom:20px;">
    <div class="hero-row">
        <div>
            <div style="font-size:13px;color:var(--brand-strong);font-weight:800;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px;">{t["today"]}</div>
            <div style="font-size:32px;font-weight:900;color:var(--ink);line-height:1.1;">{welcome}, {user_name}</div>
            <div style="font-size:15px;color:var(--muted);margin-top:4px;">{today_str}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# EMPTY STATE
# ══════════════════════════════════════════════════════
if not has_data:
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    render_empty_state(
        "🌱", t["welcome_new"],
        t["no_activity"],
        action_label=f"🩺 {t['start_health']}", action_key="dash_start_health_btn"
    )
    st.stop()

# ══════════════════════════════════════════════════════
# METRIC ROW — Score + Risk + Quick Stats
# ══════════════════════════════════════════════════════

mc1, mc2, mc3, mc4 = st.columns(4)

with mc1:
    if has_health:
        score = data["health"].get("health_score", "—")
        render_metric_card("🩺", t["health_score"], f"{score}/100")
    else:
        render_metric_card("🩺", t["health_score"], "—", color="#94a3b8")

with mc2:
    if has_health:
        risk = data["health"].get("risk_level", "—")
        render_metric_card("⚠️", t["risk_level"], risk)
    else:
        render_metric_card("⚠️", t["risk_level"], "—", color="#94a3b8")

with mc3:
    if has_emotion:
        energy = data["emotion"].get("energy", "—")
        render_metric_card("⚡", t["energy"], f"{energy}/10")
    else:
        render_metric_card("⚡", t["energy"], "—", color="#94a3b8")

with mc4:
    if has_emotion:
        stress = data["emotion"].get("stress", "—")
        render_metric_card("🧘", t["stress"], f"{stress}/10")
    else:
        render_metric_card("🧘", t["stress"], "—", color="#94a3b8")

# ══════════════════════════════════════════════════════
# INSIGHTS ROW
# ══════════════════════════════════════════════════════

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
render_section(t["key_insights"])

insights = build_trend_insights(data, language)
if insights:
    ic1, ic2 = st.columns(2)
    for idx, insight in enumerate(insights):
        col = ic1 if idx % 2 == 0 else ic2
        with col:
            render_insight_card(
                insight.get("text", ""),
                "",
                icon=insight.get("icon", "💡"),
            )
else:
    st.info(t["no_insights"])

# ══════════════════════════════════════════════════════
# TREND CARDS
# ══════════════════════════════════════════════════════

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
render_section(t["trends"])

trends_data = data.get("trends", {})
metrics = trends_data.get("metrics", []) if trends_data else []
trend_map = {m.get("metric"): m for m in metrics if isinstance(m, dict) and m.get("metric")}

tc1, tc2, tc3 = st.columns(3)

for idx, (label_key, metric_key, icon) in enumerate([
    ("trend_health", "health_score", "🟢"),
    ("trend_stress", "stress", "🔴"),
    ("trend_energy", "energy", "🔵"),
]):
    col = [tc1, tc2, tc3][idx]
    with col:
        tm = trend_map.get(metric_key, {})
        direction = tm.get("direction", "insufficient_data")
        current = tm.get("current")
        change = tm.get("change")

        if current is not None:
            try:
                cv = int(current) if float(current).is_integer() else round(float(current), 1)
            except (TypeError, ValueError):
                cv = "—"
        else:
            cv = "—"

        if change is not None:
            try:
                ch = int(change) if float(change).is_integer() else round(float(change), 1)
                prefix = "+" if ch > 0 else ""
                ch_str = f"{prefix}{ch}"
            except (TypeError, ValueError):
                ch_str = "—"
        else:
            ch_str = "—"

        dir_labels = {
            "improving": ("↑ " + ("Improving" if language == "English" else "改善中"), "#15803d"),
            "stable": ("→ " + ("Stable" if language == "English" else "稳定"), "#6b7280"),
            "declining": ("↓ " + ("Declining" if language == "English" else "下降中"), "#b91c1c"),
        }
        dir_str, dir_color = dir_labels.get(direction, ("· " + ("Insufficient data" if language == "English" else "数据不足"), "#94a3b8"))

        st.markdown(f"""
        <div class="product-card" style="text-align:center;padding:20px;border-top:4px solid {dir_color};">
            <div style="font-size:13px;color:var(--muted);font-weight:700;letter-spacing:0.04em;text-transform:uppercase;margin-bottom:8px;">{t[label_key]}</div>
            <div style="font-size:36px;font-weight:900;color:var(--ink);">{cv}</div>
            <div style="font-size:14px;color:{dir_color};font-weight:700;margin-top:4px;">{dir_str} ({ch_str})</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# QUICK ACTIONS
# ══════════════════════════════════════════════════════

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
render_section(t["quick_actions"])

qa1, qa2, qa3, qa4, qa5 = st.columns(5)

with qa1:
    if st.button(f"🩺 {t['health_check']}", use_container_width=True):
        st.switch_page("pages/1_Health_Check.py")
with qa2:
    if st.button(f"💭 {t['reflection']}", use_container_width=True):
        st.switch_page("pages/2_Mind_Reset.py")
with qa3:
    if st.button(f"📊 {t['history']}", use_container_width=True):
        st.switch_page("pages/3_Wellness_History.py")
with qa4:
    if st.button(f"📋 {t['report']}", use_container_width=True):
        st.switch_page("pages/4_Final_Report.py")
with qa5:
    if st.button(f"🤖 {t['coach']}", use_container_width=True):
        st.switch_page("pages/5_AI_Coach.py")

# ══════════════════════════════════════════════════════
# RECENT ACTIVITY
# ══════════════════════════════════════════════════════

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
render_section(t["activity"])

activity_items = []

if has_health:
    h = data["health"]
    h_date = (h.get("created_at") or "")[:10]
    h_score = h.get("health_score", "—")
    activity_items.append(("🩺", h_date, t["health_check"], f"Score: {h_score}"))

if has_emotion:
    e = data["emotion"]
    e_date = (e.get("created_at") or "")[:10]
    mood = localize_emotion(e.get("mood_key", ""), language)
    activity_items.append(("💭", e_date, t["reflection"], f"Mood: {mood}"))

if activity_items:
    for icon, date, title, desc in activity_items:
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-icon">{icon}</div>
            <div class="timeline-body">
                <div class="timeline-date">{date}</div>
                <div class="timeline-title">{title}</div>
                <div class="timeline-desc">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info(t["no_activity"])

st.divider()
st.caption("WellNest AI | " + ("Dashboard" if language == "English" else "看板"))
