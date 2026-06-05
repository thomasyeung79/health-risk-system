def calc_sleep(
    sleep_hours,
    night_wake_times,
    difficulty_falling_asleep,
    irregular_sleep_schedule,
    language
):
    from modules.health_analyzer import LEVEL_TEXTS, dedup

    sleep_score = 0
    reasons_sleep = []
    suggestions_sleep = []

    SLEEP_TEXTS = {
        "English": {
            "sleep_very_short": "Sleep duration is significantly insufficient.",
            "sleep_short": "Sleep duration is below the recommended level.",
            "sleep_normal": "Sleep duration is within a healthy range.",
            "sleep_too_long": "Sleep duration may be excessive.",

            "sleep_wake_frequent": "Frequent night awakenings were detected.",
            "sleep_wake_occasional": "Occasional night awakenings were detected.",

            "sleep_hard_fall_often": "Frequent difficulty falling asleep may indicate sleep or stress-related problems.",
            "sleep_hard_fall_sometimes": "Sometimes having difficulty falling asleep may affect sleep quality.",

            "sleep_irregular": "Sleep schedule is irregular.",
            "sleep_inconsistent": "Sleep schedule is somewhat inconsistent.",

            "sleep_suggest_duration": "Aim for at least 7 hours of sleep when possible.",
            "sleep_suggest_environment": "Improve your sleep environment and reduce disturbances.",
            "sleep_suggest_relax": "Reduce screen time before bed and relax before sleeping.",
            "sleep_suggest_schedule": "Try to maintain a consistent sleep schedule.",
            "sleep_keep": "Keep maintaining your current healthy sleep routine."
        },

        "中文": {
            "sleep_very_short": "睡眠时长严重不足。",
            "sleep_short": "睡眠时长低于建议水平。",
            "sleep_normal": "睡眠时长处于较健康范围。",
            "sleep_too_long": "睡眠时长可能偏长。",

            "sleep_wake_frequent": "夜间醒来次数较多。",
            "sleep_wake_occasional": "夜间偶尔醒来。",

            "sleep_hard_fall_often": "经常难以入睡，可能提示睡眠或压力相关问题。",
            "sleep_hard_fall_sometimes": "有时难以入睡，可能影响睡眠质量。",

            "sleep_irregular": "睡眠作息不规律。",
            "sleep_inconsistent": "睡眠作息有些不稳定。",

            "sleep_suggest_duration": "建议尽量保证至少7小时睡眠。",
            "sleep_suggest_environment": "改善睡眠环境，减少干扰。",
            "sleep_suggest_relax": "睡前减少屏幕使用，放松身心。",
            "sleep_suggest_schedule": "尽量保持规律作息。",
            "sleep_keep": "请继续保持当前健康的睡眠习惯。"
        }
    }

    sleep_t = SLEEP_TEXTS[language]
    level_t = LEVEL_TEXTS[language]

    if sleep_hours < 5:
        sleep_score += 3
        reasons_sleep.append(sleep_t["sleep_very_short"])

    elif 5 <= sleep_hours < 6:
        sleep_score += 2
        reasons_sleep.append(sleep_t["sleep_short"])

    elif 6 <= sleep_hours <= 8:
        sleep_score += 0
        reasons_sleep.append(sleep_t["sleep_normal"])

    else:
        sleep_score += 1
        reasons_sleep.append(sleep_t["sleep_too_long"])

    if night_wake_times >= 5:
        sleep_score += 2
        reasons_sleep.append(sleep_t["sleep_wake_frequent"])

    elif 2 <= night_wake_times < 5:
        sleep_score += 1
        reasons_sleep.append(sleep_t["sleep_wake_occasional"])

    if difficulty_falling_asleep == "C":
        sleep_score += 2
        reasons_sleep.append(sleep_t["sleep_hard_fall_often"])

    elif difficulty_falling_asleep == "B":
        sleep_score += 1
        reasons_sleep.append(sleep_t["sleep_hard_fall_sometimes"])

    if irregular_sleep_schedule == "C":
        sleep_score += 2
        reasons_sleep.append(sleep_t["sleep_irregular"])

    elif irregular_sleep_schedule == "B":
        sleep_score += 1
        reasons_sleep.append(sleep_t["sleep_inconsistent"])

    if sleep_score <= 1:
        risk_score_sleep = 0
        level_sleep = level_t["healthy"]
        category_sleep = "Healthy Sleep"

    elif sleep_score <= 3:
        risk_score_sleep = 1
        level_sleep = level_t["low"]
        category_sleep = "Mild Sleep Issue"

    elif sleep_score <= 5:
        risk_score_sleep = 2
        level_sleep = level_t["medium"]
        category_sleep = "Moderate Sleep Issue"

    else:
        risk_score_sleep = 3
        level_sleep = level_t["high"]
        category_sleep = "Serious Sleep Issue"

    if sleep_hours < 7:
        suggestions_sleep.append(sleep_t["sleep_suggest_duration"])

    if night_wake_times >= 2:
        suggestions_sleep.append(sleep_t["sleep_suggest_environment"])

    if difficulty_falling_asleep in ["B", "C"]:
        suggestions_sleep.append(sleep_t["sleep_suggest_relax"])

    if irregular_sleep_schedule in ["B", "C"]:
        suggestions_sleep.append(sleep_t["sleep_suggest_schedule"])

    if not suggestions_sleep:
        suggestions_sleep.append(sleep_t["sleep_keep"])

    return {
        "name": "Sleep",
        "category": category_sleep,
        "metric_value": sleep_hours,
        "raw_sleep_score": sleep_score,
        "score": risk_score_sleep,
        "max_score": 3,
        "level": level_sleep,
        "reasons": dedup(reasons_sleep),
        "suggestions": dedup(suggestions_sleep),
    }