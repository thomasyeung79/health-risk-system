import random


TOPIC_OPTIONS = {
    "Pressure Recovery": {
        "English": "Pressure Recovery",
        "中文": "压力恢复",
    },
    "Emotional Awareness": {
        "English": "Emotional Awareness",
        "中文": "情绪觉察",
    },
    "Pause Before Reaction": {
        "English": "Pause Before Reaction",
        "中文": "反应前暂停",
    },
    "Rest and Renewal": {
        "English": "Rest and Renewal",
        "中文": "休息与恢复",
    },
    "Discipline and Action": {
        "English": "Discipline and Action",
        "中文": "自律与行动",
    },
    "Gratitude and Balance": {
        "English": "Gratitude and Balance",
        "中文": "感恩与平衡",
    },
}


SUPPORT_TEXTS = {
    "Pressure Recovery": {
        "English": [
            "Pressure does not need to be solved all at once.",
            "You can reduce overload by choosing one small next step.",
        ],
        "中文": [
            "压力不需要一次全部解决。",
            "你可以通过选择一个小步骤来降低过载感。",
        ],
    },
    "Emotional Awareness": {
        "English": [
            "Naming the emotion is the first step toward regulating it.",
            "Your feelings are signals, not final conclusions.",
        ],
        "中文": [
            "说出情绪，是调节情绪的第一步。",
            "情绪是信号，不是最终结论。",
        ],
    },
    "Pause Before Reaction": {
        "English": [
            "A pause can create space between emotion and response.",
            "You do not need to react immediately to every feeling.",
        ],
        "中文": [
            "暂停可以在情绪和回应之间创造空间。",
            "你不需要对每一种情绪立刻做出反应。",
        ],
    },
    "Rest and Renewal": {
        "English": [
            "Rest is not weakness; it is part of recovery.",
            "Low energy is a signal to slow down, not to blame yourself.",
        ],
        "中文": [
            "休息不是软弱，而是恢复的一部分。",
            "能量偏低是在提醒你慢下来，而不是责备自己。",
        ],
    },
    "Discipline and Action": {
        "English": [
            "Progress often begins with one small action.",
            "You do not need perfect motivation to start.",
        ],
        "中文": [
            "进步常常从一个小行动开始。",
            "开始并不需要完美的动力。",
        ],
    },
    "Gratitude and Balance": {
        "English": [
            "A stable day is also worth noticing.",
            "Gratitude helps the mind recognise what is still supporting you.",
        ],
        "中文": [
            "平稳的一天也值得被看见。",
            "感恩能帮助你看见仍然支撑你的东西。",
        ],
    },
}


PRACTICE_TEXTS = {
    "Pressure Recovery": {
        "English": [
            "Write down one pressure point and one small action.",
            "Remove one unnecessary task from tonight.",
        ],
        "中文": [
            "写下一个压力来源和一个小行动。",
            "今晚删掉一个不必要的任务。",
        ],
    },
    "Emotional Awareness": {
        "English": [
            "Name the emotion without judging it.",
            "Write one sentence beginning with: I feel...",
        ],
        "中文": [
            "说出这个情绪，不急着评价它。",
            "写一句话：我现在感到……",
        ],
    },
    "Pause Before Reaction": {
        "English": [
            "Pause for three breaths before replying.",
            "Choose one calm sentence instead of reacting immediately.",
        ],
        "中文": [
            "回应前先暂停三个呼吸。",
            "选择一句平和的话，而不是立刻反应。",
        ],
    },
    "Rest and Renewal": {
        "English": [
            "Take a short rest without blaming yourself.",
            "Put your phone away for ten minutes.",
        ],
        "中文": [
            "短暂休息，不要责备自己。",
            "把手机放下十分钟。",
        ],
    },
    "Discipline and Action": {
        "English": [
            "Choose one task and work on it for ten minutes.",
            "Start before you feel fully motivated.",
        ],
        "中文": [
            "选择一件事，先做十分钟。",
            "不等状态完美，先开始。",
        ],
    },
    "Gratitude and Balance": {
        "English": [
            "Write down three things you are thankful for today.",
            "Notice one small thing that supported you today.",
        ],
        "中文": [
            "写下今天三件值得感恩的事。",
            "觉察今天一个支持过你的小事。",
        ],
    },
}


def detect_emotional_pattern(clean_mood, clean_things, stress_level, energy_level, language):
    clean_mood = clean_mood or []
    clean_things = clean_things or []

    if stress_level >= 8 and energy_level <= 3:
        return {
            "pattern": "Burnout Risk" if language == "English" else "过载风险",
            "severity": "High" if language == "English" else "高",
            "message": {
                "English": "High stress and low energy may indicate burnout risk.",
                "中文": "高压力与低能量叠加，可能提示疲惫过载风险。",
            }[language],
        }

    if "Anxious" in clean_mood:
        return {
            "pattern": "Overthinking / Anxiety State" if language == "English" else "焦虑与过度思考状态",
            "severity": "Medium" if language == "English" else "中",
            "message": {
                "English": "Anxiety may be increasing mental load and overthinking.",
                "中文": "焦虑可能正在增加心理负担和过度思考。",
            }[language],
        }

    if "Angry" in clean_mood or "Argued with someone" in clean_things:
        return {
            "pattern": "Emotional Tension" if language == "English" else "情绪紧张状态",
            "severity": "Medium" if language == "English" else "中",
            "message": {
                "English": "Emotional tension may be affecting your response style.",
                "中文": "情绪紧张可能正在影响你的回应方式。",
            }[language],
        }

    if "Tired" in clean_mood or energy_level <= 3:
        return {
            "pattern": "Recovery Need" if language == "English" else "恢复需求",
            "severity": "Medium" if language == "English" else "中",
            "message": {
                "English": "Your body and mind may need recovery more than productivity.",
                "中文": "你现在可能更需要恢复，而不是继续追求效率。",
            }[language],
        }

    if "Numb" in clean_mood:
        return {
            "pattern": "Emotional Suppression" if language == "English" else "情绪压抑状态",
            "severity": "Medium" if language == "English" else "中",
            "message": {
                "English": "Emotional numbness may suggest that feelings are being suppressed.",
                "中文": "情绪麻木可能说明一些感受正在被压抑。",
            }[language],
        }

    if "Calm" in clean_mood and stress_level <= 3:
        return {
            "pattern": "Stable / Balanced State" if language == "English" else "稳定平衡状态",
            "severity": "Low" if language == "English" else "低",
            "message": {
                "English": "Your current emotional state appears stable.",
                "中文": "你当前的情绪状态相对稳定。",
            }[language],
        }

    return {
        "pattern": "General Reflection State" if language == "English" else "一般反思状态",
        "severity": "Low" if language == "English" else "低",
        "message": {
            "English": "Your current state is suitable for general reflection and small adjustments.",
            "中文": "你当前状态适合进行一般反思和小幅调整。",
        }[language],
    }


def auto_select_topic(clean_mood, clean_things, stress_level, energy_level):
    clean_mood = clean_mood or []
    clean_things = clean_things or []

    if stress_level >= 8:
        return "Pressure Recovery"

    if "Anxious" in clean_mood or "Numb" in clean_mood:
        return "Emotional Awareness"

    if "Angry" in clean_mood or "Argued with someone" in clean_things:
        return "Pause Before Reaction"

    if "Tired" in clean_mood or energy_level <= 3:
        return "Rest and Renewal"

    if "Academic or work-related issue" in clean_things:
        return "Discipline and Action"

    if "Calm" in clean_mood and stress_level <= 3:
        return "Gratitude and Balance"

    return "Discipline and Action"


def generate_summary(clean_mood, clean_things, stress_level, energy_level, language):
    clean_mood = clean_mood or []

    if language == "中文":
        if stress_level >= 8 and energy_level <= 3:
            return "你现在可能处于明显压力和低能量状态，需要先降低负荷。"
        if stress_level >= 7:
            return "你现在正在经历较明显的压力，适合先做情绪整理。"
        if energy_level <= 3:
            return "你今天的能量偏低，需要给自己一些恢复空间。"
        if "Calm" in clean_mood:
            return "你今天整体较为平静，适合进行感恩、整理和轻量行动。"
        return "你目前状态整体可控，可以通过小步骤继续调整。"

    if stress_level >= 8 and energy_level <= 3:
        return "You may be under strong pressure with low energy. Reducing overload should come first."
    if stress_level >= 7:
        return "You are experiencing noticeable pressure and may benefit from emotional sorting."
    if energy_level <= 3:
        return "Your energy is low today, so recovery should be prioritised."
    if "Calm" in clean_mood:
        return "You seem relatively calm today, which is suitable for gratitude and light action."
    return "Your current state is manageable and can be improved through small adjustments."


def generate_tonight(energy_level, clean_mood, language):
    clean_mood = clean_mood or []

    if language == "中文":
        if energy_level <= 3:
            return "今晚先减少任务量，优先休息，不要继续硬撑。"
        if "Anxious" in clean_mood:
            return "今晚试着慢下来，把注意力带回呼吸和身体。"
        if "Angry" in clean_mood:
            return "今晚先离开让你烦躁的情境，不急着回应。"
        return "今晚让事情简单一点，温和地结束这一天。"

    if energy_level <= 3:
        return "Tonight, reduce your task load and prioritise rest."
    if "Anxious" in clean_mood:
        return "Tonight, slow down and return your attention to your breath and body."
    if "Angry" in clean_mood:
        return "Step away from the frustrating situation before responding."
    return "Keep tonight simple and end the day gently."


def generate_tomorrow(stress_level, clean_things, language):
    clean_things = clean_things or []

    if language == "中文":
        if stress_level >= 8:
            return "明天只专注一个小步骤，不需要一次解决所有问题。"
        if "Academic or work-related issue" in clean_things:
            return "明天先完成一个最小任务，而不是要求自己一次做完。"
        if "Argued with someone" in clean_things:
            return "明天可以用更平和的方式处理关系，不急着证明自己。"
        return "明天可以按照正常节奏继续前进。"

    if stress_level >= 8:
        return "Tomorrow, focus on one small step only."
    if "Academic or work-related issue" in clean_things:
        return "Tomorrow, begin with one minimum task instead of trying to finish everything."
    if "Argued with someone" in clean_things:
        return "Tomorrow, choose a calmer way to handle the relationship."
    return "You can move forward at your normal pace tomorrow."


def generate_reflection_guidance(topic_key, language):
    return {
        "topic": TOPIC_OPTIONS[topic_key][language],
        "topic_key": topic_key,
        "support": random.choice(SUPPORT_TEXTS[topic_key][language]),
        "practice": random.choice(PRACTICE_TEXTS[topic_key][language]),
    }


def generate_breathing_practice(clean_mood, stress_level, energy_level, language):
    clean_mood = clean_mood or []

    if "Anxious" in clean_mood or stress_level >= 8:
        breathing_type = "calming"
        title = {"English": "Calming Breath", "中文": "安定呼吸"}[language]
        purpose = {
            "English": "Reduce anxiety and return to the present moment.",
            "中文": "减轻焦虑，把注意力带回当下。",
        }[language]

    elif "Angry" in clean_mood:
        breathing_type = "pause"
        title = {"English": "Pause Breath", "中文": "暂停呼吸"}[language]
        purpose = {
            "English": "Create space between emotion and reaction.",
            "中文": "在情绪和反应之间创造空间。",
        }[language]

    elif energy_level <= 3 or "Tired" in clean_mood:
        breathing_type = "recovery"
        title = {"English": "Recovery Breath", "中文": "恢复呼吸"}[language]
        purpose = {
            "English": "Restore energy without forcing the body.",
            "中文": "不强迫身体，在温和中恢复能量。",
        }[language]

    else:
        breathing_type = "basic"
        title = {"English": "Mindful Breathing", "中文": "正念呼吸"}[language]
        purpose = {
            "English": "Build awareness through simple breathing.",
            "中文": "通过简单呼吸培养觉察。",
        }[language]

    steps_map = {
        "calming": {
            "English": [
                "Find a quiet place and sit comfortably.",
                "Relax your shoulders.",
                "Inhale slowly through your nose.",
                "Exhale slowly and gently.",
                "Return your attention to your breath.",
                "Continue for 3–5 minutes.",
            ],
            "中文": [
                "找一个安静的地方，舒服地坐下。",
                "放松肩膀。",
                "通过鼻子慢慢吸气。",
                "缓慢而温和地呼气。",
                "把注意力带回呼吸。",
                "持续练习3到5分钟。",
            ],
        },
        "pause": {
            "English": [
                "Pause before reacting.",
                "Take a slow inhale.",
                "Take a longer exhale.",
                "Notice body tension.",
                "Repeat for five breaths.",
                "Choose a calmer response.",
            ],
            "中文": [
                "反应之前先暂停。",
                "慢慢吸一口气。",
                "更长地呼出。",
                "觉察身体紧张。",
                "重复五次呼吸。",
                "选择更平静的回应。",
            ],
        },
        "recovery": {
            "English": [
                "Sit or lie down comfortably.",
                "Place one hand on your abdomen.",
                "Breathe naturally first.",
                "Slowly deepen your breathing if comfortable.",
                "Relax your body with each exhale.",
                "Stop if you feel uncomfortable.",
            ],
            "中文": [
                "舒服地坐下或躺下。",
                "把一只手放在腹部。",
                "先自然呼吸。",
                "如果舒服，再慢慢加深呼吸。",
                "每次呼气时让身体放松。",
                "如果不舒服，就停止。",
            ],
        },
        "basic": {
            "English": [
                "Sit still in a quiet place.",
                "Notice your natural breathing.",
                "Follow each inhale.",
                "Follow each exhale.",
                "Gently return when distracted.",
                "Practice for three minutes.",
            ],
            "中文": [
                "在安静的地方坐稳。",
                "觉察自然呼吸。",
                "跟随每一次吸气。",
                "跟随每一次呼气。",
                "分心时轻轻回到呼吸。",
                "练习三分钟。",
            ],
        },
    }

    return {
        "title": title,
        "purpose": purpose,
        "steps": steps_map[breathing_type][language],
        "type": breathing_type,
    }


def generate_story(summary, pattern, tonight, tomorrow, guidance, breathing, language):
    if language == "中文":
        return f"""
今天你的状态可以这样理解：

**{summary}**

系统识别到的情绪模式：

**{pattern["pattern"]}**  
{pattern["message"]}

今晚建议：

**{tonight}**

明天建议：

**{tomorrow}**

反思支持：

**{guidance["support"]}**

实践步骤：

**{guidance["practice"]}**

呼吸练习：

**{breathing["title"]}** — {breathing["purpose"]}
"""

    return f"""
Today, your current state can be described as:

**{summary}**

Detected emotional pattern:

**{pattern["pattern"]}**  
{pattern["message"]}

Tonight:

**{tonight}**

Tomorrow:

**{tomorrow}**

Reflection support:

**{guidance["support"]}**

Practice step:

**{guidance["practice"]}**

Breathing practice:

**{breathing["title"]}** — {breathing["purpose"]}
"""


def run_reflection_engine(
    clean_mood,
    clean_things,
    stress_level,
    energy_level,
    language,
    topic_mode="Auto",
    manual_topic=None,
):
    pattern = detect_emotional_pattern(
        clean_mood,
        clean_things,
        stress_level,
        energy_level,
        language,
    )

    summary = generate_summary(
        clean_mood,
        clean_things,
        stress_level,
        energy_level,
        language,
    )

    tonight = generate_tonight(
        energy_level,
        clean_mood,
        language,
    )

    tomorrow = generate_tomorrow(
        stress_level,
        clean_things,
        language,
    )

    if topic_mode == "Manual" and manual_topic:
        topic_key = manual_topic
    else:
        topic_key = auto_select_topic(
            clean_mood,
            clean_things,
            stress_level,
            energy_level,
        )

    guidance = generate_reflection_guidance(
        topic_key,
        language,
    )

    breathing = generate_breathing_practice(
        clean_mood,
        stress_level,
        energy_level,
        language,
    )

    story = generate_story(
        summary,
        pattern,
        tonight,
        tomorrow,
        guidance,
        breathing,
        language,
    )

    return {
        "summary": summary,
        "pattern": pattern,
        "matched_topic": TOPIC_OPTIONS[topic_key][language],
        "matched_topic_key": topic_key,
        "tonight": tonight,
        "tomorrow": tomorrow,
        "guidance": guidance,
        "breathing": breathing,
        "story": story,
    }