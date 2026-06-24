import streamlit as st
from datetime import datetime

from database import save_health_json, save_health_record
from modules.health_analyzer import calculate_overall_result
from modules.bmi import calc_bmi
from modules.water_ratio import calc_water_ratio
from modules.sleep import calc_sleep
from modules.activity import calc_activity
from modules.diet import calc_diet
from modules.mental_healthy import calc_mental_healthy
from modules.screen_time import calc_screen_time
from modules.habit import calc_habit

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

# ── Backend API availability ───────────────────────
BACKEND_AVAILABLE = False
try:
    from api_client.client import ApiClient
    from api_client.health_client import HealthClient

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
except Exception:
    pass

st.set_page_config(
    page_title="Health Check",
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

        "title": "Health Check",
        "subtitle": "Capture today’s core lifestyle signals and turn them into a risk-aware health snapshot.",
        "intro": "Assess your BMI, hydration, sleep, activity, diet, habits, and mental wellness.",

        "unit_note": "\U0001f4cf Unit Guide",
        "bmi_unit": "BMI = weight(kg) / height(m)².",
        "water_unit": "Water intake is measured in litres (L).",
        "sleep_unit": "Sleep is measured in hours per night.",
        "activity_unit": "Exercise is measured in minutes per day.",
        "sedentary_unit": "Sedentary time is measured in hours per day.",
        "diet_unit": "Fruit and vegetables are measured by servings.",
        "screen_unit": "Screen time is measured in hours per day.",

        "weight": "Weight (kg)",
        "height": "Height (cm)",
        "water": "Water intake (L)",

        "sleep_hours": "Sleep hours",
        "night_wake": "Night wake times",

        "exercise_minutes": "Exercise minutes",
        "sedentary_hours": "Sedentary hours",

        "fruit_veg": "Fruit and vegetable servings",
        "fast_food": "Fast food times per week",
        "sugary_drinks": "Sugary drinks per day",
        "screen_time": "Screen time",

        "generate": "Generate Health Report",
        "loading": "Analysing your health data...",

        "health_score": "Health Score",
        "risk_level": "Risk Level",
        "risk_percent": "Risk Percent",

        "module_results": "Module Results",
        "overall_assessment": "Overall Assessment",
        "interaction_risk": "Interaction Risk",
        "priority_focus": "Priority Focus",
        "tomorrow_plan": "Tomorrow Plan",

        "saved": "Health record saved.",

        "score": "Score",
        "reasons": "Reasons",
        "suggestions": "Suggestions",

        "footer": "AI Wellness Platform | Health Module",

        "healthy": "Healthy",
        "low_risk": "Low Risk",
        "medium_risk": "Medium Risk",
        "high_risk": "High Risk",

        "bmi_module": "BMI",
        "water_module": "Water",
        "sleep_module": "Sleep",
        "activity_module": "Activity",
        "diet_module": "Diet",
        "mental_module": "Mental",
        "screen_module": "Screen",
        "habit_module": "Habit",

        "back": "Back to Home",
        "next": "Next: Mind Reset"
    },

    "中文": {

        "title": "健康检测",
        "subtitle": "记录今天的关键生活方式信号，并生成可追踪的健康风险快照。",
        "intro": "评估您的 BMI、饮水、睡眠、运动、饮食、习惯与心理健康。",

        "unit_note": "\U0001f4cf 单位说明",
        "bmi_unit": "BMI = 体重(kg) / 身高(m)²。",
        "water_unit": "饮水量单位为升（L）。",
        "sleep_unit": "睡眠时间单位为每晚小时数。",
        "activity_unit": "运动时间单位为每天分钟数。",
        "sedentary_unit": "九坐时间单位为每天小时数。",
        "diet_unit": "蔬果摄入按“份数”计算。",
        "screen_unit": "屏幕时间单位为每天小时数。",

        "weight": "体重（kg）",
        "height": "身高（cm）",
        "water": "饮水量（L）",

        "sleep_hours": "睡眠时长（小时）",
        "night_wake": "夜间醒来次数",

        "exercise_minutes": "运动时间（分钟）",
        "sedentary_hours": "九坐时间（小时）",

        "fruit_veg": "蔬果份数",
        "fast_food": "每周快餐次数",
        "sugary_drinks": "每日含糖饮料",
        "screen_time": "屏幕时间（小时）",

        "generate": "生成健康报告",
        "loading": "正在分析健康数据...",

        "health_score": "健康评分",
        "risk_level": "风险等级",
        "risk_percent": "风险百分比",

        "module_results": "模块结果",
        "overall_assessment": "综合评估",
        "interaction_risk": "交互风险",
        "priority_focus": "优先关注",
        "tomorrow_plan": "明日计划",

        "saved": "健康记录已保存。",

        "score": "分数",
        "reasons": "原因",
        "suggestions": "建议",

        "footer": "AI健康平台 | 健康模块",

        "healthy": "健康",
        "low_risk": "低风险",
        "medium_risk": "中风险",
        "high_risk": "高风险",

        "bmi_module": "BMI",
        "water_module": "饮水",
        "sleep_module": "睡眠",
        "activity_module": "运动",
        "diet_module": "饮食",
        "mental_module": "心理",
        "screen_module": "屏幕",
        "habit_module": "习惯",

        "back": "返回首页",
        "next": "下一步：情绪重整"
    }
}

t = TEXT[language]

# ── Bilingual label maps for form widgets ────────────
SITUATION_MAP = {
    "English": {"A": "A - Normal daily condition", "B": "B - Exercised or sweating", "C": "C - Hot weather", "D": "D - Heavy exercise in hot weather"},
    "中文": {"A": "A - 普通日常状态", "B": "B - 有运动或出汗", "C": "C - 天气炎热", "D": "D - 炎热天气下大量运动"},
}
THIRST_MAP = {
    "English": {"A": "A - Rarely", "B": "B - Sometimes", "C": "C - Frequently"},
    "中文": {"A": "A - 很少", "B": "B - 偶尔", "C": "C - 经常"},
}
URINE_MAP = {
    "English": {"A": "A - Light / clear", "B": "B - Normal yellow", "C": "C - Dark yellow"},
    "中文": {"A": "A - 较淡 / 接近透明", "B": "B - 正常黄色", "C": "C - 深黄色"},
}
DIFFICULTY_SLEEP_MAP = {
    "English": {"A": "A - Rarely", "B": "B - Sometimes", "C": "C - Frequently"},
    "中文": {"A": "A - 很少", "B": "B - 偶尔", "C": "C - 经常"},
}
SCHEDULE_MAP = {
    "English": {"A": "A - Very regular", "B": "B - Occasionally irregular", "C": "C - Frequently irregular"},
    "中文": {"A": "A - 非常规律", "B": "B - 偶尔不规律", "C": "C - 经常不规律"},
}
FREQ_MAP = {
    "English": {"A": "A - Never", "B": "B - Occasionally", "C": "C - Frequently"},
    "中文": {"A": "A - 从不", "B": "B - 偶尔", "C": "C - 经常"},
}
LATE_MAP = {
    "English": {"A": "A - Rarely or never", "B": "B - Sometimes", "C": "C - Frequently"},
    "中文": {"A": "A - 几乎不会", "B": "B - 偶尔", "C": "C - 经常"},
}
EMOTION_MAP = {
    "English": {"A": "A - Mostly positive and emotionally stable", "B": "B - Sometimes low, stressed, or irritable", "C": "C - Frequently anxious, overwhelmed, or emotionally exhausted"},
    "中文": {"A": "A - 大多数时候积极且稳定", "B": "B - 偶尔低落、烦躁或压力较大", "C": "C - 经常焦虑、情绪崩溃或精神疲惫"},
}
FOCUS_MAP = {
    "English": {"A": "A - Able to focus well most of the time", "B": "B - Sometimes distracted or mentally tired", "C": "C - Frequently unable to focus"},
    "中文": {"A": "A - 大部分时间都能保持专注", "B": "B - 偶尔容易分心或精神疲惫", "C": "C - 经常难以集中注意力"},
}
BODY_MAP = {
    "English": {"A": "A - Rarely", "B": "B - Sometimes, such as headache, fatigue, or muscle tension", "C": "C - Frequently"},
    "中文": {"A": "A - 很少", "B": "B - 偶尔，如头痛、疲劳或身体紧绷", "C": "C - 经常"},
}
SITUATION_LABELS = {"English": "Please choose your condition today:", "中文": "请选择你今天的情况："}
THIRST_LABELS = {"English": "How often do you feel thirsty?", "中文": "你多久会感觉口渴？"}
URINE_LABELS = {"English": "Which of the following best describes your urine color?", "中文": "以下哪项最符合你的尿液颜色？"}
DIFFICULTY_LABELS = {"English": "How often do you have difficulty falling asleep?", "中文": "你多久会出现入睡困难？"}
SCHEDULE_LABELS = {"English": "How regular is your sleep schedule?", "中文": "你的作息规律程度如何？"}
SMOKING_LABELS = {"English": "How often do you smoke?", "中文": "你多久会吸烟？"}
ALCOHOL_LABELS = {"English": "How often do you drink alcohol?", "中文": "你多久会饮酒？"}
LATE_LABELS = {"English": "How often do you stay up late?", "中文": "你多久会熬夜？"}
EMOTION_LABELS = {"English": "How would you describe your mood recently?", "中文": "你最近的情绪状态如何？"}
FOCUS_LABELS = {"English": "How has your concentration been recently?", "中文": "你最近的专注力如何？"}
BODY_LABELS = {"English": "Do you experience stress-related physical symptoms?", "中文": "你是否有压力带来的身体反应？"}

render_topbar(language, user_name)
render_nav(language, "pages/1_Health_Check.py")
render_hero(
    t["title"],
    t["subtitle"],
    "Health intake" if language == "English" else "健康录入",
    t["intro"],
)

render_medical_disclaimer(language)

if st.button(t["back"], key="top_back_home"):
    st.switch_page("web_v1.py")

with st.expander(t["unit_note"]):
    st.write("-", t["bmi_unit"])
    st.write("-", t["water_unit"])
    st.write("-", t["sleep_unit"])
    st.write("-", t["activity_unit"])
    st.write("-", t["sedentary_unit"])
    st.write("-", t["diet_unit"])
    st.write("-", t["screen_unit"])

render_section_label("Daily inputs" if language == "English" else "今日数据")

col1, col2 = st.columns(2)

with col1:
    weight_kg = st.number_input(
        t["weight"],
        30.0,
        300.0,
        70.0
    )

    height_cm = st.number_input(
        t["height"],
        100.0,
        250.0,
        170.0
    )

    water_l = st.number_input(
        t["water"],
        0.0,
        10.0,
        2.0
    )

    situation = st.radio(
        SITUATION_LABELS[language],
        ["A", "B", "C", "D"],
        format_func=lambda x: SITUATION_MAP[language][x]
    )

    thirst_level = st.radio(
        THIRST_LABELS[language],
        ["A", "B", "C"],
        format_func=lambda x: THIRST_MAP[language][x]
    )

    urine_color = st.radio(
        URINE_LABELS[language],
        ["A", "B", "C"],
        format_func=lambda x: URINE_MAP[language][x]
    )

    sleep_hours = st.slider(
        t["sleep_hours"],
        0.0,
        12.0,
        7.0
    )

    night_wake_times = st.slider(
        t["night_wake"],
        0,
        10,
        1
    )

    difficulty_falling_asleep = st.radio(
        DIFFICULTY_LABELS[language],
        ["A", "B", "C"],
        format_func=lambda x: DIFFICULTY_SLEEP_MAP[language][x]
    )

    irregular_sleep_schedule = st.radio(
        SCHEDULE_LABELS[language],
        ["A", "B", "C"],
        format_func=lambda x: SCHEDULE_MAP[language][x]
    )

with col2:

    exercise_minutes = st.slider(
        t["exercise_minutes"],
        0,
        180,
        30
    )

    sedentary_hours = st.slider(
        t["sedentary_hours"],
        0,
        16,
        6
    )

    fruit_veg_servings = st.slider(
        t["fruit_veg"],
        0,
        10,
        3
    )
    st.caption({
        "English": "1 serving \u2248 1 medium fruit or 1/2 cup vegetables.",
        "中文": "1份 ≈ 1个中等水果或半杯蔬菜。"
    }[language])

    fast_food_times = st.slider(
        t["fast_food"],
        0,
        14,
        1
    )
    st.caption({
        "English": "Includes: burgers, fried chicken, pizza, instant food, takeaway meals, etc.",
        "中文": "包括：汉堡、炸鸡、披萨、方便食品、外卖等。"
    }[language])

    sugary_drinks = st.slider(
        t["sugary_drinks"],
        0,
        10,
        1
    )
    st.caption({
        "English": "Includes: soft drinks, bubble tea, energy drinks, sweetened juice, etc.",
        "中文": "包括：汽水、奶茶、能量饮料、含糖果汁等。"
    }[language])

    screen_time_hours = st.slider(
        t["screen_time"],
        0.0,
        24.0,
        5.0
    )

    smoking = st.radio(
        SMOKING_LABELS[language],
        ["A", "B", "C"],
        format_func=lambda x: FREQ_MAP[language][x]
    )

    alcohol = st.radio(
        ALCOHOL_LABELS[language],
        ["A", "B", "C"],
        format_func=lambda x: FREQ_MAP[language][x]
    )

    late_night = st.radio(
        LATE_LABELS[language],
        ["A", "B", "C"],
        format_func=lambda x: LATE_MAP[language][x]
    )

    risk_score_emotion = st.radio(
        EMOTION_LABELS[language],
        ["A", "B", "C"],
        format_func=lambda x: EMOTION_MAP[language][x]
    )

    risk_score_focus = st.radio(
        FOCUS_LABELS[language],
        ["A", "B", "C"],
        format_func=lambda x: FOCUS_MAP[language][x]
    )

    risk_score_body = st.radio(
        BODY_LABELS[language],
        ["A", "B", "C"],
        format_func=lambda x: BODY_MAP[language][x]
    )

def _adapt_api_response(api_result):
    """Convert API response to the format expected by the display code below."""
    modules_list = []
    for name, data in api_result.get("modules", {}).items():
        modules_list.append({
            "name": name,
            "score": data["score"],
            "level": data["level"],
            "max_score": 3,
            "reasons": data.get("reasons", []),
            "suggestions": data.get("suggestions", []),
        })
    overall_result = {
        "health_score": api_result["health_score"],
        "risk_percent": api_result["risk_percent"],
        "risk_level": api_result["risk_level"],
        "risk_score": sum(m["score"] for m in modules_list),
        "max_risk_score": len(modules_list) * 3,
        "interaction_score": 0,
        "interaction_notes": [],
        "overall": api_result.get("overall", ""),
        "primary_focus": api_result.get("primary_focus", ""),
        "action_plan": api_result.get("action_plan", []),
    }
    return modules_list, overall_result


if st.button(t["generate"], use_container_width=True):

    with st.spinner(t["loading"]):

        api_success = False
        if BACKEND_AVAILABLE:
            try:
                payload = {
                    "language": language,
                    "weight_kg": weight_kg, "height_cm": height_cm, "water_l": water_l,
                    "situation": situation, "thirst_level": thirst_level, "urine_color": urine_color,
                    "sleep_hours": sleep_hours, "night_wake_times": night_wake_times,
                    "difficulty_falling_asleep": difficulty_falling_asleep,
                    "irregular_sleep_schedule": irregular_sleep_schedule,
                    "exercise_minutes": exercise_minutes, "sedentary_hours": sedentary_hours,
                    "fruit_veg_servings": fruit_veg_servings, "fast_food_times": fast_food_times,
                    "sugary_drinks": sugary_drinks, "screen_time_hours": screen_time_hours,
                    "smoking": smoking, "alcohol": alcohol, "late_night": late_night,
                    "risk_score_emotion": risk_score_emotion,
                    "risk_score_focus": risk_score_focus,
                    "risk_score_body": risk_score_body,
                }
                api_result = health_api.check(**payload)
                results, overall_result = _adapt_api_response(api_result)
                api_success = True
            except Exception:
                pass

        if not api_success:
            # Legacy fallback: run 8 engines locally
            bmi_result = calc_bmi(weight_kg, height_cm, language)
            water_result = calc_water_ratio(water_l, situation, weight_kg, thirst_level, urine_color, language)
            sleep_result = calc_sleep(sleep_hours, night_wake_times, difficulty_falling_asleep, irregular_sleep_schedule, language)
            activity_result = calc_activity(exercise_minutes, sedentary_hours, language)
            diet_result = calc_diet(fruit_veg_servings, fast_food_times, sugary_drinks, language)
            mental_result = calc_mental_healthy(risk_score_emotion, risk_score_focus, risk_score_body, language)
            screen_result = calc_screen_time(screen_time_hours, language)
            habit_result = calc_habit(smoking, alcohol, late_night, language)

            results = [
                bmi_result, water_result, sleep_result, activity_result,
                diet_result, mental_result, screen_result, habit_result,
            ]

            overall_result = calculate_overall_result(results, language)

        overall_score = overall_result["health_score"]
        risk_percent = overall_result["risk_percent"]
        overall_level = overall_result["risk_level"]
        interaction_score = overall_result["interaction_score"]
        interaction_notes = overall_result["interaction_notes"]
        overall_summary = overall_result["overall"]
        primary_focus = overall_result["primary_focus"]
        action_plan = overall_result["action_plan"]

        module_scores = {
            r.get("name"): r.get("score")
            for r in results
            if isinstance(r, dict)
        }

        record = {
            "user_name": user_name,
            "username": user_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "health_score": overall_score,
            "overall_score": overall_score,
            "risk_percent": risk_percent,
            "risk_level": overall_level,
            "risk_score": overall_result["risk_score"],
            "max_risk_score": overall_result["max_risk_score"],
            "interaction_score": interaction_score,
            "interaction_notes": interaction_notes,
            "summary": overall_summary,
            "primary_focus": primary_focus,
            "action_plan": action_plan,
            "bmi_score": module_scores.get("BMI"),
            "water_score": module_scores.get("Water"),
            "sleep_score": module_scores.get("Sleep"),
            "activity_score": module_scores.get("Activity"),
            "diet_score": module_scores.get("Diet"),
            "mental_score": module_scores.get("Mental"),
            "screen_score": module_scores.get("Screen"),
            "habit_score": module_scores.get("Habit"),
            "source": "api" if api_success else "local",
        }

        try:
            save_health_json(record)
            save_health_record(record)
        except Exception as exc:
            st.error(
                f"Failed to save health record: {exc}"
                if language == "English"
                else f"健康记录保存失败：{exc}"
            )
            st.stop()

        st.success(t["saved"])

        col1, col2, col3 = st.columns(3)

        col1.metric(
            t["health_score"],
            overall_score
        )

        if overall_level in [t["healthy"]]:

            risk_color = "#22c55e"
            risk_bg = "#dcfce7"

        elif overall_level in [t["low_risk"]]:

            risk_color = "#eab308"
            risk_bg = "#fef9c3"

        elif overall_level in [t["medium_risk"]]:

            risk_color = "#f97316"
            risk_bg = "#ffedd5"

        else:

            risk_color = "#ef4444"
            risk_bg = "#fee2e2"

        with col2:

            st.markdown(f"""
            <div style="
                background:{risk_bg};
                padding:25px;
                border-radius:16px;
                border-left:8px solid {risk_color};
                text-align:center;
            ">

            <div style="
                font-size:18px;
                color:#555;
                margin-bottom:10px;
            ">
                {t["risk_level"]}
            </div>

            <div style="
                font-size:42px;
                font-weight:700;
                color:{risk_color};
            ">
                {overall_level}
            </div>

            </div>
            """, unsafe_allow_html=True)

        col3.metric(
            t["risk_percent"],
            f"{risk_percent}%"
        )

        st.divider()

        render_panel(t["overall_assessment"], overall_summary)
        render_panel(t["priority_focus"], primary_focus)

        render_section_label(t["tomorrow_plan"])
        for action in action_plan:
            st.write("-", action)

        if interaction_notes:
            render_section_label(t["interaction_risk"])
            for note in interaction_notes:
                st.write("-", note)

        st.divider()

        render_section_label(t["module_results"])

        module_name_map = {
            "BMI": t["bmi_module"],
            "Water": t["water_module"],
            "Sleep": t["sleep_module"],
            "Activity": t["activity_module"],
            "Diet": t["diet_module"],
            "Mental": t["mental_module"],
            "Screen": t["screen_module"],
            "Habit": t["habit_module"]
        }

        level_map = {
            "Healthy": t["healthy"],
            "Low Risk": t["low_risk"],
            "Medium Risk": t["medium_risk"],
            "High Risk": t["high_risk"],
            "健康": t["healthy"],
            "低风险": t["low_risk"],
            "中风险": t["medium_risk"],
            "高风险": t["high_risk"]
        }

        for r in results:

            module_name = module_name_map.get(
                r["name"],
                r["name"]
            )

            module_level = level_map.get(
                r["level"],
                r["level"]
            )

            with st.expander(
                f'{module_name} - {module_level}'
            ):

                st.write(
                    f'{t["score"]}:',
                    r["score"]
                )

                st.write(
                    f'{t["reasons"]}:'
                )

                for reason in r["reasons"]:
                    st.write("-", reason)

                st.write(
                    f'{t["suggestions"]}:'
                )

                for suggestion in r["suggestions"]:
                    st.write("-", suggestion)

st.divider()

st.caption(t["footer"])

if st.button(
    t["next"],
    key="health_next_mind",
    use_container_width=True
):
    st.switch_page("pages/2_Mind_Reset.py")
