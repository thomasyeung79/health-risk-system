"""Consultation ORM model — a wellness consultation session for a member."""

from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Consultation(Base, TimestampMixin):
    """A consultation session linked to a member."""

    __tablename__ = "consultations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    member_id: Mapped[int] = mapped_column(Integer, nullable=False)

    consultation_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    main_concern: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    questionnaire_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Consultation id={self.id} member={self.member_id}>"
