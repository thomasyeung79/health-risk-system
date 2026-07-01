"""Growth Journey service — rule-based personal growth story generation.

Combines member health records, emotion records, consultations, AI reports,
healing plans, and reflections into a timeline-style personal growth story
that feels like a narrative journey.
"""

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.ai_report import AIReport
from app.models.consultation import Consultation
from app.models.daily_reflection import DailyReflection
from app.models.emotion_record import EmotionRecord
from app.models.growth_journey import GrowthJourney
from app.models.healing_plan import HealingPlan
from app.models.health_record import HealthRecord
from app.models.member import Member


def generate_growth_journey(
    db: Session,
    user_id: int,
    member_id: int,
) -> dict[str, Any]:
    """Generate a rule-based growth journey for a member.

    Gathers all available records for the member and assembles a
    narrative timeline, emotional pattern, challenges, actions,
    progress summary, and next-step suggestions.
    """
    member = db.get(Member, member_id)
    if member is None:
        raise ValueError(f"Member {member_id} not found")

    is_cn = (member.preferred_language or "English") == "中文"

    # ── Gather member data ──────────────────────────────
    health_records = (
        db.query(HealthRecord)
        .filter(HealthRecord.user_id == user_id)
        .order_by(HealthRecord.created_at.desc())
        .limit(10)
        .all()
    )
    emotion_records = (
        db.query(EmotionRecord)
        .filter(EmotionRecord.user_id == user_id)
        .order_by(EmotionRecord.created_at.desc())
        .limit(10)
        .all()
    )
    consultations = (
        db.query(Consultation)
        .filter(Consultation.member_id == member_id, Consultation.user_id == user_id)
        .order_by(Consultation.created_at.desc())
        .all()
    )
    ai_reports = (
        db.query(AIReport)
        .filter(AIReport.member_id == member_id, AIReport.user_id == user_id)
        .order_by(AIReport.created_at.desc())
        .all()
    )
    healing_plans = (
        db.query(HealingPlan)
        .filter(HealingPlan.member_id == member_id, HealingPlan.user_id == user_id)
        .all()
    )
    reflections = (
        db.query(DailyReflection)
        .filter(DailyReflection.member_id == member_id, DailyReflection.user_id == user_id)
        .order_by(DailyReflection.created_at.desc())
        .limit(10)
        .all()
    )

    # ── Build narrative timeline ────────────────────────
    timeline_items = _build_narrative_timeline(
        member, health_records, emotion_records,
        consultations, ai_reports, healing_plans,
        reflections, is_cn,
    )

    # ── Emotional pattern ───────────────────────────────
    emotional_pattern = _build_emotional_pattern(emotion_records, is_cn)

    # ── Key challenges ──────────────────────────────────
    key_challenges = _build_key_challenges(
        health_records, consultations, is_cn,
    )

    # ── Healing actions ─────────────────────────────────
    healing_actions = _build_healing_actions(healing_plans, is_cn)

    # ── Progress summary ────────────────────────────────
    progress_summary = _build_progress_summary(
        member, health_records, ai_reports, healing_plans,
        timeline_items, reflections, is_cn,
    )

    # ── Next-step suggestions ───────────────────────────
    next_steps = _build_next_steps(health_records, healing_plans, is_cn)

    # ── Insights ────────────────────────────────────────
    insights = {
        "emotional_pattern": emotional_pattern,
        "key_challenges": key_challenges,
        "healing_actions": healing_actions,
        "progress_summary": progress_summary,
        "next_step_suggestions": next_steps,
    }

    # ── Title & summary ─────────────────────────────────
    title = (
        f"{member.name}'s Wellness Journey"
        if not is_cn
        else f"{member.name} 的健康成长之旅"
    )
    count = len(timeline_items)
    if is_cn:
        summary = (
            f"共记录了 {count} 个成长事件，包含 "
            f"{len(health_records)} 次健康检测、{len(emotion_records)} 次情绪记录、"
            f"{len(consultations)} 次咨询、{len(ai_reports)} 份 AI 报告、"
            f"{len(healing_plans)} 个康复计划、{len(reflections)} 条反思。"
        )
    else:
        summary = (
            f"A total of {count} growth events recorded, spanning "
            f"{len(health_records)} health checks, {len(emotion_records)} emotion records, "
            f"{len(consultations)} consultations, {len(ai_reports)} AI reports, "
            f"{len(healing_plans)} healing plans, and {len(reflections)} reflections."
        )

    # ── Persist ─────────────────────────────────────────
    now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    journey = GrowthJourney(
        user_id=user_id,
        member_id=member_id,
        title=title,
        summary=summary,
        timeline_items=json.dumps(timeline_items, ensure_ascii=False),
        insights=json.dumps(insights, ensure_ascii=False),
        updated_at=now_str,
    )
    db.add(journey)
    db.commit()
    db.refresh(journey)

    return {
        "id": journey.id,
        "member_id": journey.member_id,
        "title": journey.title,
        "summary": journey.summary,
        "timeline_items": timeline_items,
        "insights": insights,
        "created_at": journey.created_at.isoformat(),
        "updated_at": journey.updated_at,
    }


# ── Internal helpers ────────────────────────────────────────────────

def _build_narrative_timeline(
    member: Member,
    health_records: list[HealthRecord],
    emotion_records: list[EmotionRecord],
    consultations: list[Consultation],
    ai_reports: list[AIReport],
    healing_plans: list[HealingPlan],
    reflections: list[DailyReflection],
    is_cn: bool,
) -> list[dict[str, Any]]:
    """Assemble a narrative chronological timeline with story-like flow."""
    events: list[dict[str, Any]] = []

    # ── Member joined ───────────────────────────────────
    if member.created_at:
        events.append({
            "date": member.created_at.isoformat() if hasattr(member.created_at, "isoformat") else str(member.created_at),
            "event_type": "member_created",
            "icon": "🆕",
            "title": "Journey Began" if not is_cn else "旅程开始",
            "description": (
                f"{member.name} started their wellness journey."
                if not is_cn
                else f"{member.name} 开始了健康之旅。"
            ),
        })

    # ── Health checks ───────────────────────────────────
    for r in health_records:
        score = getattr(r, "health_score", None)
        risk = getattr(r, "risk_level", None) or ""
        events.append({
            "date": r.created_at.isoformat() if hasattr(r.created_at, "isoformat") else str(r.created_at),
            "event_type": "health_check",
            "icon": "🩺",
            "title": "Health Assessment" if not is_cn else "健康检测",
            "description": (
                f"Score: {score}/100 — {risk}"
                if not is_cn
                else f"评分：{score}/100 — {risk}"
            ),
        })

    # ── Emotion records ─────────────────────────────────
    for r in emotion_records:
        mood = getattr(r, "mood_key", "Unknown")
        energy = getattr(r, "energy", None)
        stress = getattr(r, "stress", None)
        events.append({
            "date": r.created_at.isoformat() if hasattr(r.created_at, "isoformat") else str(r.created_at),
            "event_type": "emotion_record",
            "icon": "💭",
            "title": "Emotional Check-in" if not is_cn else "情绪记录",
            "description": (
                f"Mood: {mood} | Energy: {energy}/10 | Stress: {stress}/10"
                if not is_cn
                else f"心情：{mood} | 精力：{energy}/10 | 压力：{stress}/10"
            ),
        })

    # ── Consultations ───────────────────────────────────
    for c in consultations:
        ctype = c.consultation_type or "General"
        concern = c.main_concern or ""
        events.append({
            "date": c.created_at.isoformat() if hasattr(c.created_at, "isoformat") else str(c.created_at),
            "event_type": "consultation",
            "icon": "📋",
            "title": (
                f"Consultation: {ctype}" if not is_cn else f"咨询：{ctype}"
            ),
            "description": concern,
        })

    # ── AI reports ──────────────────────────────────────
    for r in ai_reports:
        risk = r.risk_level or "N/A"
        events.append({
            "date": r.created_at.isoformat() if hasattr(r.created_at, "isoformat") else str(r.created_at),
            "event_type": "ai_report",
            "icon": "📊",
            "title": "AI Wellness Report" if not is_cn else "AI 健康报告",
            "description": (
                f"Risk assessment: {risk}"
                if not is_cn
                else f"风险评估：{risk}"
            ),
        })

    # ── Healing plans ───────────────────────────────────
    for p in healing_plans:
        status = p.status or "active"
        events.append({
            "date": p.created_at.isoformat() if hasattr(p.created_at, "isoformat") else str(p.created_at),
            "event_type": "healing_plan",
            "icon": "🎯",
            "title": (
                f"Plan Created: {p.title}" if not is_cn else f"计划创建：{p.title}"
            ),
            "description": (
                f"Status: {status}" if not is_cn else f"状态：{status}"
            ),
        })

    # ── Reflections ─────────────────────────────────────
    for r in reflections:
        went_well = r.went_well or ""
        events.append({
            "date": r.created_at.isoformat() if hasattr(r.created_at, "isoformat") else str(r.created_at),
            "event_type": "reflection",
            "icon": "📝",
            "title": "Daily Reflection" if not is_cn else "每日反思",
            "description": (
                went_well[:120] if went_well else
                ("A moment of reflection." if not is_cn else "一段反思时刻。")
            ),
        })

    # Sort by date descending (most recent first)
    events.sort(key=lambda e: e.get("date", ""), reverse=True)

    # Add improvement markers between key transitions
    if len(events) >= 3:
        # Insert a narrative milestone after every few events
        milestones_added = 0
        for i in range(len(events) - 1, 0, -1):
            if milestones_added >= 2:
                break
            current_type = events[i].get("event_type", "")
            prev_type = events[i - 1].get("event_type", "")
            if current_type != prev_type and i < len(events):
                # Insert a narrative connector
                connector = {
                    "date": "",
                    "event_type": "milestone",
                    "icon": "✨",
                    "title": (
                        "Progress Point" if not is_cn else "进展节点"
                    ),
                    "description": (
                        "A step forward in the wellness journey."
                        if not is_cn
                        else "健康之旅向前迈进的一步。"
                    ),
                }
                events.insert(i, connector)
                milestones_added += 1

    return events


def _build_emotional_pattern(
    emotion_records: list[EmotionRecord],
    is_cn: bool,
) -> str:
    """Summarise emotional patterns from emotion records."""
    if not emotion_records:
        return "No emotion data recorded yet." if not is_cn else "暂无情绪数据。"
    moods = [getattr(r, "mood_key", None) for r in emotion_records if getattr(r, "mood_key", None)]
    energies = [getattr(r, "energy", 5) for r in emotion_records if getattr(r, "energy", None) is not None]

    avg_energy = sum(energies) / len(energies) if energies else 5
    mood_summary = ", ".join(set(moods)) if moods else "N/A"

    if is_cn:
        return (
            f"记录了 {len(emotion_records)} 次情绪。"
            f"主要情绪：{mood_summary}。"
            f"平均精力水平：{avg_energy:.1f}/10。"
        )
    return (
        f"{len(emotion_records)} emotion records captured. "
        f"Key moods: {mood_summary}. "
        f"Average energy level: {avg_energy:.1f}/10."
    )


def _build_key_challenges(
    health_records: list[HealthRecord],
    consultations: list[Consultation],
    is_cn: bool,
) -> list[str]:
    """Identify key challenges from health data and consultations."""
    challenges: list[str] = []

    low_count = sum(
        1 for r in health_records
        if getattr(r, "health_score", 100) is not None and r.health_score < 60
    )
    if low_count > 0:
        challenges.append(
            f"Low health scores detected in {low_count} check(s)."
            if not is_cn
            else f"检测到 {low_count} 次低健康评分。"
        )

    for c in consultations:
        concern = getattr(c, "main_concern", "")
        if concern and concern not in challenges:
            if len(concern) <= 100:
                challenges.append(concern)

    if not challenges:
        challenges.append(
            "No significant challenges identified." if not is_cn else "未发现明显挑战。"
        )

    return challenges


def _build_healing_actions(
    healing_plans: list[HealingPlan],
    is_cn: bool,
) -> list[dict[str, str]]:
    """Extract healing actions from plans."""
    if not healing_plans:
        return [{
            "title": "No healing plans" if not is_cn else "暂无康复计划",
            "status": "—",
        }]

    return [
        {"title": p.title, "status": p.status or "active"}
        for p in healing_plans
    ]


def _build_progress_summary(
    member: Member,
    health_records: list[HealthRecord],
    ai_reports: list[AIReport],
    healing_plans: list[HealingPlan],
    timeline_items: list[dict[str, Any]],
    reflections: list[DailyReflection],
    is_cn: bool,
) -> str:
    """Create a summary of overall progress including reflections."""
    total_events = len(timeline_items)
    report_count = len(ai_reports)
    plan_count = len(healing_plans)
    completed_plans = sum(1 for p in healing_plans if getattr(p, "status", "") == "completed")
    reflection_count = len(reflections)

    if is_cn:
        parts = [
            f"{member.name} 的健康成长之旅包含了 {total_events} 个重要事件。"
        ]
        if report_count:
            parts.append(f"生成了 {report_count} 份 AI 健康报告。")
        if plan_count:
            parts.append(
                f"制定了 {plan_count} 个康复计划，"
                f"已完成 {completed_plans} 个。"
            )
        if reflection_count:
            parts.append(f"{reflection_count} 条反思记录。")
        if not report_count and not plan_count and not reflection_count:
            parts.append("继续记录健康数据，让成长之旅更加完整。")
    else:
        parts = [
            f"{member.name}'s wellness journey includes {total_events} key events."
        ]
        if report_count:
            parts.append(f"{report_count} AI report(s) generated.")
        if plan_count:
            parts.append(
                f"{plan_count} healing plan(s) created, "
                f"{completed_plans} completed."
            )
        if reflection_count:
            parts.append(f"{reflection_count} reflection(s) recorded.")
        if not report_count and not plan_count and not reflection_count:
            parts.append("Keep tracking to build a richer story.")

    return " ".join(parts)


def _build_next_steps(
    health_records: list[HealthRecord],
    healing_plans: list[HealingPlan],
    is_cn: bool,
) -> list[str]:
    """Suggest next steps based on current data."""
    steps: list[str] = []

    if not health_records:
        steps.append(
            "Complete a health check to establish baseline data."
            if not is_cn
            else "完成一次健康检测以建立基准数据。"
        )

    active_plans = [p for p in healing_plans if getattr(p, "status", "") == "active"]
    if active_plans:
        steps.append(
            f"Follow up on {len(active_plans)} active healing plan(s)."
            if not is_cn
            else f"跟进 {len(active_plans)} 个进行中的康复计划。"
        )

    steps.append(
        "Record a daily reflection to track personal growth."
        if not is_cn
        else "记录每日反思以追踪个人成长。"
    )
    steps.append(
        "Schedule a consultation to review progress." if not is_cn else "安排一次咨询以回顾进展。"
    )
    steps.append(
        "Generate a new AI report for updated insights." if not is_cn else "生成新的 AI 报告以获取最新洞察。"
    )

    return steps
