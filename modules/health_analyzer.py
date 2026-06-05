"""Health analysis logic — risk scoring, interaction analysis, prioritisation."""

# ── Shared helpers ──────────────────────────────────
def dedup(items):
    """Deduplicate a list while preserving order."""
    return list(dict.fromkeys(items))


# ── Shared bilingual level texts ─────────────────────
LEVEL_TEXTS = {
    "English": {
        "high": "High Risk",
        "medium": "Medium Risk",
        "low": "Low Risk",
        "healthy": "Healthy"
    },
    "中文": {
        "high": "高风险",
        "medium": "中风险",
        "low": "低风险",
        "healthy": "健康"
    }
}


# ── Module labels (bilingual) ───────────────────────
MODULE_LABELS = {
    "English": {
        "BMI": "weight balance",
        "Water": "hydration",
        "Sleep": "sleep recovery",
        "Activity": "daily movement",
        "Diet": "diet quality",
        "Mental": "stress and emotional load",
        "Screen": "screen habits",
        "Habit": "lifestyle habits",
    },
    "中文": {
        "BMI": "体重状态",
        "Water": "饮水状态",
        "Sleep": "睡眠恢复",
        "Activity": "日常活动量",
        "Diet": "饮食质量",
        "Mental": "压力与情绪负荷",
        "Screen": "屏幕使用习惯",
        "Habit": "生活习惯",
    },
}

INTERACTION_TEXT = {
    "English": {
        "sleep_mental": "Sleep problems and mental stress may reinforce each other.",
        "mental_activity": "Stress and inactivity may create a negative cycle.",
        "diet_activity": "Poor diet and low activity may increase long-term health risks.",
        "bmi_water": "Weight and hydration issues may affect overall health together.",
        "screen_sleep": "High screen time may contribute to poor sleep.",
        "screen_mental": "High screen time may increase mental stress.",
        "habit_sleep": "Unhealthy habits may affect sleep quality.",
        "habit_mental": "Unhealthy habits may affect mental well-being.",
        "interaction_high": "Multiple lifestyle factors are interacting and increasing overall health risks.",
        "interaction_low": "Some health factors may be interacting and should be monitored.",
    },
    "中文": {
        "sleep_mental": "睡眠问题与心理压力可能相互影响。",
        "mental_activity": "心理压力与缺乏运动可能形成负面循环。",
        "diet_activity": "饮食不佳与运动不足叠加，可能增加长期健康风险。",
        "bmi_water": "体重与饮水问题可能共同影响整体健康。",
        "screen_sleep": "屏幕时间过长可能影响睡眠质量。",
        "screen_mental": "屏幕时间过长可能加重心理压力。",
        "habit_sleep": "不良生活习惯可能影响睡眠质量。",
        "habit_mental": "不良生活习惯可能影响心理健康。",
        "interaction_high": "多个生活方式因素正在相互影响，并增加整体健康风险。",
        "interaction_low": "部分健康因素之间存在相互影响，建议持续关注。",
    },
}

LEVEL_TEXT = {
    "English": {"healthy": "Healthy", "low": "Low Risk", "medium": "Medium Risk", "high": "High Risk"},
    "中文": {"healthy": "健康", "low": "低风险", "medium": "中风险", "high": "高风险"},
}

OVERALL_TEXT = {
    "English": {
        "healthy": "Your overall pattern looks stable. The best next step is to maintain what is already working instead of making drastic changes.",
        "low": "Your overall pattern is acceptable, with a few early signals worth adjusting before they become harder to manage.",
        "medium": "Several lifestyle factors appear to be stacking together. Focus on one or two high-impact changes first instead of trying to fix everything at once.",
        "high": "Your risk signals are concentrated. Prioritise recovery, stress load, or high-risk habits first, and consider professional support if symptoms persist.",
    },
    "中文": {
        "healthy": "整体状态比较稳定，目前更适合继续巩固已有习惯，而不是做大幅改变。",
        "low": "整体状态尚可，但已经出现一些小信号，适合从一两个最容易执行的习惯开始调整。",
        "medium": "有几个生活方式因素正在叠加影响状态，建议先抓住最关键的一两项，而不是同时改变所有事情。",
        "high": "当前风险信号较集中，建议先处理恢复、压力或高风险习惯等关键问题；如果不适持续，考虑咨询专业人士。",
    },
}

PLAN_TEXT = {
    "English": {
        "Sleep": "Set a clear bedtime tonight and reduce screen stimulation 30 minutes before sleep.",
        "Mental": "Schedule 10 minutes of low-pressure recovery, such as a walk, breathing practice, or writing down the main stressor.",
        "Activity": "Add 10 to 20 minutes of light movement tomorrow and break up long sitting periods.",
        "Diet": "Make one meal more balanced tomorrow with a source of carbs, protein, and vegetables.",
        "Water": "Keep water visible and use one reminder in the morning and one in the afternoon.",
        "Screen": "Create one screen-free block tomorrow, especially before rest or bedtime.",
        "Habit": "Pick the easiest habit to reduce slightly. Aim for one small reduction, not a perfect reset.",
        "BMI": "Focus first on food structure and movement rather than only watching the weight number.",
    },
    "中文": {
        "Sleep": "今晚固定一个上床时间，并在睡前30分钟减少屏幕刺激。",
        "Mental": "给自己安排10分钟低压力恢复时间，比如散步、呼吸或写下今天最困扰的一件事。",
        "Activity": "明天安排一次10到20分钟轻运动，并每坐1小时起身活动一下。",
        "Diet": "明天先把一餐换成更均衡的组合：主食、蛋白质、蔬菜各有一部分。",
        "Water": "明天把水杯放在固定位置，上午和下午各完成一次补水提醒。",
        "Screen": "明天设置一个无屏幕时段，尤其放在睡前或休息前。",
        "Habit": "先选择一个最容易减少的习惯，不追求完全改变，只做一次小幅降低。",
        "BMI": "先关注饮食结构和活动量，不建议只盯体重数字。",
    },
}

MODULE_KEYS = ["BMI", "Water", "Sleep", "Activity", "Diet", "Mental", "Screen", "Habit"]


def calculate_overall_result(results, language):
    """Combine module-level results into an overall health risk assessment."""
    scores = {r["name"]: r.get("score", 0) for r in results}
    max_scores = {r["name"]: r.get("max_score", 3) for r in results}

    risk_score = sum(scores.values())
    max_risk_score = sum(max_scores.values())

    interaction_score = 0
    interaction_notes = []

    def s(name):
        return scores.get(name, 0)

    # ── Interaction logic ───────────────────────────
    pairs = [
        ("Sleep", "Mental", 2, "sleep_mental", s("Sleep") >= 2 and s("Mental") >= 1),
        ("Mental", "Activity", 2, "mental_activity", s("Mental") >= 2 and s("Activity") >= 2),
        ("Diet", "Activity", 1, "diet_activity", s("Diet") >= 2 and s("Activity") >= 2),
        ("BMI", "Water", 1, "bmi_water", s("BMI") > 0 and s("Water") > 0),
        ("Screen", "Sleep", 1, "screen_sleep", s("Screen") >= 2 and s("Sleep") >= 2),
        ("Screen", "Mental", 1, "screen_mental", s("Screen") >= 2 and s("Mental") >= 1),
        ("Habit", "Sleep", 1, "habit_sleep", s("Habit") >= 2 and s("Sleep") >= 2),
        ("Habit", "Mental", 1, "habit_mental", s("Habit") >= 2 and s("Mental") >= 1),
    ]
    for _, _, pts, key, condition in pairs:
        if condition:
            interaction_score += pts
            interaction_notes.append(INTERACTION_TEXT[language][key])

    interaction_notes = list(dict.fromkeys(interaction_notes))
    interaction_score = min(interaction_score, 4)

    risk_score += interaction_score
    max_risk_score += 4
    risk_percent = round((risk_score / max_risk_score) * 100, 1)
    health_score = round(100 - risk_percent, 1)

    if risk_percent >= 70:
        risk_level_key = "high"
    elif risk_percent >= 40:
        risk_level_key = "medium"
    elif risk_percent >= 20:
        risk_level_key = "low"
    else:
        risk_level_key = "healthy"

    risk_level = LEVEL_TEXT[language][risk_level_key]
    overall = OVERALL_TEXT[language][risk_level_key]

    # ── Priority focus ──────────────────────────────
    ranked = sorted(results, key=lambda r: (r.get("score", 0), r.get("max_score", 3)), reverse=True)
    focus_modules = [r["name"] for r in ranked if r.get("score", 0) > 0][:3]

    label_map = MODULE_LABELS[language]
    if focus_modules:
        if language == "中文":
            primary_focus = "当前最值得优先关注的是：" + "、".join(
                label_map.get(n, n) for n in focus_modules
            ) + "。"
        else:
            primary_focus = "Your most useful focus areas right now are " + ", ".join(
                label_map.get(n, n) for n in focus_modules
            ) + "."
    else:
        primary_focus = (
            "目前没有明显高风险模块，重点是保持节奏并继续观察变化。"
            if language == "中文"
            else "No major risk area stands out right now. The main goal is consistency and continued monitoring."
        )

    action_plan = [PLAN_TEXT[language][name] for name in focus_modules[:2]]
    if not action_plan:
        action_plan = [
            "明天继续保持今天的健康习惯，并记录一次睡眠、饮水或情绪变化。"
            if language == "中文"
            else "Tomorrow, keep the current healthy routine and log one sleep, hydration, or mood signal."
        ]

    return {
        "risk_score": risk_score,
        "max_risk_score": max_risk_score,
        "interaction_score": interaction_score,
        "interaction_notes": interaction_notes,
        "risk_percent": risk_percent,
        "health_score": health_score,
        "risk_level": risk_level,
        "overall": overall,
        "primary_focus": primary_focus,
        "action_plan": action_plan,
    }
