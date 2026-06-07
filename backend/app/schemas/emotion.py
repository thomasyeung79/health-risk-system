"""Pydantic models for emotion analysis API."""

from pydantic import BaseModel, Field


class EmotionAnalyzeRequest(BaseModel):
    """Emotion analysis request body."""
    language: str = Field(default="English")
    mood_key: str = Field(..., pattern="^(Calm|Tired|Anxious|Low|Angry|Numb)$")
    event_key: str = Field(..., pattern="^(Nothing special|Had a long day|Academic or work-related issue|Argued with someone|Felt lonely|Felt overwhelmed)$")
    energy: int = Field(..., ge=1, le=10)
    stress: int = Field(..., ge=1, le=10)


class EmotionalPattern(BaseModel):
    pattern: str
    severity: str
    message: str


class Guidance(BaseModel):
    topic: str
    topic_key: str
    support: str
    practice: str


class BreathingPractice(BaseModel):
    title: str
    purpose: str
    steps: list[str]
    type: str


class EmotionAnalyzeResponse(BaseModel):
    id: int
    created_at: str
    language: str
    summary: str
    pattern: EmotionalPattern
    matched_topic: str
    tonight: str
    tomorrow: str
    guidance: Guidance
    breathing: BreathingPractice
    full_story: str


class EmotionRecordSummary(BaseModel):
    id: int
    created_at: str
    language: str
    mood_key: str | None = None
    event_key: str | None = None
    energy: int | None = None
    stress: int | None = None
    pattern_key: str | None = None

    model_config = {"from_attributes": True}


class EmotionRecordDetail(BaseModel):
    id: int
    created_at: str
    language: str
    mood_key: str | None = None
    event_key: str | None = None
    energy: int | None = None
    stress: int | None = None
    pattern_key: str | None = None
    pattern_severity: str | None = None
    summary: str | None = None
    topic_key: str | None = None
    tonight: str | None = None
    tomorrow: str | None = None
    breathing_type: str | None = None
    full_story: str | None = None

    model_config = {"from_attributes": True}


class EmotionRecordsResponse(BaseModel):
    items: list[EmotionRecordSummary]
    total: int
    limit: int
    offset: int


class EmotionStatsResponse(BaseModel):
    total_records: int
    average_energy: float | None = None
    average_stress: float | None = None
    latest_mood: str | None = None
