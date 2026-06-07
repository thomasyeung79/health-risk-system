"""Create report_records table.

Revision ID: 003
Revises: 002
Create Date: 2026-06-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "report_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=False),

        # Report configuration
        sa.Column("style", sa.String(length=20), nullable=True),
        sa.Column("provider", sa.String(length=20), nullable=True),
        sa.Column("model", sa.String(length=30), nullable=True),

        # Data snapshot
        sa.Column("health_record_id", sa.Integer(), nullable=True),
        sa.Column("emotion_record_id", sa.Integer(), nullable=True),
        sa.Column("days_analyzed", sa.Integer(), nullable=True),

        # Report content
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("sections", sa.Text(), nullable=True),
        sa.Column("raw_output", sa.Text(), nullable=True),

        # Metadata
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("is_cached", sa.Boolean(), nullable=False, default=False),
        sa.Column("is_fallback", sa.Boolean(), nullable=False, default=False),

        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("report_records")
