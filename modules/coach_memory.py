"""Conversation memory helpers for the AI Coach page."""


PAST_REFERENCE_KEYWORDS = (
    "earlier",
    "you said",
    "before",
    "previously",
    "last time",
    "as mentioned",
    "刚才",
    "你说过",
    "之前",
    "上次",
    "前面",
    "刚刚",
)


def _safe_content(message: dict) -> tuple[str, str] | None:
    if not isinstance(message, dict):
        return None

    role = message.get("role")
    content = message.get("content")

    if role not in {"user", "assistant"}:
        return None

    if not isinstance(content, str):
        return None

    content = content.strip()
    if not content:
        return None

    label = "User" if role == "user" else "Coach"
    return label, content[:150]


def compress_conversation(messages: list[dict], max_turns: int = 5) -> str:
    """Compress recent user/assistant messages into a compact memory string.

    The function is intentionally defensive because chat history lives in
    Streamlit session state and may contain stale or malformed values.
    """
    try:
        if not messages:
            return ""

        max_messages = max(0, int(max_turns)) * 2
        if max_messages == 0:
            return ""

        formatted = []
        for message in messages:
            item = _safe_content(message)
            if item is None:
                continue
            label, content = item
            formatted.append(f"{label}: {content}")

        if not formatted:
            return ""

        return "\n\n".join(formatted[-max_messages:])
    except Exception:
        return ""


def has_reference_to_past(question: str) -> bool:
    """Return whether a question explicitly refers to previous conversation."""
    try:
        if not isinstance(question, str):
            return False

        normalized = question.lower()
        return any(keyword in normalized for keyword in PAST_REFERENCE_KEYWORDS)
    except Exception:
        return False

