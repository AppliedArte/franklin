"""Add OAuth credentials table for third-party service tokens.

Revision ID: 005
Revises: 004_add_fund_manager_dd_fields
Create Date: 2025-01-03
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "005"
down_revision = "004_add_fund_manager_dd_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_oauth_credentials table
    op.create_table(
        "user_oauth_credentials",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("access_token_encrypted", sa.Text, nullable=False),
        sa.Column("refresh_token_encrypted", sa.Text, nullable=True),
        sa.Column("token_expiry", sa.DateTime, nullable=True),
        sa.Column("scopes", sa.JSON, nullable=True),
        sa.Column("is_valid", sa.Boolean, nullable=False, default=True),
        sa.Column("last_refreshed_at", sa.DateTime, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
    )

    # Add indexes
    op.create_index("ix_user_oauth_credentials_user_id", "user_oauth_credentials", ["user_id"])
    op.create_index("ix_user_oauth_credentials_provider", "user_oauth_credentials", ["provider"])

    # Unique constraint: one credential per user per provider
    op.create_index(
        "uq_user_oauth_user_provider",
        "user_oauth_credentials",
        ["user_id", "provider"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_user_oauth_user_provider", table_name="user_oauth_credentials")
    op.drop_index("ix_user_oauth_credentials_provider", table_name="user_oauth_credentials")
    op.drop_index("ix_user_oauth_credentials_user_id", table_name="user_oauth_credentials")
    op.drop_table("user_oauth_credentials")
