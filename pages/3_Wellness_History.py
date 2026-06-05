import streamlit as st
import pandas as pd

from database import load_health_records, load_mind_records, load_json, filter_user
from modules.ui import (
    apply_product_theme,
    require_auth,
    require_user,
    render_hero,
    render_nav,
    render_section_label,
    render_topbar,
)

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


health_df = load_health_records()
mind_df = load_mind_records()

health_records = health_df.to_dict("records")
mind_records = mind_df.to_dict("records")

health_records = filter_user(health_records, user_name)
mind_records = filter_user(mind_records, user_name)

st.divider()

col1, col2 = st.columns(2)


with col1:

    render_section_label(t["health"])

    if not health_records:
        st.info(t["no_health"])

    else:

        health_rows = []

        for r in health_records:

            result = r.get("result", r)

            health_rows.append({
                "created_at": r.get("created_at") if r.get("created_at") is not None else r.get("timestamp"),
                "user": r.get("user_name") if r.get("user_name") is not None else r.get("username"),
                "health_score": result.get("health_score") if result.get("health_score") is not None else result.get("overall_score"),
                "risk_level": result.get("risk_level"),
                "risk_percent": result.get("risk_percent")
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

                chart_df["created_at"] = pd.to_datetime(
                    chart_df["created_at"]
                )

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

            mind_rows.append({
                "created_at": r.get("created_at"),
                "user": r.get("username") or r.get("user_name"),
                "mood": r.get("mood"),
                "event": r.get("event"),
                "energy": r.get("energy"),
                "stress": r.get("stress"),
                "topic": r.get("topic"),
                "summary": r.get("summary")
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

                chart_df["created_at"] = pd.to_datetime(
                    chart_df["created_at"]
                )

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
