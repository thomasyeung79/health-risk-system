import streamlit as st
from datetime import datetime

from database import save_mind_record
from modules.reflection_engine import run_reflection_engine
from modules.ui import (
    apply_product_theme,
    require_auth,
    require_user,
    render_hero,
    render_medical_disclaimer,
    render_nav,
    render_panel,
    render_section_label,
    render_topbar,
)
from modules.emotion_localization import MOOD_LABELS, localize_emotion

# ── Backend API availability ───────────────────────
BACKEND_AVAILABLE = False
try:
    from api_client.client import ApiClient
    from api_client.emotion_client import EmotionClient

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
        emotion_api = EmotionClient(_client)
except Exception:
    pass


st.set_page_config(
    page_title="Reflection",
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
        "title": "Reflection",
        "subtitle": "Turn mood, stress, and energy signals into a clear emotional reset plan.",
        "intro": "Check your mood, stress, energy, and receive structured guidance.",

        "mood": "Current mood",
        "event": "What happened today?",
        "energy": "Energy level",
        "stress": "Stress level",

        "energy_note": "1 = Extremely tired   |   10 = Very energetic",
        "stress_note": "1 = Very relaxed   |   10 = Extremely stressed",

        "generate": "Generate Reset Insight",
        "loading": "Analysing your emotional state...",
        "saved": "Saved successfully.",

        "back": "Back to Home",
        "next": "Next: Wellness History",

        "insight_title": "AI Reset Insight",
        "matched_topic": "Matched Topic",
        "emotional_summary": "Emotional Summary",
        "pattern": "Detected Emotional Pattern",
        "tonight": "Tonight",
        "tomorrow": "Tomorrow",
        "reflection_support": "Reflection Support",
        "practice_step": "Practice Step",
        "breathing": "Breathing Practice",
        "breathing_steps": "Breathing Steps",
        "full_story": "Full Reflection Story",

        "mood_metric": "Mood",
        "energy_metric": "Energy",
        "stress_metric": "Stress",

        "footer": "AI Wellness Platform | Reflection Module"
    },

    "中文": {
        "title": "反思",
        "subtitle": "把情绪、压力和能量状态转化为清晰的自我重整计划。",
        "intro": "记录你的情绪、压力和能量状态，获得结构化引导。",

        "mood": "当前情绪",
        "event": "今天发生了什么？",
        "energy": "能量水平",
        "stress": "压力水平",

        "energy_note": "1 = 非常疲惫   |   10 = 精力充沛",
        "stress_note": "1 = 非常放松   |   10 = 压力极大",

        "generate": "生成情绪重整建议",
        "loading": "正在分析你的情绪状态...",
        "saved": "记录已保存。",

        "back": "返回首页",
        "next": "下一步：历史记录",

        "insight_title": "AI情绪分析",
        "matched_topic": "匹配主题",
        "emotional_summary": "情绪总结",
        "pattern": "识别到的情绪模式",
        "tonight": "今晚",
        "tomorrow": "明天",
        "reflection_support": "反思支持",
        "practice_step": "实践步骤",
        "breathing": "呼吸练习",
        "breathing_steps": "呼吸步骤",
        "full_story": "完整情绪反思",

        "mood_metric": "情绪",
        "energy_metric": "能量",
        "stress_metric": "压力",

        "footer": "AI健康与情绪系统 | 情绪模块"
    }
}

t = TEXT[language]


EVENT_LABELS = {
    "English": {
        "Nothing special": "Nothing special",
        "Had a long day": "Had a long day",
        "Academic or work-related issue": "Academic or work-related issue",
        "Argued with someone": "Argued with someone",
        "Felt lonely": "Felt lonely",
        "Felt overwhelmed": "Felt overwhelmed"
    },
    "中文": {
        "Nothing special": "没什么特别的事",
        "Had a long day": "今天很漫长很累",
        "Academic or work-related issue": "学习或工作压力",
        "Argued with someone": "和别人发生争执",
        "Felt lonely": "感到孤独",
        "Felt overwhelmed": "感到被压垮"
    }
}


render_topbar(language, user_name)
render_nav(language, "pages/2_Mind_Reset.py")
render_hero(
    t["title"],
    t["subtitle"],
    "Emotional check-in" if language == "English" else "情绪签到",
    t["intro"],
)

render_medical_disclaimer(language)

if st.button(t["back"], key="mind_back_home"):
    st.switch_page("web_v1.py")


render_section_label("Current state" if language == "English" else "当前状态")

col1, col2 = st.columns(2)

with col1:

    mood_key = st.selectbox(
        t["mood"],
        list(MOOD_LABELS[language].keys()),
        format_func=lambda x: MOOD_LABELS[language][x]
    )

    event_key = st.selectbox(
        t["event"],
        list(EVENT_LABELS[language].keys()),
        format_func=lambda x: EVENT_LABELS[language][x]
    )

with col2:

    energy = st.slider(
        t["energy"],
        1,
        10,
        5
    )

    st.caption(t["energy_note"])

    stress = st.slider(
        t["stress"],
        1,
        10,
        5
    )

    st.caption(t["stress_note"])


st.divider()

def _adapt_emotion_api_response(api_result):
    """Minimal adapter: API uses full_story, legacy UI expects story."""
    api_result["story"] = api_result.pop("full_story")
    return api_result


if st.button(t["generate"], use_container_width=True):

    with st.spinner(t["loading"]):

        api_success = False
        result = None

        if BACKEND_AVAILABLE:
            try:
                api_raw = emotion_api.analyze(
                    language=language,
                    mood_key=mood_key,
                    event_key=event_key,
                    energy=energy,
                    stress=stress,
                )
                result = _adapt_emotion_api_response(api_raw)
                api_success = True
            except Exception:
                pass

        if not api_success:
            result = run_reflection_engine(
                clean_mood=[mood_key],
                clean_things=[event_key],
                stress_level=stress,
                energy_level=energy,
                language=language,
            )

    mood_display = localize_emotion(mood_key, language)
    event_display = EVENT_LABELS[language][event_key]

    record = {
        "username": user_name,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "language": language,

        "mood": mood_display,
        "mood_key": mood_key,

        "event": event_display,
        "event_key": event_key,

        "energy": energy,
        "stress": stress,

        "topic": result["matched_topic"],
        "summary": result["summary"],
        "pattern": result["pattern"],
        "tonight": result["tonight"],
        "tomorrow": result["tomorrow"],
        "guidance": result["guidance"],
        "breathing": result["breathing"],
        "story": result["story"]
    }

    if not api_success:
        save_mind_record(record)

    st.success(t["saved"])

    col1, col2, col3 = st.columns(3)

    col1.metric(t["mood_metric"], mood_display)
    col2.metric(t["energy_metric"], f"{energy}/10")
    col3.metric(t["stress_metric"], f"{stress}/10")

    st.divider()

    render_panel(t["insight_title"])

    st.markdown(f"""
### {t["matched_topic"]}
**{result["matched_topic"]}**

### {t["pattern"]}
**{result["pattern"]["pattern"]}**  
{result["pattern"]["message"]}

### {t["emotional_summary"]}
{result["summary"]}

### {t["tonight"]}
{result["tonight"]}

### {t["tomorrow"]}
{result["tomorrow"]}

### {t["reflection_support"]}
{result["guidance"]["support"]}

### {t["practice_step"]}
{result["guidance"]["practice"]}

### {t["breathing"]}
**{result["breathing"]["title"]}**  
{result["breathing"]["purpose"]}
""")

    with st.expander(t["breathing_steps"]):
        for step in result["breathing"]["steps"]:
            st.write("-", step)

    with st.expander(t["full_story"]):
        st.markdown(result["story"])


st.divider()

st.caption(t["footer"])

if st.button(
    t["next"],
    key="mind_next_history",
    use_container_width=True
):
    st.switch_page("pages/3_Wellness_History.py")
