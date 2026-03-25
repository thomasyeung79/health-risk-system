def calc_mental_healthy(risk_score_emotion, risk_score_focus, risk_score_body):
    reasons_mental_healthy = []
    suggestions_mental_healthy = []

    if risk_score_emotion >= 2:
        reasons_mental_healthy.append("Emotional distress (anxiety, irritability, or mood swings)")

    if risk_score_focus >= 2:
        reasons_mental_healthy.append("Reduced concentration or productivity")

    if risk_score_body >= 2:
        reasons_mental_healthy.append("Physical stress symptoms (fatigue, tension, or discomfort)")

    mental_score = risk_score_emotion + risk_score_focus + risk_score_body

    if mental_score >= 7:
        risk_score_mental_healthy = 3
        level_mental_healthy = "High Risk"
        suggestions_mental_healthy.append("Take rest and reduce stress; consider talking to someone you trust")
    elif mental_score >= 4:
        risk_score_mental_healthy = 2
        level_mental_healthy = "Medium Risk"
        suggestions_mental_healthy.append("Try relaxation techniques and manage stress levels.")
    elif mental_score >= 2:
        risk_score_mental_healthy = 1
        level_mental_healthy = "Low Risk"
        suggestions_mental_healthy.append("Maintain a healthy routine and take regular breaks")
    else:
        risk_score_mental_healthy = 0
        level_mental_healthy = "Healthy"

    max_risk_score_mental_healthy = 3

    return {
       "name": "Mental",
       "metric_value": mental_score,
       "score": risk_score_mental_healthy,
       "level": level_mental_healthy,
       "max_score": max_risk_score_mental_healthy,
       "reasons": reasons_mental_healthy,
       "suggestions": suggestions_mental_healthy,
   }