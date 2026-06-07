"""Create emotion_records table.

Revision ID: 002
Revises: 001
Create Date: 2026-06-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "emotion_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=False),

        # Input
        sa.Column("mood_key", sa.String(length=20), nullable=True),
        sa.Column("event_key", sa.String(length=30), nullable=True),
        sa.Column("energy", sa.Integer(), nullable=True),
        sa.Column("stress", sa.Integer(), nullable=True),

        # Analysis results
        sa.Column("pattern_key", sa.String(length=30), nullable=True),
        sa.Column("pattern_severity", sa.String(length=10), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("topic_key", sa.String(length=30), nullable=True),
        sa.Column("tonight", sa.Text(), nullable=True),
        sa.Column("tomorrow", sa.Text(), nullable=True),

        # Breathing practice
        sa.Column("breathing_type", sa.String(length=20), nullable=True),

        # Full story
        sa.Column("full_story", sa.Text(), nullable=True),

        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("emotion_records")
