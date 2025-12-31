"""Add fund manager due diligence fields.

Revision ID: 004
Revises: 003
Create Date: 2024-12-31
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Fund Manager DD Fields
    op.add_column("user_profiles", sa.Column("is_fund_manager", sa.Boolean(), nullable=True))

    # Fund Basics
    op.add_column("user_profiles", sa.Column("fund_name", sa.String(255), nullable=True))
    op.add_column("user_profiles", sa.Column("fund_type", sa.String(100), nullable=True))
    op.add_column("user_profiles", sa.Column("fund_stage", sa.String(100), nullable=True))
    op.add_column("user_profiles", sa.Column("fund_vintage", sa.Integer(), nullable=True))

    # Investment Thesis
    op.add_column("user_profiles", sa.Column("investment_thesis", sa.Text(), nullable=True))
    op.add_column("user_profiles", sa.Column("target_sectors", sa.JSON(), nullable=True))
    op.add_column("user_profiles", sa.Column("target_geography", sa.JSON(), nullable=True))
    op.add_column("user_profiles", sa.Column("target_stage", sa.String(100), nullable=True))

    # Economics
    op.add_column("user_profiles", sa.Column("cheque_size_min", sa.Float(), nullable=True))
    op.add_column("user_profiles", sa.Column("cheque_size_max", sa.Float(), nullable=True))
    op.add_column("user_profiles", sa.Column("target_ownership", sa.String(100), nullable=True))
    op.add_column("user_profiles", sa.Column("fund_size_target", sa.Float(), nullable=True))
    op.add_column("user_profiles", sa.Column("fund_size_current", sa.Float(), nullable=True))
    op.add_column("user_profiles", sa.Column("management_fee", sa.String(50), nullable=True))
    op.add_column("user_profiles", sa.Column("carry", sa.String(50), nullable=True))

    # Track Record
    op.add_column("user_profiles", sa.Column("num_investments", sa.Integer(), nullable=True))
    op.add_column("user_profiles", sa.Column("num_exits", sa.Integer(), nullable=True))
    op.add_column("user_profiles", sa.Column("notable_investments", sa.JSON(), nullable=True))
    op.add_column("user_profiles", sa.Column("realized_returns", sa.String(100), nullable=True))
    op.add_column("user_profiles", sa.Column("irr", sa.String(50), nullable=True))

    # Team & Operations
    op.add_column("user_profiles", sa.Column("team_size", sa.Integer(), nullable=True))
    op.add_column("user_profiles", sa.Column("team_background", sa.Text(), nullable=True))
    op.add_column("user_profiles", sa.Column("gp_commitment", sa.String(100), nullable=True))

    # LP Base & Fundraising
    op.add_column("user_profiles", sa.Column("current_lps", sa.Text(), nullable=True))
    op.add_column("user_profiles", sa.Column("fundraising_status", sa.String(100), nullable=True))
    op.add_column("user_profiles", sa.Column("target_close_date", sa.String(100), nullable=True))

    # Differentiators
    op.add_column("user_profiles", sa.Column("competitive_edge", sa.Text(), nullable=True))
    op.add_column("user_profiles", sa.Column("value_add", sa.Text(), nullable=True))


def downgrade() -> None:
    # Drop all fund manager DD columns
    columns = [
        "is_fund_manager",
        "fund_name", "fund_type", "fund_stage", "fund_vintage",
        "investment_thesis", "target_sectors", "target_geography", "target_stage",
        "cheque_size_min", "cheque_size_max", "target_ownership",
        "fund_size_target", "fund_size_current", "management_fee", "carry",
        "num_investments", "num_exits", "notable_investments", "realized_returns", "irr",
        "team_size", "team_background", "gp_commitment",
        "current_lps", "fundraising_status", "target_close_date",
        "competitive_edge", "value_add",
    ]

    for col in columns:
        op.drop_column("user_profiles", col)
