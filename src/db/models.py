"""Database models for AI Wealth Advisor."""

from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import (
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from src.db.database import Base


class ChannelType(str, Enum):
    """Communication channel types."""

    WHATSAPP = "whatsapp"
    VOICE = "voice"
    EMAIL = "email"
    WEB = "web"


class MessageRole(str, Enum):
    """Message sender role."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class RiskTolerance(str, Enum):
    """User risk tolerance levels."""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Identity
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Channel identifiers
    whatsapp_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", uselist=False, lazy="joined"
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="user", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_phone", "phone"),
        Index("ix_users_whatsapp_id", "whatsapp_id"),
    )


class UserProfile(Base):
    """User financial profile - Boardy-style profile building for sophisticated investors."""

    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Financial Snapshot
    annual_income: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    net_worth: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    liquid_assets: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    monthly_expenses: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Investor Classification
    investor_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # accredited, qualified_purchaser, institutional
    is_accredited: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Current Holdings (JSON structures)
    existing_investments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: {"public_equities": 500000, "alternatives": 200000, "crypto": 100000, "private": 300000}

    alternative_investments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: {"hedge_funds": [...], "pe_funds": [...], "venture": [...], "private_credit": [...]}

    crypto_holdings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: {"btc": 10, "eth": 50, "stables": 100000, "defi_positions": [...]}

    private_investments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: {"pre_ipo": [...], "direct_investments": [...], "spvs": [...]}

    debts: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Sophistication & Experience
    experience_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # novice, intermediate, sophisticated
    experience_areas: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # ["hedge_funds", "crypto", "venture", etc.]
    current_deal_flow: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Deals they're currently evaluating

    # Goals & Preferences
    primary_goal: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    goal_timeline: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    risk_tolerance: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    liquidity_needs: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Any upcoming liquidity events

    interests: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    # ["basis_trading", "pre_ipo", "defi_yield", "venture", "private_credit", etc.]

    # Concentration Risks
    concentration_risks: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: {"founder_stock": {"company": "...", "value": ...}, "crypto_concentration": {...}}

    # Access & Network
    fund_relationships: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Existing fund/GP relationships
    deal_flow_sources: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Where they source deals

    # Profile Completeness (0-100)
    profile_score: Mapped[int] = mapped_column(default=0)

    # Behavior Notes (Boardy-style internal observations)
    internal_notes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="profile")


class Conversation(Base):
    """Conversation session across channels."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Channel info
    channel: Mapped[str] = mapped_column(String(50))  # whatsapp, voice, email, web
    channel_session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Conversation state
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", lazy="selectin", order_by="Message.created_at"
    )

    __table_args__ = (
        Index("ix_conversations_user_id", "user_id"),
        Index("ix_conversations_channel", "channel"),
    )


class Message(Base):
    """Individual message in a conversation."""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Message content
    role: Mapped[str] = mapped_column(String(20))  # user, assistant, system
    content: Mapped[str] = mapped_column(Text)

    # Metadata
    channel: Mapped[str] = mapped_column(String(50))
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Vector embedding for semantic search
    embedding: Mapped[Optional[list]] = mapped_column(Vector(1536), nullable=True)

    # Relationship
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_id", "conversation_id"),
        Index("ix_messages_created_at", "created_at"),
    )


class PartnerService(Base):
    """Partner services, products, and advisors for matching."""

    __tablename__ = "partner_services"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(100))  # advisor, product, service, tool
    category: Mapped[str] = mapped_column(String(100))  # crypto, real_estate, tax, etc.
    description: Mapped[str] = mapped_column(Text)

    # Matching criteria
    min_net_worth: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_income: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_profiles: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # ["conservative", "moderate"]
    interests_match: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # ["crypto", "defi"]

    # Contact
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Vector embedding for semantic matching
    embedding: Mapped[Optional[list]] = mapped_column(Vector(1536), nullable=True)

    __table_args__ = (
        Index("ix_partner_services_category", "category"),
        Index("ix_partner_services_type", "type"),
    )


class Referral(Base):
    """Track referrals/introductions made (Boardy-style tracking)."""

    __tablename__ = "referrals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE")
    )
    partner_service_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("partner_services.id", ondelete="CASCADE")
    )

    # Referral details
    reason: Mapped[str] = mapped_column(Text)  # Why this match was made
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, contacted, converted, declined

    # Outcome tracking
    outcome_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_referrals_user_id", "user_id"),
        Index("ix_referrals_status", "status"),
    )
