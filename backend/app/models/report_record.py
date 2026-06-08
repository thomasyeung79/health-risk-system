"""Report record ORM model — caches AI-generated wellness reports."""

from typing import Optional

from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ReportRecord(Base, TimestampMixin):
    """A cached AI-generated wellness report."""

    __tablename__ = "report_records"

    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="English")

    # Report configuration
    style: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    provider: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Data snapshot
    health_record_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    emotion_record_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    days_analyzed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Report content
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sections: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_cached: Mapped[bool] = mapped_column(Boolean, default=False)
    is_fallback: Mapped[bool] = mapped_column(Boolean, default=False)

