def calc_water_ratio(water_ml, situation, weight_kg):
    a = 0
    if situation == "A":  # 正常
        a = 0
    elif situation == "B":  # 运动或出汗
        a = 500
    elif situation == "C":  # 天热
        a = 300
    elif situation == "D":  # 天热时运动或出汗
        a = 800

    total = 30 * weight_kg + a  # 计算需要的喝水量  # European Food Safety Authority (2010)
    water_ratio = round(water_ml / total * 100, 1)  # 计算比例

    reasons_water_ratio = []
    suggestions_water_ratio = []

    if water_ratio >= 90:
        risk_score_water_ratio = 0
        level_water_ratio = "Healthy"
    elif 75 <= water_ratio < 90:  # 饮水比例较低
        risk_score_water_ratio = 1
        level_water_ratio = "Low Risk"
        reasons_water_ratio.append("Water intake below ideal.")
        suggestions_water_ratio.append("Water intake is slightly below the recommended level. Increase fluid intake throughout the day.")
    elif 60 <= water_ratio < 75:  # 饮水比例过低
        risk_score_water_ratio = 2
        level_water_ratio = "Medium Risk"
        reasons_water_ratio.append("The proportion of drinking water intake is lower than the safety standard.")
        suggestions_water_ratio.append("Hydration level is significantly below the recommended range. Prompt fluid intake is advised.")
    else:
        risk_score_water_ratio = 3
        level_water_ratio = "High Risk"
        reasons_water_ratio.append("Water intake is significantly insufficient.")
        suggestions_water_ratio.append("Increase daily water intake immediately and monitor hydration.")

    max_risk_score_water_ratio = 3
    return {
       "name": "Water",
       "metric_value": water_ratio,
       "score": risk_score_water_ratio,
       "level": level_water_ratio,
       "max_score": max_risk_score_water_ratio,
       "reasons": reasons_water_ratio,
       "suggestions": suggestions_water_ratio,
   }

# #Scientific opinion on dietary reference values for water. EFSA Journal, 8(3), 1459.