"""Wellness Coach Engine — rule-based coaching when AI is unavailable.

Produces structured coaching responses from health, emotion, and trend data.
Bilingual (English / 中文).
"""

from datetime import datetime
from typing import Any, Optional


def _score_label(score: Optional[float], higher_is_better: bool, language: str) -> str:
    """Return a qualitative label for a numeric score."""
    if score is None:
        return "—"
    if language == "中文":
        if higher_is_better:
            if score >= 80:
                return "优秀"
            elif score >= 60:
                return "良好"
            elif score >= 40:
                return "一般"
            else:
                return "需关注"
        else:
            if score <= 3:
                return "低"
            elif score <= 6:
                return "中等"
            else:
                return "高"
    else:
        if higher_is_better:
            if score >= 80:
                return "Excellent"
            elif score >= 60:
                return "Good"
            elif score >= 40:
                return "Fair"
            else:
                return "Needs attention"
        else:
            if score <= 3:
                return "Low"
            elif score <= 6:
                return "Moderate"
            else:
                return "High"


def build_coaching_response(
    context: dict[str, Any],
    question: str,
    language: str,
) -> dict[str, Any]:
    """Generate a structured coaching response from user context.

    Args:
        context: dict with keys 'health', 'emotion', 'trends', 'report'
        question: the user's question text
        language: 'English' or '中文'

    Returns:
        dict with keys: situation, strengths, concerns, actions, goal
    """
    health = context.get("health")
    emotion = context.get("emotion")
    trends = context.get("trends", {})
    _ = context.get("report")  # unused in local mode

    lang = language
    is_cn = lang == "中文"

    # ── Situation ──────────────────────────────────
    situation_parts = []
    if health:
        score = health.get("health_score")
        risk = health.get("risk_level", "—")
        if score is not None:
            label = _score_label(score, True, lang)
            if is_cn:
                situation_parts.append(f"你的健康评分为 {score:.0f}/100（{label}），风险等级为 {risk}。")
            else:
                situation_parts.append(f"Your health score is {score:.0f}/100 ({label}), risk level is {risk}.")

    if emotion:
        stress = emotion.get("stress")
        energy = emotion.get("energy")
        mood = emotion.get("mood_key", "—")
        if stress is not None:
            slabel = _score_label(stress, False, lang)
            elabel = _score_label(energy, True, lang) if energy is not None else ""
            if is_cn:
                stress_part = f"压力水平为 {stress}/10（{slabel}）"
                energy_part = f"能量水平为 {energy}/10（{elabel}）" if energy else ""
                mood_part = f"最近情绪为「{mood}」" if mood else ""
                situation_parts.append(f"{stress_part}，{energy_part}，{mood_part}。")
            else:
                stress_part = f"Your stress level is {stress}/10 ({slabel})"
                energy_part = f", energy is {energy}/10 ({elabel})" if energy else ""
                mood_part = f", and your mood is {mood}" if mood else ""
                situation_parts.append(f"{stress_part}{energy_part}{mood_part}.")

    situation = " ".join(situation_parts) if situation_parts else (
        "No health data available. Complete a health check first."
        if not is_cn else "暂无健康数据，请先完成健康检测。"
    )

    # ── Strengths ──────────────────────────────────
    strengths = []
    if health:
        module_labels_en = {
            "bmi_score": "BMI", "water_score": "Hydration", "sleep_score": "Sleep",
            "activity_score": "Activity", "diet_score": "Diet",
            "screen_score": "Screen time", "habit_score": "Lifestyle habits",
        }
        module_labels_cn = {
            "bmi_score": "BMI", "water_score": "饮水", "sleep_score": "睡眠",
            "activity_score": "运动", "diet_score": "饮食",
            "screen_score": "屏幕时间", "habit_score": "生活习惯",
        }
        labels = module_labels_cn if is_cn else module_labels_en
        for key, label in labels.items():
            val = health.get(key)
            if val is not None and val <= 1:
                if is_cn:
                    strengths.append(f"✅ {label}良好（评分 {val}/3）")
                else:
                    strengths.append(f"✅ {label} is good (score {val}/3)")

        if trends:
            metrics = trends.get("metrics", [])
            for m in metrics:
                if m.get("direction") == "improving" and m.get("metric") in ("health_score", "energy"):
                    metric_name = "健康评分" if is_cn else "Health score"
                    if is_cn:
                        strengths.append(f"📈 {metric_name}正在改善")
                    else:
                        strengths.append(f"📈 {metric_name} is improving")

    if not strengths:
        if is_cn:
            strengths.append("暂无明显优势领域。完成更多检测以获取分析。")
        else:
            strengths.append("No clear strengths yet. Complete more assessments to get insights.")

    # ── Concerns ───────────────────────────────────
    concerns = []
    if health:
        labels_c = module_labels_cn if is_cn else module_labels_en
        for key, label in labels_c.items():
            val = health.get(key)
            if val is not None and val >= 2:
                if is_cn:
                    concerns.append(f"⚠️ {label}需关注（评分 {val}/3）")
                else:
                    concerns.append(f"⚠️ {label} needs attention (score {val}/3)")

    if emotion:
        stress = emotion.get("stress")
        if stress is not None and stress >= 7:
            if is_cn:
                concerns.append("⚠️ 压力水平偏高，建议关注压力管理")
            else:
                concerns.append("⚠️ Stress level is high, consider stress management")

    if trends:
        metrics = trends.get("metrics", [])
        for m in metrics:
            if m.get("direction") == "declining":
                metric_map_cn = {"health_score": "健康评分", "stress": "压力", "energy": "能量", "sleep_score": "睡眠"}
                metric_map_en = {"health_score": "Health score", "stress": "Stress", "energy": "Energy", "sleep_score": "Sleep"}
                mapping = metric_map_cn if is_cn else metric_map_en
                mn = mapping.get(m["metric"], m["metric"])
                if is_cn:
                    concerns.append(f"📉 {mn}呈下降趋势")
                else:
                    concerns.append(f"📉 {mn} is declining")

    if not concerns:
        if is_cn:
            concerns.append("✅ 当前无明显风险信号，继续保持良好习惯。")
        else:
            concerns.append("✅ No significant risk signals. Keep maintaining your habits.")

    # ── Actions ────────────────────────────────────
    actions = []
    if health:
        # Find worst module
        worst_module = None
        worst_score = -1
        for key in ["sleep_score", "activity_score", "diet_score", "screen_score", "stress"]:
            if key == "stress" and emotion:
                val = emotion.get("stress")
            else:
                val = health.get(key)
            if val is not None and val > worst_score:
                worst_score = val
                worst_module = key

        if worst_module:
            if is_cn:
                action_map = {
                    "sleep_score": "尝试固定作息时间，睡前30分钟远离屏幕",
                    "activity_score": "每天安排20-30分钟轻度运动，如散步或拉伸",
                    "diet_score": "增加蔬果摄入，减少快餐和含糖饮料",
                    "screen_score": "设置无屏幕时段，尤其在睡前和起床后",
                    "stress": "每天预留10分钟放松时间，可尝试呼吸练习",
                }
                default_action = "选择最容易执行的一个小习惯，先从1%的改变开始"
            else:
                action_map = {
                    "sleep_score": "Set a consistent bedtime and reduce screen time 30 min before sleep",
                    "activity_score": "Add 20-30 minutes of light movement daily, such as walking",
                    "diet_score": "Increase fruit and vegetable intake, reduce fast food and sugary drinks",
                    "screen_score": "Create screen-free blocks, especially before bed and after waking",
                    "stress": "Set aside 10 minutes daily for relaxation or breathing exercises",
                }
                default_action = "Pick one small habit to improve and start with a 1% change"
            actions.append(action_map.get(worst_module, default_action))

    # Trend-based actions
    if trends:
        metrics = trends.get("metrics", [])
        for m in metrics:
            if m.get("direction") == "declining" and m.get("metric") == "sleep_score":
                if is_cn:
                    actions.append("睡眠评分下降中，建议今晚比平时早30分钟上床")
                else:
                    actions.append("Your sleep score is declining. Try going to bed 30 minutes earlier tonight.")
            elif m.get("direction") == "declining" and m.get("metric") == "stress":
                if is_cn:
                    actions.append("压力正在上升，考虑安排一次短暂的放松或散步")
                else:
                    actions.append("Stress is rising. Consider scheduling a short break or walk.")

    if not actions:
        if is_cn:
            actions.append("继续保持当前健康习惯，定期记录和回顾。")
        else:
            actions.append("Keep your current habits and continue monitoring regularly.")

    # ── Goal ───────────────────────────────────────
    if health:
        current_score = health.get("health_score")
        if current_score is not None:
            if current_score >= 90:
                target = round(current_score, 0)
                if is_cn:
                    goal = f"保持健康评分在 {target:.0f} 以上，持续14天。"
                else:
                    goal = f"Maintain your health score above {target:.0f} for the next 14 days."
            else:
                target = min(round(current_score + 5, 0), 100)
                if is_cn:
                    goal = f"在7天内将健康评分提升至 {target:.0f}。"
                else:
                    goal = f"Raise your health score to {target:.0f} within 7 days."
        else:
            if is_cn:
                goal = "完成一次健康检测，建立基线数据。"
            else:
                goal = "Complete a health check to establish your baseline."
    else:
        if is_cn:
            goal = "开始你的第一次健康检测，了解当前状态。"
        else:
            goal = "Start with a health check to understand your current status."

    return {
        "situation": situation,
        "strengths": strengths,
        "concerns": concerns,
        "actions": actions,
        "goal": goal,
    }
