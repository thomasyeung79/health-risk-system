"""Create members, consultations, ai_reports, healing_plans, community_cases.

Revision ID: 005
Revises: 004
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("gender", sa.String(10), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("preferred_language", sa.String(10), nullable=False, server_default="English"),
        sa.Column("contact_info", sa.String(200), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("consultations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("consultation_type", sa.String(50), nullable=True),
        sa.Column("main_concern", sa.Text(), nullable=True),
        sa.Column("questionnaire_data", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("ai_reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("consultation_id", sa.Integer(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("risk_level", sa.String(20), nullable=True),
        sa.Column("key_findings", sa.Text(), nullable=True),
        sa.Column("recommendations", sa.Text(), nullable=True),
        sa.Column("model_used", sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("healing_plans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("plan_items", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("community_cases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("anonymized_summary", sa.Text(), nullable=True),
        sa.Column("healing_approach", sa.Text(), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("language", sa.String(10), nullable=False, server_default="English"),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("community_cases")
    op.drop_table("healing_plans")
    op.drop_table("ai_reports")
    op.drop_table("consultations")
    op.drop_table("members")
