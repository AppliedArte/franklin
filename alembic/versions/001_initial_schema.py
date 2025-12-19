"""Initial schema - users, profiles, conversations, messages

Revision ID: 001_initial
Revises:
Create Date: 2025-12-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), unique=True, nullable=True),
        sa.Column("phone", sa.String(50), unique=True, nullable=True),
        sa.Column("linkedin_url", sa.String(500), nullable=True),
        sa.Column("whatsapp_id", sa.String(100), unique=True, nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("onboarding_completed", sa.Boolean(), default=False),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_phone", "users", ["phone"])
    op.create_index("ix_users_whatsapp_id", "users", ["whatsapp_id"])

    # User profiles table
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        # Financial snapshot
        sa.Column("annual_income", sa.Float(), nullable=True),
        sa.Column("net_worth", sa.Float(), nullable=True),
        sa.Column("liquid_assets", sa.Float(), nullable=True),
        sa.Column("monthly_expenses", sa.Float(), nullable=True),
        sa.Column("existing_investments", sa.JSON(), nullable=True),
        sa.Column("debts", sa.JSON(), nullable=True),
        # Goals
        sa.Column("primary_goal", sa.String(255), nullable=True),
        sa.Column("goal_timeline", sa.String(100), nullable=True),
        sa.Column("risk_tolerance", sa.String(50), nullable=True),
        sa.Column("interests", sa.JSON(), nullable=True),
        # Profile completeness
        sa.Column("profile_score", sa.Integer(), default=0),
        # Behavior notes (Boardy-style)
        sa.Column("internal_notes", sa.JSON(), nullable=True),
    )

    # Conversations table
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("channel", sa.String(50), nullable=False),
        sa.Column("channel_session_id", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("summary", sa.Text(), nullable=True),
    )
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])
    op.create_index("ix_conversations_channel", "conversations", ["channel"])

    # Messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("conversation_id", sa.String(36), sa.ForeignKey("conversations.id", ondelete="CASCADE")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("channel", sa.String(50), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("embedding", Vector(1536), nullable=True),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index("ix_messages_created_at", "messages", ["created_at"])

    # Partner services table
    op.create_table(
        "partner_services",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("min_net_worth", sa.Float(), nullable=True),
        sa.Column("min_income", sa.Float(), nullable=True),
        sa.Column("risk_profiles", sa.JSON(), nullable=True),
        sa.Column("interests_match", sa.JSON(), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("embedding", Vector(1536), nullable=True),
    )
    op.create_index("ix_partner_services_category", "partner_services", ["category"])
    op.create_index("ix_partner_services_type", "partner_services", ["type"])

    # Referrals table
    op.create_table(
        "referrals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("partner_service_id", sa.String(36), sa.ForeignKey("partner_services.id", ondelete="CASCADE")),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), default="pending"),
        sa.Column("outcome_notes", sa.Text(), nullable=True),
        sa.Column("converted_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_referrals_user_id", "referrals", ["user_id"])
    op.create_index("ix_referrals_status", "referrals", ["status"])


def downgrade() -> None:
    op.drop_table("referrals")
    op.drop_table("partner_services")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("user_profiles")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")
