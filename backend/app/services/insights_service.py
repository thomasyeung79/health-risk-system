"""Insights Dashboard service — generates meaningful wellness insights.

Produces:
  - Today's wellness score
  - Monthly trend summary
  - Positive changes
  - Risk alerts
  - Recommended focus
  - Recent achievements
"""

import statistics
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.ai_report import AIReport
from app.models.emotion_record import EmotionRecord
from app.models.healing_plan import HealingPlan
from app.models.health_record import HealthRecord
from app.models.member import Member


def generate_insights(
    db: Session,
    user_id: int,
    member_id: int,
) -> dict[str, Any]:
    """Generate meaningful wellness insights for a member."""
    member = db.get(Member, member_id)
    if member is None:
        raise ValueError(f"Member {member_id} not found")

    is_cn = (member.preferred_language or "English") == "中文"

    # Gather data
    health_records = (
        db.query(HealthRecord)
        .filter(HealthRecord.user_id == user_id)
        .order_by(HealthRecord.created_at.desc())
        .limit(50)
        .all()
    )
    emotion_records = (
        db.query(EmotionRecord)
        .filter(EmotionRecord.user_id == user_id)
        .order_by(EmotionRecord.created_at.desc())
        .limit(50)
        .all()
    )
    ai_reports = (
        db.query(AIReport)
        .filter(AIReport.member_id == member_id, AIReport.user_id == user_id)
        .order_by(AIReport.created_at.desc())
        .limit(10)
        .all()
    )
    healing_plans = (
        db.query(HealingPlan)
        .filter(HealingPlan.member_id == member_id, HealingPlan.user_id == user_id)
        .all()
    )

    # Calculate wellness score
    wellness_score = _calculate_wellness_score(health_records)

    # Monthly trend
    monthly_trend = _get_monthly_trend(health_records, is_cn)

    # Positive changes
    positive_changes = _get_positive_changes(health_records, emotion_records, is_cn)

    # Risk alerts
    risk_alerts = _get_risk_alerts(health_records, ai_reports, is_cn)

    # Recommended focus
    recommended_focus = _get_recommended_focus(health_records, is_cn)

    # Recent achievements
    recent_achievements = _get_recent_achievements(
        health_records, healing_plans, ai_reports, is_cn,
    )

    return {
        "member_id": member_id,
        "wellness_score": wellness_score,
        "monthly_trend": monthly_trend,
        "positive_changes": positive_changes,
        "risk_alerts": risk_alerts,
        "recommended_focus": recommended_focus,
        "recent_achievements": recent_achievements,
    }


def _calculate_wellness_score(health_records: list[HealthRecord]) -> float | None:
    """Calculate the most recent wellness score."""
    if not health_records:
        return None
    latest = health_records[0]
    score = getattr(latest, "health_score", None)
    if score is None:
        return None
    return round(score, 1)


def _get_monthly_trend(health_records: list[HealthRecord], is_cn: bool) -> str:
    """Generate a meaningful monthly trend summary."""
    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)

    recent = [
        r for r in health_records
        if getattr(r, "health_score", None) is not None
        and r.created_at >= month_ago
    ]
    older = [
        r for r in health_records
        if getattr(r, "health_score", None) is not None
        and r.created_at < month_ago
    ]

    if recent and older:
        avg_recent = statistics.mean([r.health_score for r in recent])
        avg_older = statistics.mean([r.health_score for r in older])
        diff = avg_recent - avg_older

        if diff > 5:
            if is_cn:
                return f"健康评分在过去一个月提升了 {diff:.0f} 分。"
            return f"Wellness score improved by {diff:.0f} points this month."
        elif diff < -5:
            if is_cn:
                return f"健康评分在过去一个月下降了 {abs(diff):.0f} 分。建议关注。"
            return f"Wellness score declined by {abs(diff):.0f} points this month."
        else:
            if is_cn:
                return "健康评分在过去一个月保持稳定。"
            return "Wellness score remained stable this month."

    if recent:
        if is_cn:
            return f"近一个月记录了 {len(recent)} 次健康检测。继续定期检测以追踪趋势。"
        return f"{len(recent)} health check(s) recorded this month. Keep tracking for trend data."

    if is_cn:
        return "近一个月暂无健康检测数据。"
    return "No health check data this month."


def _get_positive_changes(
    health_records: list[HealthRecord],
    emotion_records: list[EmotionRecord],
    is_cn: bool,
) -> list[str]:
    """Identify positive changes in health metrics."""
    changes: list[str] = []

    if len(health_records) >= 2:
        sleep_scores = [
            getattr(r, "sleep_score", None) for r in reversed(health_records[-10:])
            if getattr(r, "sleep_score", None) is not None
        ]
        if len(sleep_scores) >= 4:
            mid = len(sleep_scores) // 2
            avg_first = statistics.mean(sleep_scores[:mid])
            avg_second = statistics.mean(sleep_scores[mid:])
            if avg_second < avg_first - 0.3:
                if is_cn:
                    changes.append("睡眠质量有所改善。")
                else:
                    changes.append("Sleep quality has improved.")

        activity_scores = [
            getattr(r, "activity_score", None) for r in reversed(health_records[-10:])
            if getattr(r, "activity_score", None) is not None
        ]
        if len(activity_scores) >= 4:
            mid = len(activity_scores) // 2
            avg_first = statistics.mean(activity_scores[:mid])
            avg_second = statistics.mean(activity_scores[mid:])
            if avg_second < avg_first - 0.3:
                if is_cn:
                    changes.append("运动活跃度有提升。")
                else:
                    changes.append("Physical activity level has increased.")

    if len(emotion_records) >= 4:
        recent_emotions = emotion_records[:4]
        avg_energy = statistics.mean([
            e.energy for e in recent_emotions
            if getattr(e, "energy", None) is not None
        ])
        if avg_energy >= 7:
            if is_cn:
                changes.append("近期精力水平良好。")
            else:
                changes.append("Recent energy levels are good.")

        avg_stress = statistics.mean([
            e.stress for e in recent_emotions
            if getattr(e, "stress", None) is not None
        ])
        if avg_stress <= 3:
            if is_cn:
                changes.append("近期压力水平较低。")
            else:
                changes.append("Recent stress levels are low.")

    if not changes:
        if is_cn:
            changes.append("继续记录数据以发现积极变化。")
        else:
            changes.append("Keep tracking to identify positive changes.")

    return changes


def _get_risk_alerts(
    health_records: list[HealthRecord],
    ai_reports: list[AIReport],
    is_cn: bool,
) -> list[str]:
    """Generate risk alerts based on data."""
    alerts: list[str] = []

    # Check latest health record for high risk
    if health_records:
        latest = health_records[0]
        risk_level = getattr(latest, "risk_level", None)
        if risk_level and risk_level in ("High", "高"):
            if is_cn:
                alerts.append("最新健康检测显示高风险。")
            else:
                alerts.append("Latest health check indicates high risk.")

        sleep_score = getattr(latest, "sleep_score", None)
        if sleep_score is not None and sleep_score >= 2:
            if is_cn:
                alerts.append("睡眠质量评分偏低。")
            else:
                alerts.append("Sleep quality score is below optimal.")

        mental_score = getattr(latest, "mental_score", None)
        if mental_score is not None and mental_score >= 2:
            if is_cn:
                alerts.append("心理健康评分需关注。")
            else:
                alerts.append("Mental wellness score needs attention.")

    if ai_reports:
        latest_report = ai_reports[0]
        risk = getattr(latest_report, "risk_level", None)
        if risk and risk in ("High", "Medium", "高", "中"):
            if is_cn:
                alerts.append(f"最新 AI 报告风险等级：{risk}。")
            else:
                alerts.append(f"Latest AI report risk level: {risk}.")

    if not alerts:
        if is_cn:
            alerts.append("暂无风险警报。")
        else:
            alerts.append("No risk alerts at this time.")

    return alerts


def _get_recommended_focus(health_records: list[HealthRecord], is_cn: bool) -> str:
    """Identify the area needing most attention."""
    if not health_records:
        if is_cn:
            return "完成首次健康检测以确定关注方向。"
        return "Complete a health check to identify focus areas."

    latest = health_records[0]
    module_scores = {
        "sleep": getattr(latest, "sleep_score", None),
        "activity": getattr(latest, "activity_score", None),
        "diet": getattr(latest, "diet_score", None),
        "mental": getattr(latest, "mental_score", None),
        "water": getattr(latest, "water_score", None),
        "screen": getattr(latest, "screen_score", None),
        "habit": getattr(latest, "habit_score", None),
    }

    worst_area = max(module_scores, key=lambda k: module_scores[k] if module_scores[k] is not None else -1)
    worst_score = module_scores[worst_area]

    if worst_score is None or worst_score < 1:
        if is_cn:
            return "各指标良好，继续保持。"
        return "All metrics are good — keep maintaining."

    area_labels = {
        "sleep": ("睡眠质量", "sleep quality"),
        "activity": ("运动活动", "physical activity"),
        "diet": ("饮食习惯", "dietary habits"),
        "mental": ("心理健康", "mental wellness"),
        "water": ("水分摄入", "hydration"),
        "screen": ("屏幕时间", "screen time"),
        "habit": ("生活习惯", "daily habits"),
    }
    label = area_labels.get(worst_area, (worst_area, worst_area))

    if is_cn:
        return f"建议重点关注：{label[0]}（当前评分 {worst_score}/3）。"
    return f"Recommended focus: {label[1]} (current score {worst_score}/3)."


def _get_recent_achievements(
    health_records: list[HealthRecord],
    healing_plans: list[HealingPlan],
    ai_reports: list[AIReport],
    is_cn: bool,
) -> list[str]:
    """List recent wellness achievements."""
    achievements: list[str] = []

    # Completed healing plans
    completed = [p for p in healing_plans if getattr(p, "status", "") == "completed"]
    if completed:
        if is_cn:
            achievements.append(f"完成了 {len(completed)} 个康复计划。")
        else:
            achievements.append(f"Completed {len(completed)} healing plan(s).")

    # Health checks done
    if len(health_records) >= 5:
        if is_cn:
            achievements.append("已累计 5 次以上健康检测。")
        else:
            achievements.append("Accumulated 5+ health check records.")

    # Reports generated
    if len(ai_reports) >= 3:
        if is_cn:
            achievements.append("已生成 3 份以上 AI 健康报告。")
        else:
            achievements.append("Generated 3+ AI wellness reports.")

    # Score improvements
    if len(health_records) >= 2:
        first_score = getattr(health_records[-1], "health_score", None)
        latest_score = getattr(health_records[0], "health_score", None)
        if first_score is not None and latest_score is not None and latest_score > first_score + 5:
            if is_cn:
                achievements.append(f"健康评分从 {first_score:.0f} 提升至 {latest_score:.0f}。")
            else:
                achievements.append(f"Wellness score improved from {first_score:.0f} to {latest_score:.0f}.")

    if not achievements:
        if is_cn:
            achievements.append("开始记录健康数据，迈出第一步！")
        else:
            achievements.append("Start tracking wellness data — every journey begins with a first step!")

    return achievements
