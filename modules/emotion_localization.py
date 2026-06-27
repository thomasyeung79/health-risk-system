"""Shared emotion label localization helpers."""

EMOTION_LABELS_CN = {
    "Calm": "平静",
    "Happy": "愉悦",
    "Relaxed": "放松",
    "Neutral": "平稳",
    "Tired": "疲劳",
    "Stressed": "压力较大",
    "Angry": "愤怒",
    "Sad": "悲伤",
    "Anxious": "焦虑",
    "Low": "低落",
    "Numb": "麻木",
}

EMOTION_KEYS = [
    "Calm",
    "Happy",
    "Relaxed",
    "Neutral",
    "Tired",
    "Stressed",
    "Angry",
    "Sad",
    "Anxious",
    "Low",
    "Numb",
]

MOOD_LABELS = {
    "English": {key: key for key in EMOTION_KEYS},
    "中文": {key: EMOTION_LABELS_CN.get(key, key) for key in EMOTION_KEYS},
}


def localize_emotion(value, language: str = "English"):
    """Return a display label for known emotion keys, preserving unknown values."""
    if value is None:
        return value
    text = str(value)
    if language == "中文":
        return EMOTION_LABELS_CN.get(text, text)
    return text
