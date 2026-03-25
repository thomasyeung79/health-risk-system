def calc_habit(smoking, alcohol, late_night):
    habit_score = 0
    reasons_habit = []
    suggestions_habit = []
    #smoking
    if smoking >= 2:
        habit_score += 2
    elif smoking == 1:
        habit_score += 1
    #alcohol
    if alcohol >= 2:
        habit_score += 2
    elif alcohol == 1:
        habit_score += 1
    #late night
    if late_night >= 2:
        habit_score += 1
    elif late_night == 1:
        habit_score += 0.5

    if habit_score >= 4:
        risk_score_habit = 3
        level_habit = "High Risk"
        reasons_habit.append("Unhealthy habits may increase long-term health risks.")
        suggestions_habit.append("Reduce smoking and alcohol use and try to maintain a more regular daily routine.")
    elif habit_score >= 2:
        risk_score_habit = 2
        level_habit = "Medium Risk"
        reasons_habit.append("Some unhealthy habits observed.")
        suggestions_habit.append("Try to improve daily habits and reduce risks.")
    elif habit_score >= 1:
        risk_score_habit = 1
        level_habit = "Low Risk"
        reasons_habit.append("Some lifestyle habits could be improved.")
        suggestions_habit.append("Try to maintain healthier daily habits and avoid frequent late nights.")
    else:
        risk_score_habit = 0
        level_habit = "Healthy"
        suggestions_habit.append("Maintain your current healthy lifestyle habits.")

    max_risk_score_habit = 3

    return {
        "name": "Habit",
        "metric_value": habit_score,
        "score": risk_score_habit,
        "level": level_habit,
        "max_score": max_risk_score_habit,
        "reasons": reasons_habit,
        "suggestions": suggestions_habit
    }