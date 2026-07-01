"""AI Coach service — generates daily coaching messages.

Not a chatbot. Produces one daily coaching message with:
  - Today's focus
  - Small habit suggestion
  - Motivation
  - Wellness reminder

Uses RuleBasedProvider now, compatible with OpenAI/DeepSeek later.
"""

import random
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.member import Member


# ── Message pools ───────────────────────────────────────────────────

_FOCUS_TOPICS_EN = [
    "Mindful breathing",
    "Posture check",
    "Hydration goal",
    "Step count",
    "Sleep schedule",
    "Screen break",
    "Gratitude moment",
    "Stretching break",
    "Vegetable serving",
    "Walking meeting",
]

_FOCUS_TOPICS_CN = [
    "正念呼吸",
    "姿势检查",
    "饮水目标",
    "步数目标",
    "睡眠规律",
    "屏幕休息",
    "感恩时刻",
    "拉伸放松",
    "蔬果摄入",
    "步行会议",
]

_HABITS_EN = [
    "Drink a glass of water right after waking up.",
    "Try a 5-minute morning stretch.",
    "Take a 2-minute standing break every hour.",
    "Eat one piece of fruit with lunch.",
    "Write down one thing you are grateful for today.",
    "Close your eyes and take 5 deep breaths.",
    "Go for a 10-minute walk after dinner.",
    "Put your phone away 30 minutes before bed.",
    "Replace one sugary drink with water today.",
    "Stand up when taking phone calls.",
]

_HABITS_CN = [
    "起床后立即喝一杯水。",
    "尝试 5 分钟晨间拉伸。",
    "每小时站立休息 2 分钟。",
    "午餐时吃一份水果。",
    "写下今天感恩的一件事。",
    "闭上眼睛做 5 次深呼吸。",
    "晚饭后散步 10 分钟。",
    "睡前 30 分钟放下手机。",
    "今天用喝水代替一瓶含糖饮料。",
    "接电话时站起来。",
]

_MOTIVATION_EN = [
    "Small steps lead to big changes. Keep going!",
    "Every healthy choice adds up. You are building a stronger you.",
    "Progress, not perfection. Today matters.",
    "Your body and mind are worth the effort.",
    "Consistency beats intensity. Show up for yourself every day.",
    "Wellness is a journey, not a destination. Enjoy every step.",
    "You have the power to shape your habits. Start today.",
    "Be kind to yourself — growth takes time.",
]

_MOTIVATION_CN = [
    "小步积累，成就大改变。继续加油！",
    "每一个健康选择都在累积。你在打造更强大的自己。",
    "进步而非完美。每一天都很重要。",
    "你的身心值得这份付出。",
    "持续胜过强度。每天为自己而行动。",
    "健康是一段旅程，而非终点。享受每一步。",
    "你有能力塑造自己的习惯。从今天开始。",
    "对自己温柔一点——成长需要时间。",
]

_REMINDERS_EN = [
    "Have you done your health check this week?",
    "Remember to log your emotions today.",
    "Check in with your healing plan progress.",
    "Take a moment to assess how you are feeling right now.",
    "Review your wellness goals for the week.",
    "Don't forget to track your water intake.",
    "How was your sleep last night? Log it!",
]

_REMINDERS_CN = [
    "这周完成健康检测了吗？",
    "记得记录今天的情绪状态。",
    "查看一下康复计划的进展。",
    "花一点时间感受当下的状态。",
    "回顾本周的健康目标。",
    "别忘了记录饮水量。",
    "昨晚睡得好吗？记录一下吧！",
]


def generate_daily_message(
    db: Session,
    user_id: int,
    member_id: int,
) -> dict[str, Any]:
    """Generate a daily coaching message for a member.

    Uses deterministic rule-based logic (no external API calls).
    Future versions may delegate to AIProvider subclasses.
    """
    member = db.get(Member, member_id)
    if member is None:
        raise ValueError(f"Member {member_id} not found")

    is_cn = (member.preferred_language or "English") == "中文"

    # Use member ID and current date as seed for reproducibility
    today = datetime.utcnow().strftime("%Y-%m-%d")
    seed = hash(f"{member_id}-{today}-{user_id}")
    rng = random.Random(seed)

    if is_cn:
        focus = rng.choice(_FOCUS_TOPICS_CN)
        habit = rng.choice(_HABITS_CN)
        motivation = rng.choice(_MOTIVATION_CN)
        reminder = rng.choice(_REMINDERS_CN)
        title = "今日健康提示"
    else:
        focus = rng.choice(_FOCUS_TOPICS_EN)
        habit = rng.choice(_HABITS_EN)
        motivation = rng.choice(_MOTIVATION_EN)
        reminder = rng.choice(_REMINDERS_EN)
        title = "Daily Wellness Tip"

    content_parts = [
        f"🎯 **{focus}**",
        f"💡 {habit}",
        f"✨ {motivation}",
        f"📌 {reminder}",
    ]
    content = "\n\n".join(content_parts)

    return {
        "member_id": member_id,
        "date": today,
        "message_type": "daily_coaching",
        "title": title,
        "content": content,
    }
