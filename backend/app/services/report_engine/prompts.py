"""Prompt templates for AI wellness report generation."""

_SYSTEM_PROMPTS = {
    "English": {
        "balanced": (
            "You are an AI Wellness Analyst. Analyze the user's health and emotion data "
            "and provide a balanced, professional wellness report. "
            "Use clear sections and actionable recommendations."
        ),
        "coaching": (
            "You are a supportive wellness coach. Review the user's health and emotion data "
            "and create an encouraging, motivational report. "
            "Acknowledge progress and suggest realistic next steps."
        ),
        "clinical": (
            "You are a clinical health analyst. Review the user's health and emotion data "
            "and produce a concise, objective assessment. "
            "Focus on risk indicators and evidence-based recommendations."
        ),
    },
    "中文": {
        "balanced": (
            "你是一名 AI 健康分析师。请分析用户的健康与情绪数据，"
            "提供平衡、专业的健康报告。使用清晰的章节和可操作的建议。"
        ),
        "coaching": (
            "你是一名支持型健康教练。请查看用户的健康与情绪数据，"
            "创建鼓励性的、有动力的报告。肯定进展并建议现实的下一步。"
        ),
        "clinical": (
            "你是一名临床健康分析师。请查看用户的健康与情绪数据，"
            "生成简洁、客观的评估。重点关注风险指标和基于证据的建议。"
        ),
    },
}

_SECTION_TEMPLATES = {
    "English": (
        "Please structure your response with the following sections:\n\n"
        "## Health Analysis\n"
        "Summarize the user's physical health status, highlight risk areas, "
        "and note any trends.\n\n"
        "## Emotional State\n"
        "Describe the user's emotional pattern, stress level, and energy trends.\n\n"
        "## Health & Emotion Connection\n"
        "Explain how physical health and emotional state may be influencing each other.\n\n"
        "## Priority Actions\n"
        "List 2-3 specific, actionable recommendations ordered by priority."
    ),
    "中文": (
        "请用以下结构组织你的回复：\n\n"
        "## 健康分析\n"
        "总结用户的身体健康状况，指出风险区域和趋势。\n\n"
        "## 情绪状态\n"
        "描述用户的情绪模式、压力水平和能量趋势。\n\n"
        "## 健康与情绪的关联\n"
        "解释身体健康和情绪状态如何相互影响。\n\n"
        "## 优先行动\n"
        "列出 2-3 条具体的、可操作的建议，按优先级排序。"
    ),
}


def get_system_prompt(language: str, style: str) -> str:
    """Get the system prompt for the given language and style."""
    lang_prompts = _SYSTEM_PROMPTS.get(language, _SYSTEM_PROMPTS["English"])
    system = lang_prompts.get(style, lang_prompts["balanced"])
    section = _SECTION_TEMPLATES.get(language, _SECTION_TEMPLATES["English"])
    return f"{system}\n\n{section}"


def get_user_prompt(context: dict) -> str:
    """Build the user prompt from the context dict produced by ContextBuilder."""
    language = context.get("language", "English")
    lines: list[str] = []

    if language == "中文":
        lines.append("请基于以下健康数据生成综合报告：\n")
    else:
        lines.append("Generate a comprehensive wellness report based on this data:\n")

    # Health summary
    hs = context.get("health_summary")
    if hs:
        if language == "中文":
            lines.append(f"健康评分: {hs['health_score']}/100")
            lines.append(f"风险等级: {hs['risk_level']}")
            lines.append("模块评分:")
            for mod, score in hs["modules"].items():
                if score is not None:
                    lines.append(f"  - {mod}: {score}/3")
        else:
            lines.append(f"Health Score: {hs['health_score']}/100")
            lines.append(f"Risk Level: {hs['risk_level']}")
            lines.append("Module Scores:")
            for mod, score in hs["modules"].items():
                if score is not None:
                    lines.append(f"  - {mod}: {score}/3")
    else:
        lines.append("(No health data available)" if language == "English" else "(无健康数据)")

    # Emotion summary
    es = context.get("emotion_summary")
    if es:
        lines.append("")
        if language == "中文":
            lines.append(f"情绪: {es['mood_key']}")
            lines.append(f"压力: {es['stress']}/10")
            lines.append(f"能量: {es['energy']}/10")
            lines.append(f"情绪模式: {es['pattern_key']}")
        else:
            lines.append(f"Mood: {es['mood_key']}")
            lines.append(f"Stress: {es['stress']}/10")
            lines.append(f"Energy: {es['energy']}/10")
            lines.append(f"Pattern: {es['pattern_key']}")
    else:
        lines.append("(No emotion data available)" if language == "English" else "(无情绪数据)")

    # Trends
    if context.get("trends"):
        lines.append("")
        if language == "中文":
            lines.append("趋势:")
        else:
            lines.append("Trends:")
        for t in context["trends"]:
            lines.append(f"  - {t['type']}: {t['direction']} (change: {t['change']})")

    # Correlations
    if context.get("correlations"):
        lines.append("")
        if language == "中文":
            lines.append("交叉分析:")
        else:
            lines.append("Correlations Found:")
        for c in context["correlations"]:
            lines.append(f"  - {c['description']}")

    # Flags
    if context.get("flags"):
        lines.append("")
        if language == "中文":
            lines.append("预警信号:")
        else:
            lines.append("Flags:")
        for f in context["flags"]:
            lines.append(f"  - {f}")

    return "\n".join(lines)
