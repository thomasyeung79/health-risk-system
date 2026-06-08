"""Health check record ORM model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class HealthRecord(Base, TimestampMixin):
    """A single health check assessment record."""

    __tablename__ = "health_records"

    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ── Primary key ─────────────────────────────────
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ── Metadata ────────────────────────────────────
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")

    # ── Raw inputs ──────────────────────────────────
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    water_l: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    situation: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    thirst_level: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    urine_color: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)

    sleep_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    night_wake_times: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    difficulty_falling_asleep: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    irregular_sleep_schedule: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)

    exercise_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sedentary_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    fruit_veg_servings: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fast_food_times: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sugary_drinks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    screen_time_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    smoking: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    alcohol: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    late_night: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)

    risk_score_emotion: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    risk_score_focus: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    risk_score_body: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)

    # ── Module scores (0-3, higher = worse) ─────────
    bmi_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    water_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sleep_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    activity_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    diet_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mental_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    screen_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    habit_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ── Overall results ─────────────────────────────
    health_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    risk_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_risk_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    interaction_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    overall: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_focus: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<HealthRecord id={self.id} score={self.health_score} level={self.risk_level}>"

