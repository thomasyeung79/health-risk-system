"""Growth Journey ORM model — personal wellness growth timeline for a member."""

from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class GrowthJourney(Base, TimestampMixin):
    """A member's personal growth journey — timeline, insights, and next steps."""

    __tablename__ = "growth_journeys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    member_id: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timeline_items: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # JSON
    insights: Mapped[Optional[str]] = mapped_column(Text, nullable=True)          # JSON
    updated_at: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    def __repr__(self) -> str:
        return f"<GrowthJourney id={self.id} member={self.member_id} title={self.title}>"
