"""BMI calculation engine."""
from app.services.health_analyzer import LEVEL_TEXTS, dedup


def calc_bmi(weight_kg, height_cm, language):

    bmi = round(weight_kg / (height_cm / 100) ** 2, 1)

    reasons_bmi = []
    suggestions_bmi = []

    BMI_TEXTS = {

        "English": {

            "bmi_high": "Your BMI is above the healthy range.",

            "bmi_low": "Your BMI is below the healthy range.",

            "bmi_slightly_high": "Your BMI is slightly above the recommended range.",

            "bmi_normal": "Your BMI is within the healthy range.",

            "bmi_high_suggest":
                "Consider improving your diet and increasing physical activity.",

            "bmi_low_suggest":
                "Try to maintain a balanced diet and support healthy weight gain.",

            "bmi_slightly_high_suggest":
                "Regular exercise and balanced nutrition may help improve your BMI.",

            "bmi_normal_suggest":
                "Keep maintaining your healthy lifestyle."
        },

        "中文": {

            "bmi_high": "你的BMI高于健康范围。",

            "bmi_low": "你的BMI低于健康范围。",

            "bmi_slightly_high": "你的BMI略高于推荐范围。",

            "bmi_normal": "你的BMI处于健康范围内。",

            "bmi_high_suggest":
                "建议改善饮食结构并增加运动量。",

            "bmi_low_suggest":
                "建议保持均衡饮食并帮助健康增重。",

            "bmi_slightly_high_suggest":
                "规律运动和均衡饮食有助于改善BMI。",

            "bmi_normal_suggest":
                "请继续保持当前健康生活方式。"
        }
    }

    bmi_t = BMI_TEXTS[language]
    level_t = LEVEL_TEXTS[language]


    if bmi >= 30:

        risk_score_bmi = 3
        level_bmi = level_t["high"]
        category_bmi = "Obese"

        reasons_bmi.append(bmi_t["bmi_high"])
        suggestions_bmi.append(bmi_t["bmi_high_suggest"])

    elif bmi < 18.5:

        risk_score_bmi = 2
        level_bmi = level_t["medium"]
        category_bmi = "Underweight"

        reasons_bmi.append(bmi_t["bmi_low"])
        suggestions_bmi.append(bmi_t["bmi_low_suggest"])

    elif 25 <= bmi < 30:

        risk_score_bmi = 1
        level_bmi = level_t["low"]
        category_bmi = "Overweight"

        reasons_bmi.append(bmi_t["bmi_slightly_high"])
        suggestions_bmi.append(bmi_t["bmi_slightly_high_suggest"])

    else:

        risk_score_bmi = 0
        level_bmi = level_t["healthy"]
        category_bmi = "Healthy"

        reasons_bmi.append(bmi_t["bmi_normal"])
        suggestions_bmi.append(bmi_t["bmi_normal_suggest"])

    return {
        "name": "BMI",
        "category": category_bmi,
        "metric_value": bmi,
        "score": risk_score_bmi,
        "level": level_bmi,
        "max_score": 3,
        "reasons": dedup(reasons_bmi),
        "suggestions": dedup(suggestions_bmi)
    }
