"""Pattern Discovery Engine — automatically discovers long-term behaviour patterns.

Analyses health records and emotion records to find correlations such as:
  - Stress increases after poor sleep
  - Low energy follows high workload
  - Anxiety decreases after regular exercise
  - Meditation correlates with improved mood
"""

import statistics
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.emotion_record import EmotionRecord
from app.models.health_record import HealthRecord
from app.models.member import Member


def discover_patterns(
    db: Session,
    user_id: int,
    member_id: int,
) -> dict[str, Any]:
    """Discover behavioural patterns for a given member.

    Returns a dict with a 'patterns' list — each pattern has:
      title, confidence (0-1), evidence, recommendation.
    """
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

    patterns: list[dict[str, Any]] = []

    # ── Pattern 1: Sleep → Stress correlation ───────────
    sleep_stress = _correlate_sleep_stress(health_records, emotion_records, is_cn)
    if sleep_stress:
        patterns.append(sleep_stress)

    # ── Pattern 2: Exercise → Energy correlation ─────────
    exercise_energy = _correlate_exercise_energy(health_records, emotion_records, is_cn)
    if exercise_energy:
        patterns.append(exercise_energy)

    # ── Pattern 3: Overall health trajectory ─────────────
    health_trend = _detect_health_trend(health_records, is_cn)
    if health_trend:
        patterns.append(health_trend)

    # ── Pattern 4: Emotional stability ───────────────────
    emotional_stability = _assess_emotional_stability(emotion_records, is_cn)
    if emotional_stability:
        patterns.append(emotional_stability)

    # ── Pattern 5: Diet ↔ Energy pattern ─────────────────
    diet_energy = _correlate_diet_energy(health_records, emotion_records, is_cn)
    if diet_energy:
        patterns.append(diet_energy)

    if not patterns:
        patterns.append(_no_pattern_found(is_cn))

    return {"member_id": member_id, "patterns": patterns}


# ── Internal pattern detectors ──────────────────────────────────────


def _correlate_sleep_stress(
    health_records: list[HealthRecord],
    emotion_records: list[EmotionRecord],
    is_cn: bool,
) -> dict | None:
    """Check if poor sleep correlates with higher stress."""
    if len(health_records) < 2 or not emotion_records:
        return None

    poor_sleep_days = [
        r for r in health_records
        if getattr(r, "sleep_hours", None) is not None and r.sleep_hours < 6
    ]

    if not poor_sleep_days:
        return None

    # Find emotion records near poor-sleep dates
    high_stress_after_poor_sleep = 0
    for hr in poor_sleep_days:
        hr_date = hr.created_at
        nearby = [
            e for e in emotion_records
            if getattr(e, "stress", None) is not None
            and abs((e.created_at - hr_date).total_seconds()) < 172800  # 48h
            and e.stress >= 7
        ]
        high_stress_after_poor_sleep += len(nearby)

    total_nearby = sum(
        1 for hr in poor_sleep_days
        for e in emotion_records
        if getattr(e, "stress", None) is not None
        and abs((e.created_at - hr.created_at).total_seconds()) < 172800
    )

    if total_nearby == 0:
        return None

    ratio = high_stress_after_poor_sleep / total_nearby
    if ratio < 0.4:
        return None

    confidence = round(min(ratio, 0.95), 2)

    if is_cn:
        return {
            "title": "睡眠不足与压力增加相关",
            "confidence": confidence,
            "evidence": f"在 {len(poor_sleep_days)} 次睡眠不足（<6小时）后，"
                       f"记录了 {high_stress_after_poor_sleep} 次高压力事件。",
            "recommendation": "优先保证 7-8 小时睡眠。尝试睡前 1 小时减少屏幕使用。",
        }
    return {
        "title": "Poor sleep correlates with increased stress",
        "confidence": confidence,
        "evidence": f"After {len(poor_sleep_days)} instance(s) of poor sleep (<6h), "
                   f"{high_stress_after_poor_sleep} high-stress event(s) were recorded within 48h.",
        "recommendation": "Prioritise 7-8 hours of sleep. Try reducing screen time 1h before bed.",
    }


def _correlate_exercise_energy(
    health_records: list[HealthRecord],
    emotion_records: list[EmotionRecord],
    is_cn: bool,
) -> dict | None:
    """Check if exercise correlates with higher energy."""
    if len(health_records) < 2 or not emotion_records:
        return None

    active_days = [
        r for r in health_records
        if getattr(r, "exercise_minutes", None) is not None and r.exercise_minutes >= 30
    ]

    if not active_days:
        return None

    high_energy_after_exercise = 0
    for hr in active_days:
        hr_date = hr.created_at
        nearby = [
            e for e in emotion_records
            if getattr(e, "energy", None) is not None
            and abs((e.created_at - hr_date).total_seconds()) < 86400  # 24h
            and e.energy >= 7
        ]
        high_energy_after_exercise += len(nearby)

    total_nearby = sum(
        1 for hr in active_days
        for e in emotion_records
        if getattr(e, "energy", None) is not None
        and abs((e.created_at - hr.created_at).total_seconds()) < 86400
    )

    if total_nearby == 0:
        return None

    ratio = high_energy_after_exercise / total_nearby
    if ratio < 0.4:
        return None

    confidence = round(min(ratio, 0.95), 2)

    if is_cn:
        return {
            "title": "运动后精力水平提升",
            "confidence": confidence,
            "evidence": f"在 {len(active_days)} 次运动日（≥30分钟）后，"
                       f"{high_energy_after_exercise}/{total_nearby} 的情绪记录显示高精力水平。",
            "recommendation": "保持每周至少 3 次 30 分钟以上的运动，以维持精力水平。",
        }
    return {
        "title": "Exercise correlates with higher energy levels",
        "confidence": confidence,
        "evidence": f"After {len(active_days)} active day(s) (≥30min exercise), "
                   f"{high_energy_after_exercise}/{total_nearby} emotion records show high energy.",
        "recommendation": "Maintain at least 3 sessions of 30+ min exercise per week.",
    }


def _detect_health_trend(
    health_records: list[HealthRecord],
    is_cn: bool,
) -> dict | None:
    """Detect whether health scores are improving, stable, or declining."""
    if len(health_records) < 3:
        return None

    scores = [
        r.health_score for r in reversed(health_records)
        if getattr(r, "health_score", None) is not None
    ]
    if len(scores) < 3:
        return None

    # Compare first half vs second half
    mid = len(scores) // 2
    first_half = scores[:mid]
    second_half = scores[mid:]
    avg_first = statistics.mean(first_half)
    avg_second = statistics.mean(second_half)
    diff = avg_second - avg_first
    confidence = round(min(abs(diff) / 20 + 0.5, 0.95), 2)

    if diff > 5:
        if is_cn:
            return {
                "title": "健康评分呈上升趋势",
                "confidence": confidence,
                "evidence": f"近期平均评分 ({avg_second:.0f}) 高于早期 ({avg_first:.0f})，"
                           f"提升了 {diff:.0f} 分。",
                "recommendation": "继续保持当前的健康习惯。",
            }
        return {
            "title": "Health score shows an improving trend",
            "confidence": confidence,
            "evidence": f"Recent average score ({avg_second:.0f}) is higher than earlier ({avg_first:.0f}), "
                       f"improving by {diff:.0f} points.",
            "recommendation": "Keep up your current wellness habits.",
        }
    elif diff < -5:
        if is_cn:
            return {
                "title": "健康评分呈下降趋势",
                "confidence": confidence,
                "evidence": f"近期平均评分 ({avg_second:.0f}) 低于早期 ({avg_first:.0f})，"
                           f"下降了 {abs(diff):.0f} 分。",
                "recommendation": "建议进行一次健康评估，关注下降的指标。",
            }
        return {
            "title": "Health score shows a declining trend",
            "confidence": confidence,
            "evidence": f"Recent average score ({avg_second:.0f}) is lower than earlier ({avg_first:.0f}), "
                       f"declining by {abs(diff):.0f} points.",
            "recommendation": "Consider a health check-up to identify declining areas.",
        }
    return None


def _assess_emotional_stability(
    emotion_records: list[EmotionRecord],
    is_cn: bool,
) -> dict | None:
    """Assess emotional stability from stress and mood variability."""
    if len(emotion_records) < 4:
        return None

    stress_values = [
        e.stress for e in emotion_records
        if getattr(e, "stress", None) is not None
    ]
    if len(stress_values) < 4:
        return None

    avg_stress = statistics.mean(stress_values)
    stdev = statistics.stdev(stress_values) if len(stress_values) > 1 else 0

    if avg_stress < 4 and stdev < 2:
        confidence = round(min(0.6 + stdev / 4, 0.9), 2)
        if is_cn:
            return {
                "title": "情绪状态稳定",
                "confidence": confidence,
                "evidence": f"平均压力水平 {avg_stress:.1f}/10，波动幅度小 (σ={stdev:.1f})。",
                "recommendation": "维持当前的情绪管理习惯。",
            }
        return {
            "title": "Emotional state is stable",
            "confidence": confidence,
            "evidence": f"Average stress level {avg_stress:.1f}/10 with low variability (σ={stdev:.1f}).",
            "recommendation": "Maintain your current emotional management habits.",
        }

    if avg_stress >= 6 and stdev > 1.5:
        confidence = round(min(0.5 + stdev / 5, 0.9), 2)
        if is_cn:
            return {
                "title": "压力水平偏高且波动较大",
                "confidence": confidence,
                "evidence": f"平均压力水平 {avg_stress:.1f}/10，波动幅度较大 (σ={stdev:.1f})。",
                "recommendation": "尝试每日正念练习或深呼吸，必要时寻求专业支持。",
            }
        return {
            "title": "Stress levels are elevated and variable",
            "confidence": confidence,
            "evidence": f"Average stress level {avg_stress:.1f}/10 with significant variability (σ={stdev:.1f}).",
            "recommendation": "Try daily mindfulness or deep breathing exercises. Seek professional support if needed.",
        }
    return None


def _correlate_diet_energy(
    health_records: list[HealthRecord],
    emotion_records: list[EmotionRecord],
    is_cn: bool,
) -> dict | None:
    """Check if healthy diet correlates with higher energy."""
    if len(health_records) < 2 or not emotion_records:
        return None

    healthy_diet_days = [
        r for r in health_records
        if getattr(r, "fruit_veg_servings", None) is not None
        and r.fruit_veg_servings >= 5
        and getattr(r, "fast_food_times", 1) is not None
        and (r.fast_food_times or 0) <= 1
        and getattr(r, "sugary_drinks", 1) is not None
        and (r.sugary_drinks or 0) <= 1
    ]

    if not healthy_diet_days:
        return None

    high_energy_after_good_diet = 0
    for hr in healthy_diet_days:
        hr_date = hr.created_at
        nearby = [
            e for e in emotion_records
            if getattr(e, "energy", None) is not None
            and abs((e.created_at - hr_date).total_seconds()) < 86400
            and e.energy >= 7
        ]
        high_energy_after_good_diet += len(nearby)

    total_nearby = sum(
        1 for hr in healthy_diet_days
        for e in emotion_records
        if getattr(e, "energy", None) is not None
        and abs((e.created_at - hr.created_at).total_seconds()) < 86400
    )

    if total_nearby == 0:
        return None

    ratio = high_energy_after_good_diet / total_nearby
    if ratio < 0.4:
        return None

    confidence = round(min(ratio, 0.95), 2)

    if is_cn:
        return {
            "title": "健康饮食与高精力相关",
            "confidence": confidence,
            "evidence": f"在 {len(healthy_diet_days)} 次健康饮食记录后，"
                       f"{high_energy_after_good_diet}/{total_nearby} 显示高精力。",
            "recommendation": "坚持每日 5 份蔬果，减少快餐和含糖饮料。",
        }
    return {
        "title": "Healthy diet correlates with higher energy",
        "confidence": confidence,
        "evidence": f"After {len(healthy_diet_days)} healthy diet day(s), "
                   f"{high_energy_after_good_diet}/{total_nearby} records show high energy.",
        "recommendation": "Maintain 5+ servings of fruits/vegetables daily, limit fast food and sugary drinks.",
    }


def _no_pattern_found(is_cn: bool) -> dict:
    """Return a default pattern when insufficient data exists."""
    if is_cn:
        return {
            "title": "数据不足，无法发现模式",
            "confidence": 0.0,
            "evidence": "当前数据量不足以进行模式分析。",
            "recommendation": "建议定期记录健康检测和情绪数据，积累足够数据后再次分析。",
        }
    return {
        "title": "Insufficient data for pattern discovery",
        "confidence": 0.0,
        "evidence": "Not enough data to identify meaningful patterns yet.",
        "recommendation": "Continue logging health checks and emotion records regularly, then re-run analysis.",
    }
