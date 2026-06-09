"""AI Wellness Coach — interactive chat with personalised wellness guidance."""

from datetime import datetime
from typing import Any

import streamlit as st

from modules.coach_engine import build_coaching_response
from modules.ui import apply_product_theme, render_topbar

st.set_page_config(page_title="AI Coach", page_icon="W", layout="wide")
apply_product_theme()

language = st.session_state.get("language", "English")
user_name = st.session_state.get("user_name", "")

TEXT = {
    "English": {
        "title": "AI Wellness Coach",
        "subtitle": "Ask me anything about your health and wellness.",
        "input_placeholder": "Ask me anything about your health...",
        "suggestions": "Try asking",
        "clear": "Clear conversation",
        "coach_header": "Wellness Coach",
        "footer": "WellNest AI | AI Coach",
    },
    "中文": {
        "title": "AI 健康教练",
        "subtitle": "关于你的健康，有什么想问的吗？",
        "input_placeholder": "输入你的问题...",
        "suggestions": "试试问",
        "clear": "清除对话",
        "coach_header": "健康教练",
        "footer": "WellNest AI | AI 教练",
    },
}

t = TEXT.get(language, TEXT["English"])
is_cn = language == "中文"

render_topbar(language, user_name)

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

    hc = _client.get("/health")
    if hc.get("status") == "ok" and _client.is_authenticated:
        BACKEND_AVAILABLE = True
        health_api = HealthClient(_client)
        emotion_api = EmotionClient(_client)
        report_api = ReportClient(_client)
        trend_api = TrendClient(_client)
except Exception:
    pass


def gather_context() -> dict[str, Any]:
    ctx: dict[str, Any] = {"health": None, "emotion": None, "trends": None, "report": None}
    if not BACKEND_AVAILABLE:
        return ctx
    try:
        hr = health_api.list_records(limit=1).get("items", [])
        if hr:
            ctx["health"] = hr[0]
        ctx["trends"] = trend_api.summary(days=7, language=language)
    except Exception:
        pass
    try:
        er = emotion_api.list_records(limit=1).get("items", [])
        if er:
            ctx["emotion"] = er[0]
    except Exception:
        pass
    try:
        rr = report_api.list_reports(limit=1).get("items", [])
        if rr:
            ctx["report"] = rr[0]
    except Exception:
        pass
    return ctx


def generate_response(question: str, context: dict) -> dict:
    has_data = context.get("health") is not None or context.get("emotion") is not None
    if not has_data:
        if is_cn:
            return {"situation": "暂无健康或情绪数据。", "strengths": [], "concerns": [], "actions": ["请先完成健康检测和情绪分析。"], "goal": "完成首次检测。"}
        return {"situation": "No health or emotion data available.", "strengths": [], "concerns": [], "actions": ["Complete a Health Check and Mind Reset first."], "goal": "Complete your first assessment."}

    # Try DeepSeek via report API
    if BACKEND_AVAILABLE:
        try:
            data = report_api.generate(language=language, style="coaching", days=7)
            report_text = data.get("report", {}).get("summary", "") or ""
            sections = data.get("report", {}).get("sections", [])
            if not report_text and sections:
                report_text = " ".join(s.get("content", "") for s in sections[:2])
            if len(report_text) > 50:
                actions = ["Focus on your highest-priority module", "Maintain consistent tracking"]
                if "sleep" in report_text.lower()[:300]:
                    actions[0] = "Prioritise sleep quality improvement"
                if not is_cn:
                    return {"situation": report_text[:600], "strengths": [], "concerns": [], "actions": actions, "goal": "Review the full AI report for details."}
                actions_cn = ["关注优先级最高的模块", "保持定期记录"]
                if "sleep" in report_text.lower()[:300]:
                    actions_cn[0] = "优先改善睡眠质量"
                return {"situation": report_text[:600], "strengths": [], "concerns": [], "actions": actions_cn, "goal": "查看完整 AI 报告获取详细建议。"}
        except Exception:
            pass
    return build_coaching_response(context, question, language)


SUGGESTIONS_EN = [
    "Summarise my health",
    "What should I improve first?",
    "Explain my latest emotion result",
    "Give me a 7-day action plan",
    "What are my biggest risks?",
]
SUGGESTIONS_CN = [
    "总结我的健康状态",
    "我首先应该改善什么？",
    "分析我近期的情绪",
    "给我一个7天行动计划",
    "我最大的风险是什么？",
]
suggestions = SUGGESTIONS_CN if is_cn else SUGGESTIONS_EN

if "coach_msgs" not in st.session_state:
    st.session_state.coach_msgs = []


def _format(r: dict, q: str) -> str:
    if is_cn:
        lines = [f"**🤖 {t['coach_header']}**\n"]
    else:
        lines = [f"**🤖 {t['coach_header']}**\n"]

    label_s = "📋 当前状况" if is_cn else "📋 Current Situation"
    label_str = "✅ 优势" if is_cn else "✅ Strengths"
    label_c = "⚠️ 关注点" if is_cn else "⚠️ Concerns"
    label_a = "🎯 建议行动" if is_cn else "🎯 Recommended Actions"
    label_g = "🏆 下一个目标" if is_cn else "🏆 Next Goal"

    if r.get("situation"):
        lines.append(f"\n### {label_s}")
        lines.append(r["situation"])
    for label, items in [(label_str, r.get("strengths", [])), (label_c, r.get("concerns", []))]:
        if items:
            lines.append(f"\n### {label}")
            for item in items:
                lines.append(f"- {item}")
    acts = r.get("actions", [])
    if acts:
        lines.append(f"\n### {label_a}")
        for a in acts:
            lines.append(f"- {a}")
    goal = r.get("goal", "")
    if goal:
        lines.append(f"\n### {label_g}")
        lines.append(goal)
    return "\n".join(lines)


def ask(question: str):
    if not question or not question.strip():
        return
    q = question.strip()
    ctx = gather_context()
    now = datetime.now().strftime("%H:%M")
    st.session_state.coach_msgs.append({"role": "user", "content": q, "time": now})
    result = generate_response(q, ctx)
    st.session_state.coach_msgs.append({"role": "assistant", "content": _format(result, q), "time": datetime.now().strftime("%H:%M")})


# ── UI ────────────────────────────────────────────
st.title(t["title"])
st.markdown(t["subtitle"])

msgs = st.session_state.coach_msgs
if msgs:
    for m in msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            st.caption(m["time"])
else:
    st.markdown(f"""<div style="text-align:center;padding:40px 20px;color:#667085;">
        <div style="font-size:48px;margin-bottom:12px;">🤖</div>
        <div style="font-size:18px;font-weight:600;color:#172026;">{t['title']}</div>
        <div style="font-size:14px;">{t['subtitle']}</div>
    </div>""", unsafe_allow_html=True)

num_cols = min(len(suggestions), 3)
cols = st.columns(num_cols)
for idx, s in enumerate(suggestions):
    with cols[idx % num_cols]:
        if st.button(s, use_container_width=True, key=f"s_{idx}"):
            ask(s)
            st.rerun()

q_input = st.chat_input(placeholder=t["input_placeholder"])
if q_input:
    ask(q_input)
    st.rerun()

if msgs:
    st.divider()
    if st.button(f"🗑️ {t['clear']}", use_container_width=False):
        st.session_state.coach_msgs = []
        st.rerun()

st.divider()
st.caption(t["footer"])
