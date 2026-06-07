from app.services.health_analyzer import LEVEL_TEXTS, dedup
def calc_screen_time(screen_time_hours, language):

    reasons_screen = []
    suggestions_screen = []

    SCREEN_TEXTS = {
        "English": {
            "screen_good": "Daily screen time is within a healthy range.",
            "screen_excessive": "Daily screen time is excessively high.",
            "screen_above_recommended": "Daily screen time is above the recommended level.",
            "screen_slightly_high": "Daily screen time is slightly high.",
            "screen_keep": "Keep maintaining balanced digital habits.",
            "screen_reduce": "Reduce recreational screen time and take frequent breaks.",
            "screen_limit": "Try to limit screen use and include more offline activities.",
            "screen_monitor": "Monitor screen habits and avoid unnecessary prolonged use."
        },
        "中文": {
            "screen_good": "每日屏幕使用时间处于较健康范围。",
            "screen_excessive": "每日屏幕使用时间过长。",
            "screen_above_recommended": "每日屏幕时间超过推荐水平。",
            "screen_slightly_high": "每日屏幕时间略高。",
            "screen_keep": "请继续保持较平衡的数字生活习惯。",
            "screen_reduce": "减少娱乐性屏幕使用时间，并适当休息。",
            "screen_limit": "尽量减少屏幕使用，多参与线下活动。",
            "screen_monitor": "注意屏幕使用习惯，避免长时间不必要的使用。"
        }
    }

    screen_t = SCREEN_TEXTS[language]
    level_t = LEVEL_TEXTS[language]

    if screen_time_hours > 8:
        screen_score = 3
        risk_score_screen = 3
        level_screen = level_t["high"]
        category_screen = "Digital Overload"
        reasons_screen.append(screen_t["screen_excessive"])
        suggestions_screen.append(screen_t["screen_reduce"])

    elif screen_time_hours > 6:
        screen_score = 2
        risk_score_screen = 2
        level_screen = level_t["medium"]
        category_screen = "High Screen Use"
        reasons_screen.append(screen_t["screen_above_recommended"])
        suggestions_screen.append(screen_t["screen_limit"])

    elif screen_time_hours > 4:
        screen_score = 1
        risk_score_screen = 1
        level_screen = level_t["low"]
        category_screen = "Slightly High"
        reasons_screen.append(screen_t["screen_slightly_high"])
        suggestions_screen.append(screen_t["screen_monitor"])

    else:
        screen_score = 0
        risk_score_screen = 0
        level_screen = level_t["healthy"]
        category_screen = "Balanced"
        reasons_screen.append(screen_t["screen_good"])
        suggestions_screen.append(screen_t["screen_keep"])

    return {
        "name": "Screen",
        "category": category_screen,
        "metric_value": screen_time_hours,
        "raw_screen_score": screen_score,
        "score": risk_score_screen,
        "level": level_screen,
        "max_score": 3,
        "reasons": dedup(reasons_screen),
        "suggestions": dedup(suggestions_screen)
    }