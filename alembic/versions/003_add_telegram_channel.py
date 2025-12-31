"""Add Telegram channel support.

Revision ID: 003
Revises: 002_rag_tables
Create Date: 2024-12-31
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "003"
down_revision = "002_rag_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add telegram_id column to users table
    op.add_column(
        "users",
        sa.Column("telegram_id", sa.String(100), unique=True, nullable=True),
    )

    # Add index for telegram_id lookups
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])


def downgrade() -> None:
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_column("users", "telegram_id")
