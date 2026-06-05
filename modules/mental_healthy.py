def calc_mental_healthy(
    risk_score_emotion,
    risk_score_focus,
    risk_score_body,
    language
):
    from modules.health_analyzer import LEVEL_TEXTS, dedup

    mental_score = 0

    reasons_mental = []

    suggestions_mental = []

    MENTAL_TEXTS = {

        "English": {
            "emotion_c":
                "You often feel emotionally low, anxious, or overwhelmed.",
            "emotion_b":
                "Your mood is sometimes low or irritable.",

            "focus_c":
                "You often have difficulty concentrating.",
            "focus_b":
                "You sometimes feel mentally tired or distracted.",

            "body_c":
                "You often experience stress-related physical symptoms.",
            "body_b":
                "You sometimes experience physical signs of stress.",

            "mental_stable":
                "Your recent mental well-being appears stable.",

            "emotion_suggest":
                "Make time for activities that help you relax and improve your mood.",

            "focus_suggest":
                "Reduce distractions, take regular breaks, and avoid mental overload.",

            "body_suggest":
                "Pay attention to stress-related physical symptoms and rest when needed.",

            "seek_help":
                "Consider talking to a trusted person or seeking professional support if stress continues.",

            "mental_keep":
                "Keep maintaining your current emotional balance and recovery habits."
        },

        "中文": {
            "emotion_c":
                "你经常感到情绪低落、焦虑或压力过大。",
            "emotion_b":
                "你的情绪有时较低落或易烦躁。",

            "focus_c":
                "你经常难以集中注意力。",
            "focus_b":
                "你有时感到精神疲惫或注意力不集中。",

            "body_c":
                "你经常出现与压力相关的身体不适症状。",
            "body_b":
                "你有时会出现压力带来的身体反应。",

            "mental_stable":
                "你近期的心理状态总体较为稳定。",

            "emotion_suggest":
                "建议安排时间进行放松活动，改善情绪状态。",

            "focus_suggest":
                "减少干扰，定期休息，避免过度用脑。",

            "body_suggest":
                "关注身体的压力信号，必要时注意休息。",

            "seek_help":
                "如果压力持续存在，建议与信任的人沟通或寻求专业帮助。",

            "mental_keep":
                "请继续保持当前较稳定的情绪与恢复状态。"
        }
    }

    mental_t = MENTAL_TEXTS[language]
    level_t = LEVEL_TEXTS[language]

    if risk_score_emotion == "C":
        mental_score += 2
        reasons_mental.append(
            mental_t["emotion_c"]
        )

    elif risk_score_emotion == "B":
        mental_score += 1
        reasons_mental.append(
            mental_t["emotion_b"]
        )

    if risk_score_focus == "C":
        mental_score += 2
        reasons_mental.append(
            mental_t["focus_c"]
        )

    elif risk_score_focus == "B":
        mental_score += 1
        reasons_mental.append(
            mental_t["focus_b"]
        )

    if risk_score_body == "C":
        mental_score += 2
        reasons_mental.append(
            mental_t["body_c"]
        )

    elif risk_score_body == "B":
        mental_score += 1
        reasons_mental.append(
            mental_t["body_b"]
        )

    if mental_score <= 1:
        risk_score_mental = 0
        level_mental = level_t["healthy"]
        category_mental = "Stable"

        if not reasons_mental:
            reasons_mental.append(
                mental_t["mental_stable"]
            )

    elif mental_score <= 3:
        risk_score_mental = 1
        level_mental = level_t["low"]
        category_mental = "Mild Stress"

    elif mental_score <= 5:
        risk_score_mental = 2
        level_mental = level_t["medium"]
        category_mental = "Emotional Strain"

    else:
        risk_score_mental = 3
        level_mental = level_t["high"]
        category_mental = "High Mental Stress"

    if risk_score_emotion in ["B", "C"]:
        suggestions_mental.append(
            mental_t["emotion_suggest"]
        )

    if risk_score_focus in ["B", "C"]:
        suggestions_mental.append(
            mental_t["focus_suggest"]
        )

    if risk_score_body in ["B", "C"]:
        suggestions_mental.append(
            mental_t["body_suggest"]
        )

    if mental_score >= 4:
        suggestions_mental.append(
            mental_t["seek_help"]
        )

    if not suggestions_mental:
        suggestions_mental.append(
            mental_t["mental_keep"]
        )

    return {
        "name": "Mental",
        "category": category_mental,
        "metric_value": mental_score,
        "raw_mental_score": mental_score,
        "score": risk_score_mental,
        "max_score": 3,
        "level": level_mental,
        "reasons": dedup(reasons_mental),
        "suggestions": dedup(suggestions_mental)
    }