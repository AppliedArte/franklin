"""Add RAG tables - documents, chunks, user_facts, calls

Revision ID: 002_rag_tables
Revises: 001_initial
Create Date: 2025-12-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "002_rag_tables"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Documents table - user uploaded documents
    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        # Document metadata
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("doc_type", sa.String(50), nullable=False, server_default="other"),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        # Storage
        sa.Column("storage_url", sa.String(1000), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        # Processing status
        sa.Column("is_processed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("processing_error", sa.Text(), nullable=True),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_documents_user_id", "documents", ["user_id"])
    op.create_index("ix_documents_doc_type", "documents", ["doc_type"])

    # Document chunks table - chunked and embedded content
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("document_id", sa.String(36), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        # Chunk content
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False, server_default="0"),
        # Metadata
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("section_title", sa.String(500), nullable=True),
        # Vector embedding
        sa.Column("embedding", Vector(1536), nullable=True),
    )
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])

    # User facts table - extracted facts from conversations
    op.create_table(
        "user_facts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        # Fact content
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("fact", sa.Text(), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        # Context
        sa.Column("conversation_id", sa.String(36), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
        # Vector embedding
        sa.Column("embedding", Vector(1536), nullable=True),
    )
    op.create_index("ix_user_facts_user_id", "user_facts", ["user_id"])
    op.create_index("ix_user_facts_category", "user_facts", ["category"])

    # Calls table - voice call tracking
    op.create_table(
        "calls",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        # Vapi integration
        sa.Column("vapi_call_id", sa.String(100), unique=True, nullable=True),
        # Scheduling
        sa.Column("scheduled_for", sa.DateTime(), nullable=True),
        # Call status & timing
        sa.Column("status", sa.String(50), nullable=False, server_default="scheduled"),
        sa.Column("initiated_at", sa.DateTime(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        # Call content
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        # Outcome
        sa.Column("outcome", sa.String(50), nullable=True),
        sa.Column("outcome_notes", sa.Text(), nullable=True),
        # Profile data extracted
        sa.Column("extracted_data", sa.JSON(), nullable=True),
        # Retry tracking
        sa.Column("attempt_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("next_retry_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_calls_user_id", "calls", ["user_id"])
    op.create_index("ix_calls_status", "calls", ["status"])
    op.create_index("ix_calls_scheduled_for", "calls", ["scheduled_for"])
    op.create_index("ix_calls_vapi_call_id", "calls", ["vapi_call_id"])

    # Add missing columns to users table
    op.add_column("users", sa.Column("gender", sa.String(20), nullable=True))
    op.add_column("users", sa.Column("age", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("profession", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("lead_status", sa.String(50), nullable=False, server_default="new"))
    op.add_column("users", sa.Column("lead_source", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("signed_up_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("areas_of_interest", sa.JSON(), nullable=True))
    op.add_column("users", sa.Column("financial_goals", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("asset_classes_of_interest", sa.JSON(), nullable=True))
    op.add_column("users", sa.Column("how_can_franklin_help", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("timezone", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("availability_windows", sa.JSON(), nullable=True))
    op.create_index("ix_users_lead_status", "users", ["lead_status"])

    # Add missing columns to user_profiles table
    op.add_column("user_profiles", sa.Column("investor_type", sa.String(50), nullable=True))
    op.add_column("user_profiles", sa.Column("is_accredited", sa.Boolean(), nullable=True))
    op.add_column("user_profiles", sa.Column("alternative_investments", sa.JSON(), nullable=True))
    op.add_column("user_profiles", sa.Column("crypto_holdings", sa.JSON(), nullable=True))
    op.add_column("user_profiles", sa.Column("private_investments", sa.JSON(), nullable=True))
    op.add_column("user_profiles", sa.Column("experience_level", sa.String(50), nullable=True))
    op.add_column("user_profiles", sa.Column("experience_areas", sa.JSON(), nullable=True))
    op.add_column("user_profiles", sa.Column("current_deal_flow", sa.JSON(), nullable=True))
    op.add_column("user_profiles", sa.Column("liquidity_needs", sa.String(255), nullable=True))
    op.add_column("user_profiles", sa.Column("concentration_risks", sa.JSON(), nullable=True))
    op.add_column("user_profiles", sa.Column("fund_relationships", sa.JSON(), nullable=True))
    op.add_column("user_profiles", sa.Column("deal_flow_sources", sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove added columns from user_profiles
    op.drop_column("user_profiles", "deal_flow_sources")
    op.drop_column("user_profiles", "fund_relationships")
    op.drop_column("user_profiles", "concentration_risks")
    op.drop_column("user_profiles", "liquidity_needs")
    op.drop_column("user_profiles", "current_deal_flow")
    op.drop_column("user_profiles", "experience_areas")
    op.drop_column("user_profiles", "experience_level")
    op.drop_column("user_profiles", "private_investments")
    op.drop_column("user_profiles", "crypto_holdings")
    op.drop_column("user_profiles", "alternative_investments")
    op.drop_column("user_profiles", "is_accredited")
    op.drop_column("user_profiles", "investor_type")

    # Remove added columns from users
    op.drop_index("ix_users_lead_status", table_name="users")
    op.drop_column("users", "availability_windows")
    op.drop_column("users", "timezone")
    op.drop_column("users", "how_can_franklin_help")
    op.drop_column("users", "asset_classes_of_interest")
    op.drop_column("users", "financial_goals")
    op.drop_column("users", "areas_of_interest")
    op.drop_column("users", "signed_up_at")
    op.drop_column("users", "lead_source")
    op.drop_column("users", "lead_status")
    op.drop_column("users", "profession")
    op.drop_column("users", "age")
    op.drop_column("users", "gender")

    # Drop new tables
    op.drop_table("calls")
    op.drop_table("user_facts")
    op.drop_table("document_chunks")
    op.drop_table("documents")
