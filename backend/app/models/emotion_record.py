"""Emotion analysis record ORM model."""

from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class EmotionRecord(Base, TimestampMixin):
    """A single emotion analysis record."""

    __tablename__ = "emotion_records"

    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ── Primary key ─────────────────────────────────
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ── Metadata ────────────────────────────────────
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="English")

    # ── Input ───────────────────────────────────────
    mood_key: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    event_key: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    energy: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stress: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ── Analysis results ────────────────────────────
    pattern_key: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    pattern_severity: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    topic_key: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    tonight: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tomorrow: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── Breathing practice ──────────────────────────
    breathing_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # ── Full story text ─────────────────────────────
    full_story: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<EmotionRecord id={self.id} mood={self.mood_key} stress={self.stress}>"

