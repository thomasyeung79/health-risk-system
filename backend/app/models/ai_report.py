"""AI-generated wellness report for a member."""

from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AIReport(Base, TimestampMixin):
    __tablename__ = "ai_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    member_id: Mapped[int] = mapped_column(Integer, nullable=False)
    consultation_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    key_findings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:
        return f"<AIReport id={self.id} member={self.member_id} risk={self.risk_level}>"
