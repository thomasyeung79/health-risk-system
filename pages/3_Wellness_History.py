import streamlit as st
import pandas as pd

from modules.emotion_localization import localize_emotion
from modules.ui import (
    apply_product_theme,
    require_auth,
    require_user,
    render_hero,
    render_nav,
    render_section_label,
    render_topbar,
)

# ── Backend API data loading ────────────────────────
BACKEND_AVAILABLE = False
try:
    from api_client.client import ApiClient
    from api_client.health_client import HealthClient
    from api_client.emotion_client import EmotionClient
    from api_client.report_client import ReportClient
    from api_client.trend_client import TrendClient

    if "api_client" in st.session_state:
        client = st.session_state["api_client"]
    else:
        client = ApiClient()
        st.session_state["api_client"] = client

    # Restore tokens if available
    if st.session_state.get("access_token"):
        client.set_tokens(
            st.session_state["access_token"],
            st.session_state.get("refresh_token", ""),
        )

    health_api = HealthClient(client)
    emotion_api = EmotionClient(client)
    report_api = ReportClient(client)
    trend_api = TrendClient(client)
    health_status = client.get("/health")
    BACKEND_AVAILABLE = client.is_authenticated and health_status.get("status") == "ok"
except Exception:
    pass


def load_health_records_api():
    """Load health records from backend API."""
    if not BACKEND_AVAILABLE:
        return []
    try:
        result = health_api.list_records(limit=100, offset=0)
        return result.get("items", [])
    except Exception:
        return []


def load_emotion_records_api():
    """Load emotion records from backend API."""
    if not BACKEND_AVAILABLE:
        return []
    try:
        result = emotion_api.list_records(limit=100, offset=0)
        return result.get("items", [])
    except Exception:
        return []


def _record_key(record):
    if not isinstance(record, dict):
        return ""
    src = record.get("result", record)
    return "|".join([
        str(record.get("id", "")),
        str(record.get("created_at") or record.get("timestamp") or ""),
        str(src.get("health_score") or src.get("overall_score") or ""),
        str(record.get("user_name") or record.get("username") or ""),
    ])


def _merge_records(*record_groups):
    merged = []
    seen = set()
    for records in record_groups:
        for record in records or []:
            if not isinstance(record, dict):
                continue
            key = _record_key(record)
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            merged.append(record)
    return merged


def safe_to_datetime(values):
    """Parse mixed API/local datetime strings without crashing the page."""
    try:
        return pd.to_datetime(values, format="mixed", errors="coerce")
    except (TypeError, ValueError):
        series = values if isinstance(values, pd.Series) else pd.Series(values)
        return series.apply(lambda value: pd.to_datetime(value, errors="coerce"))

st.set_page_config(
    page_title="Wellness History",
    page_icon="W",
    layout="wide"
)

apply_product_theme()

language = st.session_state.get("language", "English")
user_name = st.session_state.get("user_name")
require_auth(language)
require_user(language)

TEXT = {
    "English": {
        "title": "Wellness History",
        "subtitle": "Review health and emotional records as a single longitudinal wellness timeline.",

        "health": "Health Records",
        "mind": "Mind Reset Records",

        "no_health": "No health records found.",
        "no_mind": "No mind reset records found.",
        "no_chart": "Not enough valid dated records to draw this chart.",

        "summary": "History Summary",

        "health_records": "Health Records",
        "mind_records": "Mind Records",
        "total_records": "Total Records",

        "back": "Back to Home",

        "footer": "AI Wellness Platform | History Module"
    },

    "中文": {
        "title": "历史记录",
        "subtitle": "用同一条时间线查看身体健康与情绪重整记录。",

        "health": "健康记录",
        "mind": "情绪记录",

        "no_health": "暂无健康记录。",
        "no_mind": "暂无情绪记录。",
        "no_chart": "暂无足够的有效日期记录用于绘制图表。",

        "summary": "历史总结",

        "health_records": "健康记录数",
        "mind_records": "情绪记录数",
        "total_records": "总记录数",

        "back": "返回首页",

        "footer": "AI健康与情绪系统 | 历史模块"
    }
}

t = TEXT[language]

render_topbar(language, user_name)
render_nav(language, "pages/3_Wellness_History.py")
render_hero(
    t["title"],
    t["subtitle"],
    "Progress archive" if language == "English" else "进度档案",
    f"{user_name}",
)

if st.button(t["back"]):
    st.switch_page("web_v1.py")


# ── Load data ───────────────────────────────────────
from database import (
    load_health_json,
    load_health_records,
    load_mind_records,
    filter_user,
)

api_health_records = load_health_records_api() if BACKEND_AVAILABLE else []
api_mind_records = load_emotion_records_api() if BACKEND_AVAILABLE else []

health_df = load_health_records()
local_health_csv = filter_user(health_df.to_dict("records"), user_name)
local_health_json = filter_user(load_health_json(), user_name)

mind_df = load_mind_records()
local_mind_records = filter_user(mind_df.to_dict("records"), user_name)

health_records = _merge_records(
    api_health_records,
    local_health_json,
    local_health_csv,
)
mind_records = _merge_records(
    api_mind_records,
    local_mind_records,
)

st.divider()

col1, col2 = st.columns(2)


with col1:

    render_section_label(t["health"])

    if not health_records:
        st.info(t["no_health"])

    else:

        health_rows = []

        for r in health_records:
            # Support both API format (flat) and legacy format (with "result" wrapper)
            src = r.get("result", r) if isinstance(r, dict) else {}

            health_rows.append({
                "created_at": r.get("created_at") or r.get("timestamp", ""),
                "health_score": (
                    r.get("health_score")
                    if r.get("health_score") is not None
                    else src.get("health_score") or src.get("overall_score")
                ),
                "risk_level": r.get("risk_level") or src.get("risk_level"),
                "risk_percent": r.get("risk_percent") or src.get("risk_percent"),
            })

        health_df = pd.DataFrame(health_rows)

        st.dataframe(
            health_df.sort_values("created_at", ascending=False),
            use_container_width=True
        )

        if "health_score" in health_df.columns:

            chart_df = health_df.dropna(
                subset=["health_score"]
            ).copy()

            if not chart_df.empty:

                chart_df["created_at"] = safe_to_datetime(chart_df["created_at"])
                chart_df = chart_df.dropna(subset=["created_at"])

                if chart_df.empty:
                    st.info(t["no_chart"])
                else:
                    chart_df = chart_df.sort_values(
                        "created_at"
                    )

                    st.line_chart(
                        chart_df.set_index(
                            "created_at"
                        )["health_score"]
                    )


with col2:

    render_section_label(t["mind"])

    if not mind_records:
        st.info(t["no_mind"])

    else:

        mind_rows = []

        for r in mind_records:
            # Map API format or legacy format to display columns
            mood_value = r.get("mood") or r.get("mood_key", "")
            mind_rows.append({
                "created_at": r.get("created_at", ""),
                "mood": localize_emotion(mood_value, language),
                "event": r.get("event") or r.get("event_key", ""),
                "energy": r.get("energy"),
                "stress": r.get("stress"),
                "topic": r.get("topic") or r.get("pattern_key", ""),
            })

        mind_df = pd.DataFrame(mind_rows)

        st.dataframe(
            mind_df.sort_values(
                "created_at",
                ascending=False
            ),
            use_container_width=True
        )

        if "stress" in mind_df.columns:

            chart_df = mind_df.dropna(
                subset=["stress"]
            ).copy()

            if not chart_df.empty:

                chart_df["created_at"] = safe_to_datetime(chart_df["created_at"])
                chart_df = chart_df.dropna(subset=["created_at"])

                if chart_df.empty:
                    st.info(t["no_chart"])
                else:
                    chart_df = chart_df.sort_values(
                        "created_at"
                    )

                    st.line_chart(
                        chart_df.set_index(
                            "created_at"
                        )["stress"]
                    )

st.divider()


render_section_label(t["summary"])

health_count = len(health_records)
mind_count = len(mind_records)

c1, c2, c3 = st.columns(3)

c1.metric(
    t["health_records"],
    health_count
)

c2.metric(
    t["mind_records"],
    mind_count
)

c3.metric(
    t["total_records"],
    health_count + mind_count
)

if health_records:
    health_csv = pd.DataFrame(health_records).to_csv(index=False)
    st.download_button(
        "Download Health Data (CSV)" if language == "English" else "下载健康数据（CSV）",
        data=health_csv,
        file_name=f"health_{user_name}.csv",
        mime="text/csv",
        use_container_width=True,
    )

if mind_records:
    import json
    mind_json = json.dumps(mind_records, ensure_ascii=False, indent=2)
    st.download_button(
        "Download Mind Records (JSON)" if language == "English" else "下载情绪记录（JSON）",
        data=mind_json,
        file_name=f"mind_{user_name}.json",
        mime="application/json",
        use_container_width=True,
    )

st.divider()

st.caption(t["footer"])

if st.button("Next: Final Report" if language == "English" else "下一步：综合报告"):
    st.switch_page("pages/4_Final_Report.py")
