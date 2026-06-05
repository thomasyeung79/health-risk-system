def calc_water_ratio(water_l, situation, weight_kg, thirst_level, urine_color, language):
    from modules.health_analyzer import LEVEL_TEXTS, dedup

    situation_extra = {
        "A": 0,
        "B": 0.5,
        "C": 0.3,
        "D": 0.8
    }

    a = situation_extra.get(situation, 0)
    safe_weight = max(weight_kg, 1.0) if weight_kg is not None else 70.0

    recommended_water_l = 0.03 * safe_weight + a
    water_ratio = round(water_l / recommended_water_l * 100, 1)

    reasons_water_ratio = []
    suggestions_water_ratio = []

    WATER_TEXTS = {
        "English": {
            "thirst_c": "Frequent thirst may indicate insufficient hydration.",
            "thirst_b": "Occasional thirst may suggest slightly reduced hydration levels.",
            "urine_c": "Darker urine color may indicate dehydration.",
            "urine_b": "Moderate urine color may suggest hydration is slightly below optimal.",
            "water_good": "Your hydration level is within the recommended range.",
            "water_slightly_low": "Water intake is slightly below optimal.",
            "water_low": "Hydration level is below the recommended range.",
            "water_very_low": "Water intake is significantly below recommended levels.",
            "water_keep": "Keep maintaining your current hydration habit.",
            "water_increase": "Consider increasing daily water intake.",
            "water_monitor": "Increase water intake and monitor hydration habits.",
            "water_immediate": "Increase daily water intake as soon as possible.",
            "after_exercise": "Consider additional hydration after physical activity.",
            "hot_weather": "Increase fluid intake during warm or hot conditions."
        },
        "中文": {
            "thirst_c": "经常感到口渴可能提示水分摄入不足。",
            "thirst_b": "偶尔感到口渴，可能提示水分摄入略低。",
            "urine_c": "较深的尿液颜色可能提示脱水。",
            "urine_b": "中等尿液颜色可能表示水分摄入略低于理想状态。",
            "water_good": "你的水分摄入处于推荐范围内。",
            "water_slightly_low": "饮水量略低于理想水平。",
            "water_low": "水分摄入低于推荐范围。",
            "water_very_low": "饮水量明显低于推荐水平。",
            "water_keep": "请继续保持当前良好的补水习惯。",
            "water_increase": "建议适当增加每日饮水量。",
            "water_monitor": "建议增加饮水量并关注补水习惯。",
            "water_immediate": "建议尽快增加每日饮水量。",
            "after_exercise": "运动后建议适当补充水分。",
            "hot_weather": "天气炎热时建议增加补水。"
        }
    }

    water_t = WATER_TEXTS[language]
    level_t = LEVEL_TEXTS[language]

    penalty = 0

    if thirst_level == "C":
        penalty += 5
        reasons_water_ratio.append(water_t["thirst_c"])
    elif thirst_level == "B":
        penalty += 2
        reasons_water_ratio.append(water_t["thirst_b"])

    if urine_color == "C":
        penalty += 5
        reasons_water_ratio.append(water_t["urine_c"])
    elif urine_color == "B":
        penalty += 2
        reasons_water_ratio.append(water_t["urine_b"])

    water_ratio_adjusted = max(0, water_ratio - penalty)

    if water_ratio_adjusted >= 90:
        risk_score_water_ratio = 0
        level_water_ratio = level_t["healthy"]
        category_water = "Optimal"
        reasons_water_ratio.append(water_t["water_good"])
        suggestions_water_ratio.append(water_t["water_keep"])

    elif 75 <= water_ratio_adjusted < 90:
        risk_score_water_ratio = 1
        level_water_ratio = level_t["low"]
        category_water = "Slightly Low"
        reasons_water_ratio.append(water_t["water_slightly_low"])
        suggestions_water_ratio.append(water_t["water_increase"])

    elif 60 <= water_ratio_adjusted < 75:
        risk_score_water_ratio = 2
        level_water_ratio = level_t["medium"]
        category_water = "Low"
        reasons_water_ratio.append(water_t["water_low"])
        suggestions_water_ratio.append(water_t["water_monitor"])

    else:
        risk_score_water_ratio = 3
        level_water_ratio = level_t["high"]
        category_water = "Very Low"
        reasons_water_ratio.append(water_t["water_very_low"])
        suggestions_water_ratio.append(water_t["water_immediate"])

    if situation in ["B", "D"]:
        suggestions_water_ratio.append(water_t["after_exercise"])

    if situation in ["C", "D"]:
        suggestions_water_ratio.append(water_t["hot_weather"])

    return {
        "name": "Water",
        "category": category_water,
        "metric_value": water_ratio,
        "adjusted_value": water_ratio_adjusted,
        "score": risk_score_water_ratio,
        "max_score": 3,
        "level": level_water_ratio,
        "reasons": dedup(reasons_water_ratio),
        "suggestions": dedup(suggestions_water_ratio),
        "recommended_water_l": round(recommended_water_l, 1)
    }