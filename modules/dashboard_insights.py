"""Insight helpers for the dashboard overview."""

from __future__ import annotations


MODULE_RECOMMENDATIONS = {
    "English": {
        "sleep_score": "Set a consistent bedtime this week.",
        "activity_score": "Add at least 20 minutes of movement daily.",
        "diet_score": "Increase fruit and vegetable intake.",
        "screen_score": "Create screen-free time before bed.",
        "water_score": "Increase daily hydration gradually.",
        "mental_score": "Try a short daily relaxation exercise.",
        "habit_score": "Focus on one consistent habit this week.",
        "bmi_score": "Maintain a balanced diet and regular activity.",
    },
    "中文": {
        "sleep_score": "本周优先建立稳定的入睡时间。",
        "activity_score": "每天增加至少20分钟活动。",
        "diet_score": "增加蔬菜和水果摄入。",
        "screen_score": "睡前安排一段无屏幕时间。",
        "water_score": "逐步增加每日饮水量。",
        "mental_score": "尝试每天进行短时间放松练习。",
        "habit_score": "本周专注建立一个稳定习惯。",
        "bmi_score": "保持均衡饮食和规律活动。",
    },
}

METRIC_LABELS = {
    "English": {
        "health_score": "Health score",
        "stress": "Stress",
        "energy": "Energy",
        "sleep_score": "Sleep score",
        "activity_score": "Activity score",
    },
    "中文": {
        "health_score": "健康评分",
        "stress": "压力",
        "energy": "能量",
        "sleep_score": "睡眠评分",
        "activity_score": "活动评分",
    },
}

HEALTH_MODULES = (
    "bmi_score",
    "water_score",
    "sleep_score",
    "activity_score",
    "diet_score",
    "mental_score",
    "screen_score",
    "habit_score",
)


def _number(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_number(value):
    value = _number(value)
    if value is None:
        return "—"
    if value.is_integer():
        return str(int(value))
    return str(round(value, 1))


def _trend_direction(change, direction):
    change_value = _number(change)
    if change_value is not None:
        if change_value > 0:
            return "increased"
        if change_value < 0:
            return "decreased"

    if direction == "improving":
        return "increased"
    if direction == "declining":
        return "decreased"
    return "stable"


def _trend_text(metric, current, change, direction, language):
    label = METRIC_LABELS.get(language, METRIC_LABELS["English"]).get(metric, metric)
    direction_text = _trend_direction(change, direction)
    change_text = _format_number(abs(_number(change) or 0))
    current_text = _format_number(current)

    if language == "中文":
        verb = "上升" if direction_text == "increased" else "下降"
        if direction_text == "stable":
            return f"本周{label}基本稳定（当前：{current_text}）。"
        return f"本周{label}{verb} {change_text} 分（当前：{current_text}）。"

    verb = "increased" if direction_text == "increased" else "decreased"
    unit = "pt" if change_text == "1" else "pts"
    if direction_text == "stable":
        return f"{label} stayed stable this week (current: {current_text})."
    return f"{label} {verb} by {change_text} {unit} this week (current: {current_text})."


def _trend_insights(data, language):
    trends = data.get("trends") if isinstance(data, dict) else {}
    metrics = trends.get("metrics", []) if isinstance(trends, dict) else []
    valid_metrics = []

    for metric in metrics:
        if not isinstance(metric, dict):
            continue
        if metric.get("direction") == "insufficient_data":
            continue
        change = _number(metric.get("change"))
        current = _number(metric.get("current"))
        if change is None or current is None:
            continue
        valid_metrics.append(metric)

    valid_metrics.sort(key=lambda item: abs(_number(item.get("change")) or 0), reverse=True)

    insights = []
    for metric in valid_metrics[:2]:
        insights.append({
            "type": "trend",
            "icon": "📈",
            "text": _trend_text(
                metric.get("metric", ""),
                metric.get("current"),
                metric.get("change"),
                metric.get("direction"),
                language,
            ),
        })
    return insights


def _cross_domain_insights(data, language):
    health = data.get("health") if isinstance(data, dict) else None
    emotion = data.get("emotion") if isinstance(data, dict) else None
    if not isinstance(health, dict) or not isinstance(emotion, dict):
        return []

    insights = []
    sleep_score = _number(health.get("sleep_score"))
    activity_score = _number(health.get("activity_score"))
    stress = _number(emotion.get("stress"))
    energy = _number(emotion.get("energy"))

    if sleep_score is not None and stress is not None and sleep_score >= 2 and stress >= 7:
        insights.append({
            "type": "cross_domain",
            "icon": "🔁",
            "text": (
                "睡眠质量和压力可能正在相互影响。"
                if language == "中文"
                else "Sleep quality and stress may be reinforcing each other."
            ),
        })

    if activity_score is not None and energy is not None and activity_score >= 2 and energy <= 3:
        insights.append({
            "type": "cross_domain",
            "icon": "⚡",
            "text": (
                "运动不足可能正在影响你的能量水平。"
                if language == "中文"
                else "Low activity may be affecting your energy level."
            ),
        })

    return insights


def _priority_insights(data, language):
    health = data.get("health") if isinstance(data, dict) else None
    emotion = data.get("emotion") if isinstance(data, dict) else None
    insights = []

    if isinstance(health, dict):
        scored_modules = []
        for module in HEALTH_MODULES:
            value = _number(health.get(module))
            if value is not None:
                scored_modules.append((module, value))

        if scored_modules:
            worst_module, worst_score = max(scored_modules, key=lambda item: item[1])
            if worst_score > 0:
                insights.append({
                    "type": "priority",
                    "icon": "🎯",
                    "text": MODULE_RECOMMENDATIONS.get(language, MODULE_RECOMMENDATIONS["English"])[worst_module],
                })

    stress = _number(emotion.get("stress")) if isinstance(emotion, dict) else None
    if stress is not None and stress >= 7:
        insights.append({
            "type": "priority",
            "icon": "🧘",
            "text": (
                "今天尝试一次5分钟呼吸练习。"
                if language == "中文"
                else "Try a 5-minute breathing exercise today."
            ),
        })

    return insights


def build_trend_insights(data: dict, language: str) -> list[dict]:
    """Build dashboard insights from dashboard data.

    Returns a maximum of four insight dictionaries and never raises.
    """
    try:
        if not isinstance(data, dict) or not any(data.values()):
            return []

        lang = "中文" if language == "中文" else "English"
        insights = []
        insights.extend(_trend_insights(data, lang))
        insights.extend(_cross_domain_insights(data, lang))
        insights.extend(_priority_insights(data, lang))

        clean = []
        for insight in insights:
            if not isinstance(insight, dict):
                continue
            text = insight.get("text")
            if not text:
                continue
            clean.append({
                "type": str(insight.get("type", "insight")),
                "icon": str(insight.get("icon", "•")),
                "text": str(text),
            })

        return clean[:4]
    except Exception:
        return []
