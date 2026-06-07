"""Pydantic models for health check API."""

from typing import Any

from pydantic import BaseModel, Field


# ── Request Schemas ──────────────────────────────────

class HealthCheckRequest(BaseModel):
    """Full health check request body."""
    language: str = Field(default="English", description="Language code: English or 中文")

    weight_kg: float = Field(..., ge=20, le=400)
    height_cm: float = Field(..., ge=50, le=300)
    water_l: float = Field(..., ge=0, le=20)
    situation: str = Field(..., pattern="^[A-D]$")
    thirst_level: str = Field(..., pattern="^[A-C]$")
    urine_color: str = Field(..., pattern="^[A-C]$")

    sleep_hours: float = Field(..., ge=0, le=24)
    night_wake_times: int = Field(..., ge=0, le=20)
    difficulty_falling_asleep: str = Field(..., pattern="^[A-C]$")
    irregular_sleep_schedule: str = Field(..., pattern="^[A-C]$")

    exercise_minutes: int = Field(..., ge=0, le=600)
    sedentary_hours: int = Field(..., ge=0, le=24)

    fruit_veg_servings: int = Field(..., ge=0, le=30)
    fast_food_times: int = Field(..., ge=0, le=30)
    sugary_drinks: int = Field(..., ge=0, le=30)

    screen_time_hours: float = Field(..., ge=0, le=24)

    smoking: str = Field(..., pattern="^[A-C]$")
    alcohol: str = Field(..., pattern="^[A-C]$")
    late_night: str = Field(..., pattern="^[A-C]$")

    risk_score_emotion: str = Field(..., pattern="^[A-C]$")
    risk_score_focus: str = Field(..., pattern="^[A-C]$")
    risk_score_body: str = Field(..., pattern="^[A-C]$")


# ── Response Schemas ─────────────────────────────────

class ModuleResult(BaseModel):
    """Result for a single health assessment module."""
    score: int
    level: str
    reasons: list[str]
    suggestions: list[str]


class ModuleMap(BaseModel):
    """Map of module name to result."""
    BMI: ModuleResult
    Water: ModuleResult
    Sleep: ModuleResult
    Activity: ModuleResult
    Diet: ModuleResult
    Mental: ModuleResult
    Screen: ModuleResult
    Habit: ModuleResult


class HealthCheckResponse(BaseModel):
    """Response after running a full health check."""
    id: int
    created_at: str
    language: str
    health_score: float
    risk_percent: float
    risk_level: str
    modules: ModuleMap
    overall: str
    primary_focus: str
    action_plan: list[str]


class HealthRecordSummary(BaseModel):
    """Summary of a single health record for list views."""
    id: int
    created_at: str
    language: str
    health_score: float | None
    risk_percent: float | None
    risk_level: str | None

    model_config = {"from_attributes": True}


class HealthRecordDetail(BaseModel):
    """Full detail of a single health record."""
    id: int
    created_at: str
    language: str
    weight_kg: float | None
    height_cm: float | None
    water_l: float | None
    situation: str | None
    thirst_level: str | None
    urine_color: str | None
    sleep_hours: float | None
    night_wake_times: int | None
    difficulty_falling_asleep: str | None
    irregular_sleep_schedule: str | None
    exercise_minutes: int | None
    sedentary_hours: int | None
    fruit_veg_servings: int | None
    fast_food_times: int | None
    sugary_drinks: int | None
    screen_time_hours: float | None
    smoking: str | None
    alcohol: str | None
    late_night: str | None
    risk_score_emotion: str | None
    risk_score_focus: str | None
    risk_score_body: str | None
    bmi_score: int | None
    water_score: int | None
    sleep_score: int | None
    activity_score: int | None
    diet_score: int | None
    mental_score: int | None
    screen_score: int | None
    habit_score: int | None
    health_score: float | None
    risk_percent: float | None
    risk_level: str | None
    risk_score: int | None
    interaction_score: int | None
    overall: str | None
    primary_focus: str | None
    action_plan: str | None

    model_config = {"from_attributes": True}


class HealthRecordsResponse(BaseModel):
    """Paginated list of health records."""
    items: list[HealthRecordSummary]
    total: int
    limit: int
    offset: int


class HealthStatsResponse(BaseModel):
    """Aggregated health statistics."""
    total_records: int
    average_health_score: float | None
    latest_risk_level: str | None
