def calc_habit(smoking, alcohol, late_night, language):
    from modules.health_analyzer import LEVEL_TEXTS, dedup

    habit_score = 0
    reasons_habit = []
    suggestions_habit = []

    HABIT_TEXTS = {
        "English": {
            "habit_good": "Your lifestyle habits are currently within a healthy range.",
            "habit_keep": "Keep maintaining your current healthy habits.",

            "smoking_high": "Smoking habit may increase long-term health risks.",
            "smoking_mid": "Occasional smoking may still affect health.",

            "alcohol_high": "Frequent alcohol intake may negatively affect your health.",
            "alcohol_mid": "Alcohol intake is slightly above the ideal level.",

            "late_high": "Frequent late nights may reduce recovery and affect overall health.",
            "late_mid": "Sometimes staying up late may affect sleep quality and energy level.",

            "suggest_smoking": "Reduce smoking frequency and consider quitting gradually.",
            "suggest_alcohol": "Limit alcohol intake and avoid frequent drinking.",
            "suggest_sleep": "Try to maintain an earlier and more consistent bedtime."
        },

        "中文": {
            "habit_good": "你的生活习惯目前处于较健康范围。",
            "habit_keep": "请继续保持当前较健康的生活习惯。",

            "smoking_high": "长期吸烟可能增加健康风险。",
            "smoking_mid": "偶尔吸烟仍可能影响健康。",

            "alcohol_high": "频繁饮酒可能对健康产生负面影响。",
            "alcohol_mid": "饮酒量略高于理想水平。",

            "late_high": "经常熬夜会影响身体恢复和整体健康。",
            "late_mid": "偶尔熬夜可能影响睡眠质量和精力水平。",

            "suggest_smoking": "减少吸烟频率，并逐步考虑戒烟。",
            "suggest_alcohol": "控制饮酒量，避免频繁饮酒。",
            "suggest_sleep": "尽量保持更早且规律的作息时间。"
        }
    }

    habit_t = HABIT_TEXTS[language]
    level_t = LEVEL_TEXTS[language]

    if smoking == "C":
        habit_score += 2
        reasons_habit.append(habit_t["smoking_high"])
    elif smoking == "B":
        habit_score += 1
        reasons_habit.append(habit_t["smoking_mid"])

    if alcohol == "C":
        habit_score += 2
        reasons_habit.append(habit_t["alcohol_high"])
    elif alcohol == "B":
        habit_score += 1
        reasons_habit.append(habit_t["alcohol_mid"])

    if late_night == "C":
        habit_score += 2
        reasons_habit.append(habit_t["late_high"])
    elif late_night == "B":
        habit_score += 1
        reasons_habit.append(habit_t["late_mid"])

    if habit_score >= 5:
        risk_score_habit = 3
        level_habit = level_t["high"]
        category_habit = "High-Risk Habits"

    elif habit_score >= 3:
        risk_score_habit = 2
        level_habit = level_t["medium"]
        category_habit = "Unhealthy Habits"

    elif habit_score >= 1:
        risk_score_habit = 1
        level_habit = level_t["low"]
        category_habit = "Needs Attention"

    else:
        risk_score_habit = 0
        level_habit = level_t["healthy"]
        category_habit = "Healthy Habits"
        reasons_habit.append(habit_t["habit_good"])
        suggestions_habit.append(habit_t["habit_keep"])

    if smoking in ["B", "C"]:
        suggestions_habit.append(habit_t["suggest_smoking"])

    if alcohol in ["B", "C"]:
        suggestions_habit.append(habit_t["suggest_alcohol"])

    if late_night in ["B", "C"]:
        suggestions_habit.append(habit_t["suggest_sleep"])

    return {
        "name": "Habit",
        "category": category_habit,
        "metric_value": habit_score,
        "raw_habit_score": habit_score,
        "score": risk_score_habit,
        "max_score": 3,
        "level": level_habit,
        "reasons": dedup(reasons_habit),
        "suggestions": dedup(suggestions_habit),
    }