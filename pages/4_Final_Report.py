import streamlit as st
from datetime import datetime
import os
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd

from database import load_json, filter_user, HEALTH_JSON, MIND_JSON

try:
    from modules.pdf_report import generate_pdf as generate_pdf_report
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False
from modules.ui import (
    apply_product_theme,
    require_auth,
    require_user,
    render_hero,
    render_nav,
    render_panel,
    render_section_label,
    render_topbar,
)

matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = [
    "Noto Sans CJK JP",
    "DejaVu Sans",
]
matplotlib.rcParams["axes.unicode_minus"] = False

st.set_page_config(
    page_title="Final Wellness Report",
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
        "title": "Final Wellness Report",
        "subtitle": "Combine your latest physical and emotional records into one practical wellness plan.",

        "generate": "Generate Final AI Report",
        "loading": "Generating combined wellness insight...",
        "ai_error": "AI report generation is unavailable. Please check your OpenAI API key and try again.",
        "fallback_notice": "AI generation is unavailable, so a local summary was generated instead.",
        "download": "Download Report",
        "download_pdf": "Export PDF",

        "no_data": "No health or mind records found for this user.",

        "health_snapshot": "Health Snapshot",
        "mind_snapshot": "Mind Snapshot",
        "history_snapshot": "History Trend",
        "intelligence_snapshot": "Wellness Intelligence",
        "trend_chart": "Trend Timeline",
        "report_style": "Report Style",
        "style_balanced": "Balanced",
        "style_coaching": "Coaching",
        "style_clinical": "Clinical",

        "health_score": "Health Score",
        "risk_level": "Risk Level",
        "risk_percent": "Risk Percent",
        "health_records": "Health Records",
        "mind_records": "Mind Records",
        "health_trend": "Health Trend",
        "stress_trend": "Stress Trend",
        "energy_trend": "Energy Trend",
        "data_coverage": "Data Coverage",
        "average_health": "Avg Health",
        "average_stress": "Avg Stress",
        "average_energy": "Avg Energy",

        "mood": "Mood",
        "energy": "Energy",
        "stress": "Stress",

        "no_health": "No health record.",
        "no_mind": "No mind reset record.",

        "insight_title": "AI Final Wellness Insight",

        "radar_title": "Wellness Radar",

        "radar_labels": ["BMI", "Water", "Sleep", "Activity", "Diet", "Mental", "Screen", "Habit"],

        "back": "Back to Home",

        "footer": "AI Wellness Platform | Final Report Module"
    },

    "中文": {
        "title": "综合健康报告",
        "subtitle": "把最新身体记录和情绪记录整合成一份可执行的健康计划。",

        "generate": "生成最终AI报告",
        "loading": "正在生成综合健康与情绪分析...",
        "ai_error": "AI 报告暂时无法生成，请检查 OpenAI API Key 后重试。",
        "fallback_notice": "AI 生成暂时不可用，已为你生成本地综合报告。",
        "download": "下载报告",
        "download_pdf": "导出 PDF",

        "no_data": "未找到该用户的健康或情绪记录。",

        "health_snapshot": "健康快照",
        "mind_snapshot": "情绪快照",
        "history_snapshot": "历史趋势",
        "intelligence_snapshot": "健康智能概览",
        "trend_chart": "趋势时间线",
        "report_style": "报告风格",
        "style_balanced": "平衡分析",
        "style_coaching": "教练建议",
        "style_clinical": "专业简洁",

        "health_score": "健康评分",
        "risk_level": "风险等级",
        "risk_percent": "风险比例",
        "health_records": "健康记录",
        "mind_records": "情绪记录",
        "health_trend": "健康趋势",
        "stress_trend": "压力趋势",
        "energy_trend": "能量趋势",
        "data_coverage": "数据覆盖度",
        "average_health": "平均健康",
        "average_stress": "平均压力",
        "average_energy": "平均能量",

        "mood": "情绪",
        "energy": "能量",
        "stress": "压力",

        "no_health": "暂无健康记录。",
        "no_mind": "暂无情绪记录。",

        "insight_title": "AI综合健康分析",

        "radar_title": "综合健康雷达图",

        "radar_labels": ["BMI", "饮水", "睡眠", "运动", "饮食", "心理", "屏幕", "习惯"],

        "back": "返回首页",

        "footer": "AI健康与情绪系统 | 综合报告模块"
    }
}

t = TEXT[language]

# ── Backend API availability ───────────────────────
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
        report_api = ReportClient(_client)
        trend_api = TrendClient(_client)
except Exception:
    pass


render_topbar(language, user_name)
render_nav(language, "pages/4_Final_Report.py")
render_hero(
    t["title"],
    t["subtitle"],
    "Integrated report" if language == "English" else "综合分析",
    f"{user_name}",
)

if st.button(t["back"]):
    st.switch_page("web_v1.py")


def get_latest_health(records):

    if not records:
        return None

    records = sorted(
        records,
        key=lambda x: x.get("created_at", "") or x.get("timestamp", ""),
        reverse=True
    )

    latest = records[0]

    return latest.get("result", latest)


def get_latest_mind(records):

    if not records:
        return None

    records = sorted(
        records,
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )

    return records[0]


def get_health_payload(record):
    return record.get("result", record)


def as_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def trend_label(start, end, language, higher_is_better=True):
    start_num = as_number(start)
    end_num = as_number(end)

    if start_num is None or end_num is None:
        return "Not enough data" if language == "English" else "数据不足"

    delta = round(end_num - start_num, 1)

    if abs(delta) < 0.5:
        return "Stable" if language == "English" else "基本稳定"

    improved = delta > 0 if higher_is_better else delta < 0

    if language == "中文":
        direction = "改善" if improved else "下降"
        return f"{direction} {abs(delta)}"

    direction = "Improved" if improved else "Declined"
    return f"{direction} by {abs(delta)}"


def data_coverage_label(health_count, mind_count, language):
    total = health_count + mind_count

    if total >= 8 and health_count >= 3 and mind_count >= 3:
        return "High" if language == "English" else "高"

    if total >= 4 and health_count >= 1 and mind_count >= 1:
        return "Medium" if language == "English" else "中"

    return "Early" if language == "English" else "初始"


def build_history_summary(health_records, mind_records, language):
    sorted_health = sorted(
        health_records,
        key=lambda x: x.get("created_at", "") or x.get("timestamp", "")
    )
    sorted_mind = sorted(
        mind_records,
        key=lambda x: x.get("created_at", "")
    )

    health_payloads = [get_health_payload(record) for record in sorted_health]
    health_scores = [
        as_number(item.get("health_score") if item.get("health_score") is not None else item.get("overall_score"))
        for item in health_payloads
    ]
    health_scores = [score for score in health_scores if score is not None]

    stress_scores = [
        as_number(record.get("stress"))
        for record in sorted_mind
    ]
    stress_scores = [score for score in stress_scores if score is not None]

    energy_scores = [
        as_number(record.get("energy"))
        for record in sorted_mind
    ]
    energy_scores = [score for score in energy_scores if score is not None]

    recent_health = health_payloads[-5:]
    recent_mind = sorted_mind[-5:]
    health_series = [
        {
            "created_at": record.get("created_at") or record.get("timestamp"),
            "health_score": score,
        }
        for record, score in zip(sorted_health, [
            as_number(item.get("health_score", item.get("overall_score")))
            for item in health_payloads
        ])
        if score is not None
    ]
    mind_series = [
        {
            "created_at": record.get("created_at"),
            "stress": as_number(record.get("stress")),
            "energy": as_number(record.get("energy")),
        }
        for record in sorted_mind
        if as_number(record.get("stress")) is not None
        or as_number(record.get("energy")) is not None
    ]

    return {
        "health_record_count": len(sorted_health),
        "mind_record_count": len(sorted_mind),
        "data_coverage": data_coverage_label(
            len(sorted_health),
            len(sorted_mind),
            language,
        ),
        "health_score_trend": trend_label(
            health_scores[0] if health_scores else None,
            health_scores[-1] if health_scores else None,
            language,
            higher_is_better=True,
        ),
        "stress_trend": trend_label(
            stress_scores[0] if stress_scores else None,
            stress_scores[-1] if stress_scores else None,
            language,
            higher_is_better=False,
        ),
        "energy_trend": trend_label(
            energy_scores[0] if energy_scores else None,
            energy_scores[-1] if energy_scores else None,
            language,
            higher_is_better=True,
        ),
        "average_health_score": round(sum(health_scores) / len(health_scores), 1)
        if health_scores else None,
        "average_stress": round(sum(stress_scores) / len(stress_scores), 1)
        if stress_scores else None,
        "average_energy": round(sum(energy_scores) / len(energy_scores), 1)
        if energy_scores else None,
        "health_series": health_series,
        "mind_series": mind_series,
        "recent_health_records": recent_health,
        "recent_mind_records": recent_mind,
    }


def generate_final_report(username, health, mind, history_summary, report_style, language, model="gpt-4o-mini", use_ollama=False):

    if language == "中文":
        report_language = "Simplified Chinese"
        output_instruction = """
请用简体中文生成报告。
语气要像专业但易懂的健康顾问。
不要只分别分析身体和情绪，而是重点说明身体健康与情绪状态之间的关系。
"""
    else:
        report_language = "English"
        output_instruction = """
Generate the report in English.
Use a professional but easy-to-understand wellness coaching tone.
Do not only analyse physical health and emotional state separately. Focus on how physical health and emotional wellness influence each other.
"""

    prompt = f"""
You are an AI wellness analyst.

Username: {username}
Report language: {report_language}

Latest physical health data:
{health}

Latest emotional / mind reset data:
{mind}

Historical wellness trend summary:
{history_summary}

Preferred report style:
{report_style}

Important task:
Generate one integrated wellness report that combines physical health, emotional wellness, and the user's historical trend.

You must analyse:
1. Overall wellness summary
2. How physical health may affect emotional state
3. How emotional state may affect physical habits
4. What has changed across the user's history
5. Whether the trend is improving, stable, or worsening
6. Lifestyle interaction risks
7. Priority concerns
8. Practical action plan for tomorrow
9. Final recommendation

Use the user's actual data.
If one side has missing data, clearly say that the analysis is limited.
Do not overstate trends when there are only one or two records.

{output_instruction}

Keep the report clear, practical, and suitable for a portfolio project.
"""

    if use_ollama:
        ollama_base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        client = OpenAI(base_url=ollama_base, api_key="ollama")
    else:
        client = OpenAI()
    response = client.chat.completions.create(
        model=model if not use_ollama else "llama3.2",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )

    return response.choices[0].message.content


def value_or_na(value, language):
    if value in [None, ""]:
        return "N/A" if language == "English" else "暂无"
    return value


def generate_local_report(username, health, mind, history_summary, report_style, language, model="gpt-4o-mini"):
    if language == "中文":
        health_score = value_or_na(
            health.get("health_score", health.get("overall_score"))
            if health else None,
            language,
        )
        risk_level = value_or_na(health.get("risk_level") if health else None, language)
        mood = value_or_na(mind.get("mood") if mind else None, language)
        stress = value_or_na(mind.get("stress") if mind else None, language)
        energy = value_or_na(mind.get("energy") if mind else None, language)
        focus = value_or_na(health.get("primary_focus") if health else None, language)

        return f"""# {username} 的综合健康报告

## 当前状态
- 健康评分：{health_score}
- 风险等级：{risk_level}
- 当前情绪：{mood}
- 压力水平：{stress}
- 能量水平：{energy}

## 历史趋势
- 健康记录数：{history_summary["health_record_count"]}
- 情绪记录数：{history_summary["mind_record_count"]}
- 数据覆盖度：{history_summary["data_coverage"]}
- 健康评分趋势：{history_summary["health_score_trend"]}
- 压力趋势：{history_summary["stress_trend"]}
- 能量趋势：{history_summary["energy_trend"]}
- 平均健康评分：{value_or_na(history_summary["average_health_score"], language)}
- 平均压力：{value_or_na(history_summary["average_stress"], language)}
- 平均能量：{value_or_na(history_summary["average_energy"], language)}

## 综合解读
{focus if focus != "暂无" else "当前数据还不够完整，建议先完成一次健康检测和一次情绪重整。"}

身体状态、压力、睡眠、运动和屏幕使用往往会互相影响。如果健康评分下降同时压力升高，优先处理睡眠恢复、压力管理和日常活动量会更有效。

## 明日行动
1. 先完成一个最小行动：补水、散步、早睡或减少睡前屏幕时间任选一个。
2. 明天再次记录一次健康或情绪状态，用来判断趋势是否稳定。
3. 如果压力或身体不适持续存在，建议和可信任的人沟通，必要时寻求专业支持。
"""

    health_score = value_or_na(
        health.get("health_score", health.get("overall_score"))
        if health else None,
        language,
    )
    risk_level = value_or_na(health.get("risk_level") if health else None, language)
    mood = value_or_na(mind.get("mood") if mind else None, language)
    stress = value_or_na(mind.get("stress") if mind else None, language)
    energy = value_or_na(mind.get("energy") if mind else None, language)
    focus = value_or_na(health.get("primary_focus") if health else None, language)

    return f"""# Integrated Wellness Report for {username}

## Current Snapshot
- Health score: {health_score}
- Risk level: {risk_level}
- Mood: {mood}
- Stress: {stress}
- Energy: {energy}

## Historical Trend
- Health records: {history_summary["health_record_count"]}
- Mind records: {history_summary["mind_record_count"]}
- Data coverage: {history_summary["data_coverage"]}
- Health trend: {history_summary["health_score_trend"]}
- Stress trend: {history_summary["stress_trend"]}
- Energy trend: {history_summary["energy_trend"]}
- Average health score: {value_or_na(history_summary["average_health_score"], language)}
- Average stress: {value_or_na(history_summary["average_stress"], language)}
- Average energy: {value_or_na(history_summary["average_energy"], language)}

## Integrated Reading
{focus if focus != "N/A" else "There is not enough complete data yet. Complete one health check and one mind reset to make the report more useful."}

Physical health, stress, sleep, movement, and screen habits usually influence each other. If health score is declining while stress is rising, recovery, stress management, and daily movement should be treated as the first priorities.

## Tomorrow's Action Plan
1. Pick one small action: hydration, a short walk, earlier sleep, or less screen time before bed.
2. Log one health or emotional signal again tomorrow to check whether the trend is stable.
3. If stress or physical symptoms persist, talk to someone you trust or seek professional support.
"""

# ── API data adapters ─────────────────────────────
def _api_records_to_health_records(api_items):
    """Convert API health records to legacy format."""
    result = []
    for item in api_items:
        result.append({
            "created_at": item.get("created_at", ""),
            "health_score": item.get("health_score"),
            "risk_level": item.get("risk_level"),
            "risk_percent": item.get("risk_percent"),
            "bmi_score": item.get("bmi_score"),
            "water_score": item.get("water_score"),
            "sleep_score": item.get("sleep_score"),
            "activity_score": item.get("activity_score"),
            "diet_score": item.get("diet_score"),
            "mental_score": item.get("mental_score"),
            "screen_score": item.get("screen_score"),
            "habit_score": item.get("habit_score"),
        })
    return result


def _api_records_to_mind_records(api_items):
    """Convert API emotion records to legacy format. Maps mood_key -> mood."""
    result = []
    for item in api_items:
        result.append({
            "created_at": item.get("created_at", ""),
            "mood": item.get("mood_key", ""),
            "mood_key": item.get("mood_key", ""),
            "event": item.get("event_key", ""),
            "event_key": item.get("event_key", ""),
            "energy": item.get("energy"),
            "stress": item.get("stress"),
            "topic": item.get("pattern_key", ""),
            "pattern_key": item.get("pattern_key", ""),
            "summary": item.get("summary", ""),
        })
    return result


# ── Load data: API first, JSON fallback ───────────
_api_health_data = None
_api_mind_data = None

if BACKEND_AVAILABLE:
    try:
        _api_health_data = health_api.list_records(limit=100).get("items", [])
        _api_mind_data = emotion_api.list_records(limit=100).get("items", [])
    except Exception:
        pass

if _api_health_data is not None:
    health_records = _api_records_to_health_records(_api_health_data)
else:
    health_records = load_json(HEALTH_JSON)
    health_records = filter_user(health_records, user_name)

if _api_mind_data is not None:
    mind_records = _api_records_to_mind_records(_api_mind_data)
else:
    mind_records = load_json(MIND_JSON)
    mind_records = filter_user(mind_records, user_name)

latest_health = get_latest_health(health_records)
latest_mind = get_latest_mind(mind_records)

history_summary = build_history_summary(health_records, mind_records, language)

st.divider()

col1, col2 = st.columns(2)


with col1:

    render_section_label(t["health_snapshot"])

    if latest_health:

        st.metric(
            t["health_score"],
            latest_health.get(
                "health_score",
                latest_health.get(
                    "overall_score",
                    "N/A"
                )
            )
        )

        st.metric(
            t["risk_level"],
            latest_health.get(
                "risk_level",
                "N/A"
            )
        )

        st.metric(
            t["risk_percent"],
            latest_health.get(
                "risk_percent",
                "N/A"
            )
        )

    else:

        st.info(
            t["no_health"]
        )


with col2:

    render_section_label(t["mind_snapshot"])

    if latest_mind:

        st.metric(
            t["mood"],
            latest_mind.get(
                "mood",
                "N/A"
            )
        )

        st.metric(
            t["energy"],
            latest_mind.get(
                "energy",
                "N/A"
            )
        )

        st.metric(
            t["stress"],
            latest_mind.get(
                "stress",
                "N/A"
            )
        )

    else:

        st.info(
            t["no_mind"]
        )

render_section_label(t["history_snapshot"])

h1, h2, h3, h4 = st.columns(4)
h1.metric(t["health_records"], history_summary["health_record_count"])
h2.metric(t["mind_records"], history_summary["mind_record_count"])
h3.metric(t["health_trend"], history_summary["health_score_trend"])
h4.metric(t["stress_trend"], history_summary["stress_trend"])

st.divider()

render_section_label(t["intelligence_snapshot"])

i1, i2, i3, i4 = st.columns(4)
i1.metric(t["data_coverage"], history_summary["data_coverage"])
i2.metric(
    t["average_health"],
    value_or_na(history_summary["average_health_score"], language)
)
i3.metric(
    t["average_stress"],
    value_or_na(history_summary["average_stress"], language)
)
i4.metric(
    t["average_energy"],
    value_or_na(history_summary["average_energy"], language)
)

trend_rows = []

for item in history_summary["health_series"]:
    trend_rows.append({
        "created_at": item["created_at"],
        t["health_score"]: item["health_score"],
    })

for item in history_summary["mind_series"]:
    trend_rows.append({
        "created_at": item["created_at"],
        t["stress"]: item["stress"],
        t["energy"]: item["energy"],
    })

if trend_rows:
    render_section_label(t["trend_chart"])
    trend_df = pd.DataFrame(trend_rows)
    trend_df["created_at"] = pd.to_datetime(
        trend_df["created_at"],
        errors="coerce",
    )
    trend_df = trend_df.dropna(subset=["created_at"]).sort_values("created_at")

    if not trend_df.empty:
        trend_df = trend_df.groupby("created_at").first()
        st.line_chart(trend_df, use_container_width=True)

st.divider()


if latest_health:

    render_section_label(t["radar_title"])

    labels = t["radar_labels"]

    values = [
        latest_health.get("bmi_score", 0),
        latest_health.get("water_score", 0),
        latest_health.get("sleep_score", 0),
        latest_health.get("activity_score", 0),
        latest_health.get("diet_score", 0),
        latest_health.get("mental_score", 0),
        latest_health.get("screen_score", 0),
        latest_health.get("habit_score", 0)
    ]

    # Invert: risk 0 = outer (healthy, value 3.0), risk 3 = inner (value 1.5)
    values = [0 if v is None else v for v in values]
    values = [max(0.5, 3.0 - (float(v) * 0.5)) for v in values]

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False
    ).tolist()

    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(
        figsize=(6, 6),
        subplot_kw=dict(polar=True)
    )

    theta = np.linspace(0, 2*np.pi, 100)

    ax.fill_between(theta, 0, 1,
                    color="#ff6b6b",
                    alpha=0.08)

    ax.fill_between(theta, 1, 2,
                    color="#ffd166",
                    alpha=0.08)

    ax.fill_between(theta, 2, 3,
                    color="#06d6a0",
                    alpha=0.08)

    ax.plot(
        angles,
        values,
        color="#52c41a",
        linewidth=2.5
    )

    ax.fill(
        angles,
        values,
        color="#52c41a",
        alpha=0.2
    )

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    ax.set_ylim(0, 3)

    ax.grid(
        color="#dddddd",
        linestyle="--",
        linewidth=0.7,
        alpha=0.6
    )

    ax.spines['polar'].set_visible(False)

    st.pyplot(
        fig,
        use_container_width=True
    )

    st.caption(
        "🟢 Healthy   🟡 Warning   🔴 Risk"
        if language == "English"
        else "🟢 健康  🟡 警告  🔴 风险"
    )


if not latest_health and not latest_mind:

    st.warning(
        t["no_data"]
    )

else:
    report_style_options = [
        t["style_balanced"],
        t["style_coaching"],
        t["style_clinical"],
    ]
    report_style = st.segmented_control(
        t["report_style"],
        report_style_options,
        default=t["style_balanced"],
    )

    def _api_report_to_markdown(api_result):
        """Convert API report sections back to markdown for display."""
        parts = [api_result["report"]["summary"]]
        for s in api_result["report"]["sections"]:
            parts.append(f"\n## {s['title']}\n{s['content']}")
        return "\n".join(parts).strip()

    if st.button(
        t["generate"],
        use_container_width=True
    ):

        with st.spinner(
            t["loading"]
        ):

            api_success = False
            report = ""

            if BACKEND_AVAILABLE:
                try:
                    api_result = report_api.generate(
                        language=language,
                        style=report_style.lower() if report_style else "balanced",
                        days=7,
                    )
                    report = _api_report_to_markdown(api_result)
                    api_success = True
                    # Detect LocalProvider "no_data" response and fall through
                    # to generate_local_report() which uses locally-loaded data.
                    summary_text = api_result.get("report", {}).get("summary", "") or ""
                    if "not enough" in summary_text.lower() or "没有足够的" in summary_text:
                        api_success = False
                except Exception:
                    st.warning(
                        "Backend report API unavailable, using local fallback."
                        if language == "English"
                        else "后端报告 API 不可用，使用本地回退。"
                    )

            if not api_success:
                report = generate_local_report(
                    user_name,
                    latest_health,
                    latest_mind,
                    history_summary,
                    report_style,
                    language,
                    "gpt-4o-mini",
                )

        render_panel(t["insight_title"])
        st.markdown(report)
        st.session_state["final_report_text"] = report
        st.session_state["final_report_data"] = {
            "latest_health": latest_health,
            "latest_mind": latest_mind,
            "history_summary": history_summary,
        }

if st.session_state.get("final_report_text"):
    report_date = datetime.now().strftime("%Y%m%d")

    col_pdf, col_md = st.columns(2)

    with col_md:
        st.download_button(
            t["download"],
            data=st.session_state["final_report_text"],
            file_name=f"wellnest_report_{user_name}_{report_date}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col_pdf:
        if PDF_AVAILABLE:
            report_data = st.session_state.get("final_report_data", {})
            try:
                pdf_bytes = generate_pdf_report(
                    user_name=user_name,
                    language=language,
                    report_text=st.session_state["final_report_text"],
                    latest_health=report_data.get("latest_health"),
                    latest_mind=report_data.get("latest_mind"),
                    history_summary=report_data.get("history_summary"),
                )
                st.download_button(
                    t["download_pdf"],
                    data=pdf_bytes,
                    file_name=f"wellnest_report_{user_name}_{report_date}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception:
                st.caption(
                    "PDF export unavailable (font rendering issue)"
                    if language == "English"
                    else "PDF 导出不可用（字体渲染问题）"
                )

st.divider()

st.caption(
    t["footer"]
)

if st.button(t["back"], key="final_report_back_home"):
    st.switch_page("web_v1.py")
