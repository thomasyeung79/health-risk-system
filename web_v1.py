from bmi import calc_bmi
from water_ratio import calc_water_ratio
from sleep import calc_sleep
from activity import calc_activity
from diet import calc_diet
from mental_healthy import calc_mental_healthy
from screen_time import calc_screen_time
from habit import calc_habit

import streamlit as st
import mysql.connector
import pandas as pd

st.set_page_config(page_title="AI Health Risk System", layout="wide")

st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

div[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #e9ecef;
    padding: 12px;
    border-radius: 14px;
}

h1, h2, h3 {
    color: #212529;
}
</style>
""", unsafe_allow_html=True)

USE_DB = True

def connect_database():
    return mysql.connector.connect(
        host=st.secrets["MYSQLHOST"],
        user=st.secrets["MYSQLUSER"],
        password=st.secrets["MYSQLPASSWORD"],
        database=st.secrets["MYSQLDATABASE"],
        port=int(st.secrets["MYSQLPORT"])
    )

def save_to_db(user_name, result):
    db = connect_database()
    cursor = db.cursor()

    sql = """
        INSERT INTO healthy_records_web (
            user_name,
            bmi,
            water_ratio,
            sleep_score,
            activity_score,
            diet_score,
            mental_score,
            screen_metric,
            habit_score,
            interaction_score,
            risk_score,
            risk_percent,
            health_score,
            risk_level,
            summary
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        user_name,
        result["metrics"]["BMI"],
        result["metrics"]["Water"],
        result["metrics"]["Sleep"],
        result["metrics"]["Activity"],
        result["metrics"]["Diet"],
        result["metrics"]["Mental"],
        result["metrics"]["Screen"],
        result["metrics"]["Habit"],
        result["interaction_score"],
        result["risk_score"],
        result["risk_percent"],
        result["health_score"],
        result["risk_level"],
        result["summary"]
    )

    cursor.execute(sql, values)
    db.commit()
    cursor.close()
    db.close()

def get_history(user_name):
    conn = connect_database()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT created_at, health_score, risk_level, risk_percent
    FROM healthy_records_web
    WHERE user_name = %s
    ORDER BY created_at DESC
    LIMIT 20
    """
    
    cursor.execute(query, (user_name,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

def run_web_assessment(
    weight_kg,
    height_cm,
    water_ml,
    situation,
    sleep_hours,
    night_wake_times,
    exercise_minutes,
    sedentary_hours,
    fruit_veg_servings,
    fast_food_times,
    sugary_drinks,
    risk_score_emotion,
    risk_score_focus,
    risk_score_body,
    screen_time_hours,
    smoking,
    alcohol,
    late_night
):
    modules = []

    bmi_result = calc_bmi(weight_kg, height_cm)
    modules.append(bmi_result)

    water_result = calc_water_ratio(water_ml, situation, weight_kg)
    modules.append(water_result)

    sleep_result = calc_sleep(sleep_hours, night_wake_times)
    modules.append(sleep_result)

    activity_result = calc_activity(exercise_minutes, sedentary_hours)
    modules.append(activity_result)

    diet_result = calc_diet(fruit_veg_servings, fast_food_times, sugary_drinks)
    modules.append(diet_result)

    mental_result = calc_mental_healthy(risk_score_emotion, risk_score_focus, risk_score_body)
    modules.append(mental_result)

    screen_result = calc_screen_time(screen_time_hours)
    modules.append(screen_result)

    habit_result = calc_habit(smoking, alcohol, late_night)
    modules.append(habit_result)

    scores = {m["name"]: m.get("score", 0) for m in modules}
    metrics = {m["name"]: m.get("metric_value", 0) for m in modules}
    levels = {m["name"]: m.get("level", "") for m in modules}

    get_score = lambda name: scores.get(name, 0)
    get_metric = lambda name: metrics.get(name, 0)
    get_level = lambda name: levels.get(name, "")

    risk_score = sum(m["score"] for m in modules)
    max_risk_score = sum(m["max_score"] for m in modules)

    interaction_score = 0
    interaction_notes = []

    if get_score("Sleep") >= 2 and get_score("Mental") >= 1:
        interaction_score += 2
        interaction_notes.append("Sleep and mental stress may be reinforcing each other.")
    if get_score("Mental") >= 2 and get_score("Activity") >= 2:
        interaction_score += 2
        interaction_notes.append("Stress and inactivity may create a negative cycle.")
    if get_score("Diet") >= 2 and get_score("Activity") >= 2:
        interaction_score += 1
        interaction_notes.append("Poor diet and low activity together may increase long-term health risks.")
    if get_score("BMI") > 0 and get_score("Water") > 0:
        interaction_score += 1
        interaction_notes.append("Weight and hydration issues may be related and affect overall health.")
    if get_score("Screen") >= 2 and get_score("Sleep") >= 2:
        interaction_score += 1
        interaction_notes.append("High screen time may be contributing to poor sleep.")
    if get_score("Screen") >= 2 and get_score("Mental") >= 1:
        interaction_score += 1
        interaction_notes.append("High screen time may increase mental stress.")
    if get_score("Habit") >= 2 and get_score("Sleep") >= 2:
        interaction_score += 1
        interaction_notes.append("Unhealthy habits may be contributing to poor sleep quality.")
    if get_score("Habit") >= 2 and get_score("Mental") >= 1:
        interaction_score += 1
        interaction_notes.append("Unhealthy habits may be affecting mental well-being.")

    interaction_notes = list(dict.fromkeys(interaction_notes))
    interaction_score = min(interaction_score, 4)

    risk_score += interaction_score
    max_risk_score += 4

    risk_percent = round((risk_score / max_risk_score) * 100, 1)
    health_score = round(100 - risk_percent, 1)

    if risk_percent >= 66:
        risk_level = "High risk"
        overall = "Multiple health risks were detected. Immediate action is advised."
    elif risk_percent >= 33:
        risk_level = "Medium risk"
        overall = "Some health risks were identified. Improvements are recommended."
    else:
        risk_level = "Low risk"
        overall = "Your overall health is in a good condition."

    red_flags = []
    main_concerns = []
    lifestyle = []

    if get_score("Mental") >= 2:
        red_flags.append("Mental stress is high and may impact overall health.")
    elif get_score("Mental") > 0:
        main_concerns.append("Mental well-being could be improved.")
    else:
        lifestyle.append("Maintain your current mental well-being.")

    if get_score("Sleep") >= 2:
        red_flags.append("Poor sleep quality may affect recovery and daily performance.")
    elif get_score("Sleep") > 0:
        main_concerns.append("Sleep quality could be improved.")
    else:
        lifestyle.append("Maintain your current healthy sleep routine.")

    if get_score("Screen") >= 2:
        red_flags.append("Excessive screen time may affect sleep and mental health.")
    elif get_score("Screen") > 0:
        main_concerns.append("Screen time could be reduced.")
    else:
        lifestyle.append("Maintain your current screen habits.")

    if get_score("Activity") >= 2:
        red_flags.append("Insufficient physical activity may increase health risks.")
    elif get_score("Activity") > 0:
        main_concerns.append("Physical activity levels could be improved.")
    else:
        lifestyle.append("Maintain your current activity level.")

    if get_score("Diet") >= 2:
        red_flags.append("Unhealthy dietary habits may increase long-term health risks.")
    elif get_score("Diet") > 0:
        main_concerns.append("Diet quality could be improved.")
    else:
        lifestyle.append("Maintain your current healthy diet.")

    if get_score("Water") >= 2:
        red_flags.append("Low hydration levels may affect physical performance.")
    elif get_score("Water") > 0:
        main_concerns.append("Hydration could be improved.")
    else:
        lifestyle.append("Maintain your current hydration habits.")

    if get_score("BMI") >= 2:
        red_flags.append("BMI is outside the healthy range and may increase health risks.")
    elif get_score("BMI") > 0:
        main_concerns.append("BMI needs attention.")
    else:
        lifestyle.append("Maintain your current healthy weight.")

    if get_score("Habit") >= 2:
        red_flags.append("Unhealthy habits may increase long-term health risks.")
    elif get_score("Habit") > 0:
        main_concerns.append("Lifestyle habits could be improved.")
    else:
        lifestyle.append("Maintain your current healthy lifestyle habits.")

    if interaction_score >= 3:
        red_flags.append("Multiple lifestyle factors are interacting and increasing overall health risks.")
    elif interaction_score >= 1:
        main_concerns.append("Some health factors may be interacting and should be monitored.")

    red_flags = list(dict.fromkeys(red_flags))
    main_concerns = list(dict.fromkeys(main_concerns))
    lifestyle = list(dict.fromkeys(lifestyle))

    summary_parts = [f"Overall assessment: {overall}"]
    if red_flags:
        summary_parts.append("High-priority issues include: " + ", ".join(red_flags[:2]) + ".")
    if main_concerns:
        summary_parts.append("Key areas for improvement include: " + ", ".join(main_concerns[:2]) + ".")
    if lifestyle:
        summary_parts.append("Recommendations: " + ", ".join(lifestyle[:2]) + ".")

    summary = "\n".join(summary_parts)

    return {
        "risk_level": risk_level,
        "health_score": health_score,
        "risk_percent": risk_percent,
        "risk_score": risk_score,
        "interaction_score": interaction_score,
        "summary": summary,
        "red_flags": red_flags,
        "main_concerns": main_concerns,
        "lifestyle": lifestyle,
        "metrics": {
            "BMI": get_metric("BMI"),
            "Water": get_metric("Water"),
            "Sleep": get_metric("Sleep"),
            "Activity": get_metric("Activity"),
            "Diet": get_metric("Diet"),
            "Mental": get_metric("Mental"),
            "Screen": get_metric("Screen"),
            "Habit": get_metric("Habit"),
        },
        "levels": {
            "BMI": get_level("BMI"),
            "Water": get_level("Water"),
            "Sleep": get_level("Sleep"),
            "Activity": get_level("Activity"),
            "Diet": get_level("Diet"),
            "Mental": get_level("Mental"),
            "Screen": get_level("Screen"),
            "Habit": get_level("Habit"),
        }
    }

st.markdown("""
    <style>
    .main {
        padding-top: 1.5rem;
    }

    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e5e7eb;
        padding: 15px;
        border-radius: 12px;
    }

    div.stAlert {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.header-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
    border: 1px solid #e9ecef;
    border-radius: 20px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.header-title {
    font-size: 42px;
    font-weight: 800;
    color: #212529;
    margin-bottom: 8px;
}
.header-subtitle {
    font-size: 16px;
    color: #6c757d;
    margin-bottom: 16px;
}
.header-badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: #eef7ff;
    color: #2b6cb0;
    font-size: 14px;
    font-weight: 600;
}
.small-hero-img img {
    border-radius: 18px;
    max-height: 220px;
    object-fit: cover;
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
}
</style>
""", unsafe_allow_html=True)

left, right = st.columns([1.8, 1])

with left:
    st.markdown("""
    <div class="header-card">
        <div class="header-title">🧠 AI Health Risk System</div>
        <div class="header-subtitle">Understand your health in 60 seconds</div>
        <div class="header-badge">Lifestyle-based health assessment</div>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="small-hero-img">', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1505751172876-fa1923c5c528", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
st.info("Enter your lifestyle data to get a quick health risk assessment and personalised insights.")
st.markdown("---")

user_name = st.text_input("👤 Enter your user name:")

if not user_name:
    st.info("👆 Please enter your name to start the assessment.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="
        background:white;
        padding:20px;
        border-radius:16px;
        border:1px solid #e9ecef;
        margin-bottom:20px;
    ">

    <div style="
        font-size:20px;
        font-weight:700;
        margin-bottom:12px;
    ">
    🩺 Basic Health Information
    </div>

    <div style="
        font-size:14px;
        color:#6c757d;
        margin-bottom:12px;
    ">
    Enter your basic body information
    </div>

    <hr style="margin:10px 0; border:none; border-top:1px solid #eee;">
    
    """, unsafe_allow_html=True)
    
    st.subheader("🧍 Personal Information")
    st.caption("Enter your basic body information.")
    weight_kg = st.number_input("Weight (kg):", min_value=30.0, max_value=300.0, value=70.0)
    st.caption("Your current body weight.")
    height_cm = st.number_input("Height (cm):", min_value=100.0, max_value=250.0, value=170.0)
    st.caption("Your current height.")
    st.markdown("---")

    st.subheader("💧 Hydration")
    water_ml = st.number_input("Water intake (ml):", min_value=0.0, max_value=100000.0, value=2000.0)
    st.caption("Total daily water intake.")
    situation = st.selectbox(
        "Please choose your situation today:",
        ["A", "B", "C", "D"],
        format_func=lambda x: {
            "A": "A - Normal",
            "B": "B - Exercised or sweating",
            "C": "C - Hot weather",
            "D": "D - Exercised or sweating in hot weather"
        }[x]
    )
    st.caption("Your hydration status today")
    st.markdown("---")

    st.subheader("😴 Sleep")
    sleep_hours = st.number_input("Sleeping (hours):", min_value=0.0, max_value=24.0, value=7.0)
    st.caption("Average sleep duration per night.")
    night_wake_times = st.number_input("Night wake-ups (times):", min_value=0, max_value=20, value=1)
    st.caption("Number of times you wake up during sleep.")
    st.markdown("---")

    st.subheader("🏃 Activity")
    exercise_minutes = st.number_input("Exercise (min/day):", min_value=0.0, max_value=600.0, value=30.0)
    st.caption("Daily exercise or physical activity time.")
    sedentary_hours = st.number_input("Sedentary time (hours/day):", min_value=0.0, max_value=24.0, value=6.0)
    st.caption("Time spent sitting or inactive.")

st.markdown("---")

with col2:
    st.markdown("""
    <div style="
        background:white;
        padding:20px;
        border-radius:16px;
        border:1px solid #e9ecef;
        margin-bottom:20px;
    ">

    <div style="
        font-size:20px;
        font-weight:700;
        margin-bottom:12px;
    ">
    🌿 Lifestyle & Mental Health
    </div>

    <div style="
        font-size:14px;
        color:#6c757d;
        margin-bottom:12px;
    ">
    Enter your basic body information
    </div>

    <hr style="margin:10px 0; border:none; border-top:1px solid #eee;">
    
    """, unsafe_allow_html=True)
    
    st.subheader("🥗 Diet")
    st.caption("Tell about your eating habits to assess your diet quality.")
    
    fruit_veg_servings = st.number_input(
        "Fruit & vegetable (servings per day):",
        min_value=0.0, max_value=20.0, value=3.0
    )
    st.caption("1 serving ≈ 1 medium fruit or 1/2 cup vegetables.")

    fast_food_times = st.number_input(
        "Fast food (times per week):",
        min_value=0, max_value=21, value=1
    )
    st.caption("Includes: McDonald's, KFC, fried food, pizza, takeaway meals.")

    sugary_drinks = st.number_input(
        "Sugary drinks (per day):",
        min_value=0, max_value=10, value=1
    )
    st.caption("Includes: soft drinks, bubble tea, energy drinks, sweetened juice,etc.")
    
    st.markdown("---")

    st.subheader("🧠 Mental Health")
    st.caption("In the past week, have you experienced any of the following issues in these parts? Choose the quantity you have(0-3):")
    
    risk_score_emotion = st.selectbox(
        "Easily get irritated, Easily experience anxiety, and Have significant mood swings.",
        [0, 1, 2, 3],
        format_func=lambda x: {
            0: "0 - None",
            1: "1 - One issue",
            2: "2 - Two issues",
            3: "3 - Three issues"
        }[x]
    )
    
    risk_score_focus = st.selectbox(
        "Distraction, Not wanting to do things, and Decrease in efficiency.",
        [0, 1, 2, 3],
        format_func=lambda x: {
            0: "0 - None",
            1: "1 - One issue",
            2: "2 - Two issues",
            3: "3 - Three issues"
        }[x]
    )
    
    risk_score_body = st.selectbox(
        "Easily fatigued, Headache, and Sense of tension.",
        [0, 1, 2, 3],
        format_func=lambda x: {
            0: "0 - None",
            1: "1 - One issue",
            2: "2 - Two issues",
            3: "3 - Three issues"
        }[x]
    )
    st.markdown("---")

    st.subheader("📱 Screen Time")
    screen_time_hours = st.number_input("Screen time (hours/day):", min_value=0.0, max_value=24.0, value=4.0)
    st.caption("Total screen time per day (phone, computer, TV).")
    st.markdown("---")

    st.subheader("🚭 Habit")
    st.caption("Daily lifestyle habits.")
    
    smoking = st.selectbox(
        "Smoking:",
        [0, 1, 2],
        format_func=lambda x: {
            0: "0 - Never",
            1: "1 - Occasionally",
            2: "2 - Frequently"
        }[x]
    )
    
    alcohol = st.selectbox(
        "Alcohol:",
        [0, 1, 2],
        format_func=lambda x: {
            0: "0 - Never",
            1: "1 - Occasionally",
            2: "2 - Frequently"
        }[x]
    )
    late_night = st.selectbox(
        "Late-night:",
        [0, 1, 2],
        format_func=lambda x: {
            0: "0 - Never",
            1: "1 - Occasionally",
            2: "2 - Frequently"
        }[x]
    )

if st.button("🚀 Start Assessment"):
    result = run_web_assessment(
        weight_kg,
        height_cm,
        water_ml,
        situation,
        sleep_hours,
        night_wake_times,
        exercise_minutes,
        sedentary_hours,
        fruit_veg_servings,
        fast_food_times,
        sugary_drinks,
        risk_score_emotion,
        risk_score_focus,
        risk_score_body,
        screen_time_hours,
        smoking,
        alcohol,
        late_night
    )

    if USE_DB:
        save_to_db(user_name, result)

    c1, c2, c3 = st.columns(3)

    c1.markdown(f"""
    <div style="
       padding:18px; 
       border-radius:14px; 
       background:#ffffff; 
       border:1px solid #e9ecef;
       box-shadow:0 1px 4px rgba(0,0,0,0.04);">
       <div style="font-size:13px; color:#6c757d;">Health Score</div>
       <div style="font-size:34px; font-weight:700; color:#212529;">{result["health_score"]:.1f}</div>
       </div>
    """, unsafe_allow_html=True)

    if result["risk_level"] == "High risk":
       color = "#dc3545"
       text = "🔴 High Risk"
    elif result["risk_level"] == "Medium risk":
       color = "#f0ad4e"
       text = "🟡 Medium Risk"
    else:
       color = "#28a745"
       text = "🟢 Low Risk"

    c2.markdown(f"""
    <div style="
       padding:18px; 
       border-radius:14px; 
       background:#ffffff; 
       border:1px solid #e9ecef;
       box-shadow:0 1px 4px rgba(0,0,0,0.04);">
       <div style="font-size:13px; color:#6c757d;">Risk Level</div>
       <div style="font-size:24px; font-weight:700; color:{color};">{text}</div>
    </div>
    """, unsafe_allow_html=True)

    c3.markdown(f"""
    <div style="
       padding:18px; 
       border-radius:14px; 
       background:#ffffff; border:1px solid #e9ecef;
       box-shadow:0 1px 4px rgba(0,0,0,0.04);">
       <div style="font-size:13px; color:#6c757d;">Risk Percent</div>
       <div style="font-size:34px; font-weight:700; color:#212529;">{result["risk_percent"]:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    if result["risk_level"] == "High risk":
       st.error("High health risk detected. Please review your lifestyle habits and take action soon.")
    elif result["risk_level"] == "Medium risk":
       st.warning("Medium health risk detected. Some areas of your lifestyle may need improvement.")
    else:
       st.success("You are currently at low health risk. Keep maintaining your healthy habits.")

    st.markdown("---")

    st.subheader("📝 Summary")
    st.info(result["summary"])
    st.markdown("---")

    st.subheader("📊 Key Indicators")
    st.caption("Overview of each health dimension.")
    def show_card(name, level):
        if "High" in level:
            status = "Dangerous"
            color = "#dc3545"
            icon = "🔴"
        elif "Medium" in level:
            status = "Warning"
            color = "#ffc107"
            icon = "🟡"
        else:
            status = "Healthy"
            color = "#28a745"
            icon = "🟢"

        st.markdown(
            f"""
            <div style="
                 padding:14px;
                 border-radius:14px;
                 margin-bottom:12px;
                 background-color:#f9f9f9;
                 border-left:6px solid {color};
                 font-size:15px;
                 font-weight:500;
            ">
                 <b>{icon} {name}</b> — <span style="color:{color}; font-weight:700;">{status}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    for k in result["levels"]:
        show_card(k, result["levels"][k])
    st.markdown("---")

    if result["red_flags"]:
        st.subheader("🚨 High-Priority Concerns")
        for item in result["red_flags"][:3]:
            st.error(f"⚠️ {item}")
        st.markdown("---")

    if result["main_concerns"]:
        st.subheader("⚠️ Main Concerns")
        for item in result["main_concerns"][:3]:
            st.warning(item)
        st.markdown("---")

    if result["lifestyle"]:
        st.subheader("💡 Healthy Tips")
        for item in result["lifestyle"][:3]:
            st.info(item)
        st.markdown("---")

    st.subheader("📜 History")
    st.caption("Recent assessment records and trend changes over time.")
    if USE_DB:
        history = get_history(user_name)

        if history:
           df = pd.DataFrame(history)

           if "created_at" in df.columns:
               df["created_at"] = pd.to_datetime(df["created_at"])
               df = df.sort_values("created_at", ascending=False)

               show_df = df.copy()
               show_df["created_at"] = show_df["created_at"].dt.strftime("%Y-%m-%d %H:%M")
           else:
               show_df = df.copy()

           show_cols = [
               "created_at",
               "health_score",
               "risk_level",
               "risk_percent"
            ]

           show_df = show_df[[col for col in show_cols if col in show_df.columns]]

    st.markdown("### 📋 Recent Records")
    st.dataframe(show_df, use_container_width=True, height=200)

    st.caption(f"Total records: {len(df)}")

    st.markdown("---")

    st.markdown("### 📈 Trends")
    st.caption("This chart shows how your health score and risk percentage have changed across recent records.")
    chart_df = df.sort_values("created_at").set_index("created_at")

    col1, col2 = st.columns(2)

    if "health_score" in chart_df.columns:
        with col1:
            st.markdown("**Health Score**")
            st.line_chart(chart_df["health_score"], use_container_width=True)

    if "risk_percent" in chart_df.columns:
        with col2:
            st.markdown("**Risk Index (%)**")
            st.line_chart(chart_df["risk_percent"], use_container_width=True)
    else:
        st.info("No history records yet.")
