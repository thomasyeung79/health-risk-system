"""Daily Reflection ORM model — personal daily wellness reflection entries."""

from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class DailyReflection(Base, TimestampMixin):
    """A daily wellness reflection entry for a member."""

    __tablename__ = "daily_reflections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    member_id: Mapped[int] = mapped_column(Integer, nullable=False)

    went_well: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    biggest_challenge: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gratitude: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<DailyReflection id={self.id} member={self.member_id}>"
