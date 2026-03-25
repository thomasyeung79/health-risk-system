def calc_screen_time(screen_time_hours):
    reasons_screen_time = []
    suggestions_screen_time = []

    if screen_time_hours >= 8:
        risk_score_screen_time = 3
        level_screen_time = "High Risk"
        reasons_screen_time.append("Excessive screen time.")
        suggestions_screen_time.append("Reduce screen time and take regular breaks.")
    elif screen_time_hours >= 6:
        risk_score_screen_time = 2
        level_screen_time = "Medium Risk"
        reasons_screen_time.append("High screen time.")
        suggestions_screen_time.append("Limit screen usage and rest your eyes regularly.")
    elif screen_time_hours >= 4:
        risk_score_screen_time = 1
        level_screen_time = "Low Risk"
        reasons_screen_time.append("Moderate screen time.")
        suggestions_screen_time.append("Limit screen exposure.")
    else:
        risk_score_screen_time = 0
        level_screen_time = "Healthy"

    max_risk_score_screen_time = 3

    return {
        "name": "Screen",
        "metric_value": screen_time_hours,
        "score": risk_score_screen_time,
        "level": level_screen_time,
        "max_score": max_risk_score_screen_time,
        "reasons": reasons_screen_time,
        "suggestions": suggestions_screen_time
    }