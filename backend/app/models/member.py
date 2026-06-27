"""Member profile ORM model — a client/constituent managed by a user."""

from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Member(Base, TimestampMixin):
    """A wellness member/client profile managed by a consultant user."""

    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), nullable=False, default="English")
    contact_info: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Member id={self.id} name={self.name}>"
