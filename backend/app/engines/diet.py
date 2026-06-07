from app.services.health_analyzer import LEVEL_TEXTS, dedup
def calc_diet(fruit_veg_servings, fast_food_times, sugary_drinks, language):

    diet_score = 0
    reasons_diet = []
    suggestions_diet = []

    DIET_TEXTS = {
        "English": {
            "diet_good": "Your diet quality is within a healthy range.",
            "diet_keep": "Keep maintaining balanced eating habits.",

            "fruit_veg_slightly_low": "Fruit and vegetable intake is slightly below the recommended level.",
            "fruit_veg_low": "Fruit and vegetable intake is significantly below the recommended level.",
            "fruit_veg_increase": "Try to include more fruits and vegetables in your daily meals.",
            "fruit_veg_target": "Increase daily fruit and vegetable intake to at least 5 servings.",

            "fast_food_high": "Fast food consumption is relatively high.",
            "fast_food_reduce": "Reduce fast food meals and choose healthier home-cooked options.",

            "sugary_drink_high": "Sugary drink intake is above the recommended level.",
            "sugary_drink_reduce": "Limit sugary drinks and replace them with water or low-sugar alternatives."
        },
        "中文": {
            "diet_good": "你的饮食质量处于较健康范围。",
            "diet_keep": "请继续保持均衡的饮食习惯。",

            "fruit_veg_slightly_low": "水果和蔬菜摄入量略低于推荐水平。",
            "fruit_veg_low": "水果和蔬菜摄入量明显低于推荐水平。",
            "fruit_veg_increase": "建议在日常饮食中增加水果和蔬菜的摄入。",
            "fruit_veg_target": "建议将每日水果和蔬菜摄入量提高至至少5份。",

            "fast_food_high": "快餐摄入频率较高。",
            "fast_food_reduce": "建议减少快餐摄入，尽量选择更健康的家庭自制餐食。",

            "sugary_drink_high": "含糖饮料摄入超过推荐水平。",
            "sugary_drink_reduce": "建议减少含糖饮料，改为饮用水或低糖替代品。"
        }
    }

    diet_t = DIET_TEXTS[language]
    level_t = LEVEL_TEXTS[language]

    if fruit_veg_servings >= 5:
        diet_score += 0

    elif 3 <= fruit_veg_servings < 5:
        diet_score += 1
        reasons_diet.append(diet_t["fruit_veg_slightly_low"])
        suggestions_diet.append(diet_t["fruit_veg_increase"])

    else:
        diet_score += 2
        reasons_diet.append(diet_t["fruit_veg_low"])
        suggestions_diet.append(diet_t["fruit_veg_target"])

    if fast_food_times >= 2:
        diet_score += 1
        reasons_diet.append(diet_t["fast_food_high"])
        suggestions_diet.append(diet_t["fast_food_reduce"])

    if sugary_drinks > 1:
        diet_score += 1
        reasons_diet.append(diet_t["sugary_drink_high"])
        suggestions_diet.append(diet_t["sugary_drink_reduce"])

    if diet_score >= 4:
        risk_score_diet = 3
        level_diet = level_t["high"]
        category_diet = "Poor Diet"

    elif diet_score >= 2:
        risk_score_diet = 2
        level_diet = level_t["medium"]
        category_diet = "Needs Improvement"

    elif diet_score >= 1:
        risk_score_diet = 1
        level_diet = level_t["low"]
        category_diet = "Slightly Unbalanced"

    else:
        risk_score_diet = 0
        level_diet = level_t["healthy"]
        category_diet = "Balanced Diet"
        reasons_diet.append(diet_t["diet_good"])
        suggestions_diet.append(diet_t["diet_keep"])

    return {
        "name": "Diet",
        "category": category_diet,
        "metric_value": diet_score,
        "fruit_veg_servings": fruit_veg_servings,
        "fast_food_times": fast_food_times,
        "sugary_drinks": sugary_drinks,
        "raw_diet_score": diet_score,
        "score": risk_score_diet,
        "level": level_diet,
        "max_score": 3,
        "reasons": dedup(reasons_diet),
        "suggestions": dedup(suggestions_diet),
    }