"""Create health_records table.

Revision ID: 001
Revises:
Create Date: 2026-06-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "health_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=False),

        # Raw inputs
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("height_cm", sa.Float(), nullable=True),
        sa.Column("water_l", sa.Float(), nullable=True),
        sa.Column("situation", sa.String(length=1), nullable=True),
        sa.Column("thirst_level", sa.String(length=1), nullable=True),
        sa.Column("urine_color", sa.String(length=1), nullable=True),
        sa.Column("sleep_hours", sa.Float(), nullable=True),
        sa.Column("night_wake_times", sa.Integer(), nullable=True),
        sa.Column("difficulty_falling_asleep", sa.String(length=1), nullable=True),
        sa.Column("irregular_sleep_schedule", sa.String(length=1), nullable=True),
        sa.Column("exercise_minutes", sa.Integer(), nullable=True),
        sa.Column("sedentary_hours", sa.Integer(), nullable=True),
        sa.Column("fruit_veg_servings", sa.Integer(), nullable=True),
        sa.Column("fast_food_times", sa.Integer(), nullable=True),
        sa.Column("sugary_drinks", sa.Integer(), nullable=True),
        sa.Column("screen_time_hours", sa.Float(), nullable=True),
        sa.Column("smoking", sa.String(length=1), nullable=True),
        sa.Column("alcohol", sa.String(length=1), nullable=True),
        sa.Column("late_night", sa.String(length=1), nullable=True),
        sa.Column("risk_score_emotion", sa.String(length=1), nullable=True),
        sa.Column("risk_score_focus", sa.String(length=1), nullable=True),
        sa.Column("risk_score_body", sa.String(length=1), nullable=True),

        # Module scores
        sa.Column("bmi_score", sa.Integer(), nullable=True),
        sa.Column("water_score", sa.Integer(), nullable=True),
        sa.Column("sleep_score", sa.Integer(), nullable=True),
        sa.Column("activity_score", sa.Integer(), nullable=True),
        sa.Column("diet_score", sa.Integer(), nullable=True),
        sa.Column("mental_score", sa.Integer(), nullable=True),
        sa.Column("screen_score", sa.Integer(), nullable=True),
        sa.Column("habit_score", sa.Integer(), nullable=True),

        # Overall results
        sa.Column("health_score", sa.Float(), nullable=True),
        sa.Column("risk_percent", sa.Float(), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=True),
        sa.Column("risk_score", sa.Integer(), nullable=True),
        sa.Column("max_risk_score", sa.Integer(), nullable=True),
        sa.Column("interaction_score", sa.Integer(), nullable=True),
        sa.Column("overall", sa.Text(), nullable=True),
        sa.Column("primary_focus", sa.Text(), nullable=True),
        sa.Column("action_plan", sa.Text(), nullable=True),

        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("health_records")
