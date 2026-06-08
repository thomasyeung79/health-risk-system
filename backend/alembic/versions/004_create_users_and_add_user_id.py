"""Create users, refresh_tokens, add user_id to all record tables.

Revision ID: 004
Revises: 003
Create Date: 2026-06-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Create users table ─────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("preferred_language", sa.String(length=10), nullable=False, server_default="English"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("idx_users_username", "users", ["username"])

    # ── 2. Create refresh_tokens table ────────────────
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_jti", sa.String(length=36), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],),
    )
    op.create_index("idx_refresh_tokens_jti", "refresh_tokens", ["token_jti"], unique=True)

    # ── 3. Add user_id to existing tables (nullable) ──
    op.add_column("health_records", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("emotion_records", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("report_records", sa.Column("user_id", sa.Integer(), nullable=True))



def downgrade() -> None:
    op.drop_column("report_records", "user_id")
    op.drop_column("emotion_records", "user_id")
    op.drop_column("health_records", "user_id")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
