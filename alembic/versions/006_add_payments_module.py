"""Add payments module tables for autonomous spending.

Creates tables for:
- spending_rules: User-defined spending limits and auto-approval thresholds
- payment_methods: Stored payment methods (virtual cards, etc.)
- purchases: Transaction history and audit trail

Revision ID: 006
Revises: 005
Create Date: 2026-01-03
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================================================================
    # Spending Rules Table
    # =========================================================================
    op.create_table(
        "spending_rules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        # Category this rule applies to
        sa.Column("category", sa.String(50), nullable=False),
        # Spending limits
        sa.Column("max_per_transaction", sa.Float, nullable=False, default=500.0),
        sa.Column("max_daily", sa.Float, nullable=True),
        sa.Column("max_weekly", sa.Float, nullable=True),
        sa.Column("max_monthly", sa.Float, nullable=True),
        # Auto-approval thresholds
        sa.Column("auto_approve_under", sa.Float, nullable=False, default=100.0),
        sa.Column("notify_only_under", sa.Float, nullable=False, default=500.0),
        # Preferences (JSON)
        sa.Column("preferences", sa.JSON, nullable=True),
        # Merchant controls
        sa.Column("allowed_merchants", sa.JSON, nullable=True),
        sa.Column("blocked_merchants", sa.JSON, nullable=True),
        # Status
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
    )

    op.create_index("ix_spending_rules_user_id", "spending_rules", ["user_id"])
    op.create_index("ix_spending_rules_category", "spending_rules", ["category"])
    op.create_index(
        "uq_spending_rules_user_category",
        "spending_rules",
        ["user_id", "category"],
        unique=True,
    )

    # =========================================================================
    # Payment Methods Table
    # =========================================================================
    op.create_table(
        "payment_methods",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        # Method details
        sa.Column("method_type", sa.String(50), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("nickname", sa.String(100), nullable=False),
        # Card details (encrypted)
        sa.Column("card_number_encrypted", sa.Text, nullable=True),
        sa.Column("expiry_encrypted", sa.Text, nullable=True),
        sa.Column("cvv_encrypted", sa.Text, nullable=True),
        # For API-based providers
        sa.Column("external_card_id", sa.String(100), nullable=True),
        # Billing address
        sa.Column("billing_name", sa.String(255), nullable=True),
        sa.Column("billing_address", sa.JSON, nullable=True),
        # Card limits
        sa.Column("spending_limit", sa.Float, nullable=True),
        sa.Column("spending_limit_period", sa.String(50), nullable=True),
        # Usage tracking
        sa.Column("amount_spent", sa.Float, nullable=False, default=0.0),
        sa.Column("last_used_at", sa.DateTime, nullable=True),
        # Status
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("is_default", sa.Boolean, nullable=False, default=False),
    )

    op.create_index("ix_payment_methods_user_id", "payment_methods", ["user_id"])
    op.create_index("ix_payment_methods_provider", "payment_methods", ["provider"])

    # =========================================================================
    # Purchases Table
    # =========================================================================
    op.create_table(
        "purchases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "payment_method_id",
            sa.String(36),
            sa.ForeignKey("payment_methods.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        # Purchase details
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("merchant", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        # Amount
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, default="USD"),
        # Status
        sa.Column("status", sa.String(50), nullable=False, default="pending"),
        # Approval tracking
        sa.Column("approval_required", sa.Boolean, nullable=False, default=False),
        sa.Column("approved_at", sa.DateTime, nullable=True),
        sa.Column("approval_method", sa.String(50), nullable=True),
        # Execution details
        sa.Column("executed_at", sa.DateTime, nullable=True),
        sa.Column("external_transaction_id", sa.String(255), nullable=True),
        sa.Column("confirmation_number", sa.String(255), nullable=True),
        # Error tracking
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("retry_count", sa.Integer, nullable=False, default=0),
        # Purchase data (JSON)
        sa.Column("purchase_data", sa.JSON, nullable=True),
        # Original request
        sa.Column("original_request", sa.Text, nullable=True),
        # Linked conversation
        sa.Column("conversation_id", sa.String(36), nullable=True),
    )

    op.create_index("ix_purchases_user_id", "purchases", ["user_id"])
    op.create_index("ix_purchases_status", "purchases", ["status"])
    op.create_index("ix_purchases_category", "purchases", ["category"])
    op.create_index("ix_purchases_created_at", "purchases", ["created_at"])


def downgrade() -> None:
    # Drop purchases table
    op.drop_index("ix_purchases_created_at", table_name="purchases")
    op.drop_index("ix_purchases_category", table_name="purchases")
    op.drop_index("ix_purchases_status", table_name="purchases")
    op.drop_index("ix_purchases_user_id", table_name="purchases")
    op.drop_table("purchases")

    # Drop payment_methods table
    op.drop_index("ix_payment_methods_provider", table_name="payment_methods")
    op.drop_index("ix_payment_methods_user_id", table_name="payment_methods")
    op.drop_table("payment_methods")

    # Drop spending_rules table
    op.drop_index("uq_spending_rules_user_category", table_name="spending_rules")
    op.drop_index("ix_spending_rules_category", table_name="spending_rules")
    op.drop_index("ix_spending_rules_user_id", table_name="spending_rules")
    op.drop_table("spending_rules")
