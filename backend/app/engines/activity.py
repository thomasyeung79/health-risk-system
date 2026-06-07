from app.services.health_analyzer import LEVEL_TEXTS, dedup
def calc_activity(exercise_minutes, sedentary_hours, language):

    activity_score = 0
    reasons_activity = []
    suggestions_activity = []

    ACTIVITY_TEXTS = {
        "English": {
            "activity_good": "Your physical activity level is within a healthy range.",
            "activity_very_low": "Very low physical activity.",
            "activity_below_recommended": "Below recommended activity level.",
            "activity_excessive_sitting": "Excessive sitting time.",
            "activity_high_sedentary": "High sedentary time.",
            "activity_keep": "Keep maintaining your current activity routine.",
            "activity_exercise_more": "Try to exercise at least 30 minutes daily.",
            "activity_reduce_sitting": "Reduce sitting time and take short movement breaks."
        },
        "中文": {
            "activity_good": "你的身体活动水平处于较健康范围。",
            "activity_very_low": "身体活动水平非常低。",
            "activity_below_recommended": "运动量低于建议水平。",
            "activity_excessive_sitting": "久坐时间过长。",
            "activity_high_sedentary": "久坐时间较多。",
            "activity_keep": "请继续保持当前的运动习惯。",
            "activity_exercise_more": "建议每天至少运动30分钟。",
            "activity_reduce_sitting": "减少久坐时间，适当起身活动。"
        }
    }

    activity_t = ACTIVITY_TEXTS[language]
    level_t = LEVEL_TEXTS[language]

    # Exercise
    if exercise_minutes < 10:
        activity_score += 2
        reasons_activity.append(activity_t["activity_very_low"])

    elif exercise_minutes < 30:
        activity_score += 1
        reasons_activity.append(activity_t["activity_below_recommended"])

    # Sedentary
    if sedentary_hours >= 10:
        activity_score += 2
        reasons_activity.append(activity_t["activity_excessive_sitting"])

    elif sedentary_hours >= 8:
        activity_score += 1
        reasons_activity.append(activity_t["activity_high_sedentary"])

    # Risk level
    if activity_score <= 1:
        risk_score = 0
        level = level_t["healthy"]
        category = "Active"

    elif activity_score <= 2:
        risk_score = 1
        level = level_t["low"]
        category = "Slightly Inactive"

    elif activity_score <= 3:
        risk_score = 2
        level = level_t["medium"]
        category = "Inactive"

    else:
        risk_score = 3
        level = level_t["high"]
        category = "Very Inactive"

    # Suggestions
    if exercise_minutes < 30:
        suggestions_activity.append(activity_t["activity_exercise_more"])

    if sedentary_hours >= 8:
        suggestions_activity.append(activity_t["activity_reduce_sitting"])

    if not suggestions_activity:
        reasons_activity.append(activity_t["activity_good"])
        suggestions_activity.append(activity_t["activity_keep"])

    return {
        "name": "Activity",
        "category": category,
        "metric_value": exercise_minutes,
        "sedentary_hours": sedentary_hours,
        "raw_activity_score": activity_score,
        "score": risk_score,
        "max_score": 3,
        "level": level,
        "reasons": dedup(reasons_activity),
        "suggestions": dedup(suggestions_activity),
    }