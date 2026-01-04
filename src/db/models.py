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
    TELEGRAM = "telegram"


class LeadStatus(str, Enum):
    """Lead/signup funnel status."""

    NEW = "new"                        # Just signed up via form
    AVAILABILITY_ASKED = "availability_asked"  # WhatsApp sent asking for availability
    AVAILABILITY_RECEIVED = "availability_received"  # User responded with times
    CALL_SCHEDULED = "call_scheduled"  # Call booked
    CALL_IN_PROGRESS = "call_in_progress"
    CALL_COMPLETED = "call_completed"
    CALL_FAILED = "call_failed"        # No answer, technical issue
    CALL_NO_ANSWER = "call_no_answer"  # User didn't pick up
    FOLLOWUP_SENT = "followup_sent"    # Post-call WhatsApp sent
    ENGAGED = "engaged"                # Ongoing conversation
    CONVERTED = "converted"            # Became active user


class CallStatus(str, Enum):
    """Voice call status."""

    SCHEDULED = "scheduled"
    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    CANCELLED = "cancelled"


class CallOutcome(str, Enum):
    """Outcome of a completed call."""

    INTERESTED = "interested"          # Wants to continue
    CALLBACK_REQUESTED = "callback_requested"  # Wants another call
    NOT_INTERESTED = "not_interested"
    NEEDS_TIME = "needs_time"          # Thinking about it
    WRONG_NUMBER = "wrong_number"


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
    telegram_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)

    # Demographics (from signup form)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # male, female, other, prefer_not_to_say
    age: Mapped[Optional[int]] = mapped_column(nullable=True)
    profession: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Lead/Signup tracking
    lead_status: Mapped[str] = mapped_column(String(50), default="new")  # LeadStatus enum
    lead_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # typeform, tally, website
    signed_up_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Initial form data (before full profile is built via conversation)
    areas_of_interest: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    # ["crypto", "real_estate", "private_equity", "hedge_funds", "tax_optimization", etc.]

    financial_goals: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Free text: "Build passive income", "Grow net worth", "Retire early", etc.

    asset_classes_of_interest: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    # ["equities", "fixed_income", "alternatives", "crypto", "real_estate", "private_credit"]

    how_can_franklin_help: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Free text: What they're looking for from Franklin

    # Scheduling
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "America/New_York"
    availability_windows: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: {"preferred_days": ["monday", "wednesday"], "preferred_times": ["morning", "evening"]}

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
    calls: Mapped[list["Call"]] = relationship(
        "Call", back_populates="user", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_phone", "phone"),
        Index("ix_users_whatsapp_id", "whatsapp_id"),
        Index("ix_users_telegram_id", "telegram_id"),
        Index("ix_users_lead_status", "lead_status"),
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

    # ==========================================================================
    # FUND MANAGER DUE DILIGENCE (if user is a fund manager/GP)
    # ==========================================================================
    is_fund_manager: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Fund Basics
    fund_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    fund_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # VC, PE, hedge, crypto, RE, etc.
    fund_stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # emerging, established, institutional
    fund_vintage: Mapped[Optional[int]] = mapped_column(nullable=True)  # Year fund started

    # Investment Thesis
    investment_thesis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Core thesis/strategy
    target_sectors: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # ["fintech", "AI", "healthcare"]
    target_geography: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # ["US", "Europe", "SEA"]
    target_stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # pre-seed, seed, Series A, growth

    # Economics
    cheque_size_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Min investment size
    cheque_size_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Max investment size
    target_ownership: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "10-20%"
    fund_size_target: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Target AUM
    fund_size_current: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Current AUM
    management_fee: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "2%"
    carry: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "20%"

    # Track Record
    num_investments: Mapped[Optional[int]] = mapped_column(nullable=True)  # Total investments made
    num_exits: Mapped[Optional[int]] = mapped_column(nullable=True)  # Successful exits
    notable_investments: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Portfolio companies
    realized_returns: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "3.2x MOIC"
    irr: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "28% net IRR"

    # Team & Operations
    team_size: Mapped[Optional[int]] = mapped_column(nullable=True)
    team_background: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Key team experience
    gp_commitment: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # GP skin in the game

    # LP Base & Fundraising
    current_lps: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Types of LPs (family offices, endowments, etc.)
    fundraising_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # raising, closed, evergreen
    target_close_date: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Differentiators
    competitive_edge: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # What makes them unique
    value_add: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # How they help portfolio companies

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
    msg_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)

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


class DocumentType(str, Enum):
    """Types of documents users can upload."""

    PITCH_DECK = "pitch_deck"
    FINANCIALS = "financials"
    DEAL_MEMO = "deal_memo"
    TERM_SHEET = "term_sheet"
    PORTFOLIO = "portfolio"
    TAX_DOC = "tax_doc"
    OTHER = "other"


class Document(Base):
    """User-uploaded documents for RAG."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Document metadata
    filename: Mapped[str] = mapped_column(String(500))
    doc_type: Mapped[str] = mapped_column(String(50), default="other")  # DocumentType
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Storage
    storage_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)  # S3/Supabase URL
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Processing status
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chunk_count: Mapped[int] = mapped_column(default=0)

    # Relationships
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", lazy="selectin", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_documents_user_id", "user_id"),
        Index("ix_documents_doc_type", "doc_type"),
    )


class DocumentChunk(Base):
    """Chunked and embedded document content for vector search."""

    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Chunk content
    content: Mapped[str] = mapped_column(Text)
    chunk_index: Mapped[int] = mapped_column(default=0)  # Order within document

    # Metadata for context
    page_number: Mapped[Optional[int]] = mapped_column(nullable=True)
    section_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Vector embedding (1536 for OpenAI, 1024 for Voyage)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(1536), nullable=True)

    # Relationship
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    __table_args__ = (
        Index("ix_document_chunks_document_id", "document_id"),
    )


class UserFact(Base):
    """Extracted facts from user conversations for RAG.

    These are structured pieces of information Franklin learns about a user
    during conversations, stored for quick retrieval.
    """

    __tablename__ = "user_facts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Fact content
    category: Mapped[str] = mapped_column(String(100))  # goals, preferences, holdings, concerns, etc.
    fact: Mapped[str] = mapped_column(Text)  # The actual fact
    source: Mapped[str] = mapped_column(String(50))  # conversation, document, form

    # Context
    conversation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)  # How confident we are

    # Vector embedding for semantic search
    embedding: Mapped[Optional[list]] = mapped_column(Vector(1536), nullable=True)

    __table_args__ = (
        Index("ix_user_facts_user_id", "user_id"),
        Index("ix_user_facts_category", "category"),
    )


class OAuthProvider(str, Enum):
    """Supported OAuth providers."""

    GOOGLE = "google"
    PLAID = "plaid"
    PRIVACY = "privacy"  # Privacy.com virtual cards


class PaymentMethodType(str, Enum):
    """Types of payment methods."""

    VIRTUAL_CARD = "virtual_card"  # Privacy.com, Lithic, etc.
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    BANK_ACCOUNT = "bank_account"


class PurchaseStatus(str, Enum):
    """Status of a purchase."""

    PENDING = "pending"  # Created, waiting for execution
    APPROVED = "approved"  # User approved (if needed)
    PROCESSING = "processing"  # Being executed
    COMPLETED = "completed"  # Successfully completed
    FAILED = "failed"  # Failed to complete
    CANCELLED = "cancelled"  # Cancelled by user
    REFUNDED = "refunded"  # Refunded after completion


class PurchaseCategory(str, Enum):
    """Categories for spending rules."""

    FLIGHTS = "flights"
    HOTELS = "hotels"
    TRANSPORT = "transport"
    RESTAURANTS = "restaurants"
    SUBSCRIPTIONS = "subscriptions"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    GENERAL = "general"


class UserOAuthCredential(Base):
    """Store encrypted OAuth tokens for third-party services."""

    __tablename__ = "user_oauth_credentials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Provider info
    provider: Mapped[str] = mapped_column(String(50))  # google, plaid, etc.

    # Encrypted tokens (use Fernet encryption)
    access_token_encrypted: Mapped[str] = mapped_column(Text)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Token metadata
    token_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scopes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Status
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    last_refreshed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_user_oauth_credentials_user_id", "user_id"),
        Index("ix_user_oauth_credentials_provider", "provider"),
        # Unique constraint: one credential per user per provider
        Index("uq_user_oauth_user_provider", "user_id", "provider", unique=True),
    )


class Call(Base):
    """Track voice calls with users (Vapi)."""

    __tablename__ = "calls"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Vapi integration
    vapi_call_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)

    # Scheduling
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Call status & timing
    status: Mapped[str] = mapped_column(String(50), default="scheduled")  # CallStatus enum
    initiated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Call content
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # AI-generated summary

    # Outcome
    outcome: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # CallOutcome enum
    outcome_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Profile data extracted from call
    extracted_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: {"goals": "...", "net_worth_range": "...", "interests": [...], etc.}

    # Retry tracking
    attempt_number: Mapped[int] = mapped_column(default=1)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="calls")

    __table_args__ = (
        Index("ix_calls_user_id", "user_id"),
        Index("ix_calls_status", "status"),
        Index("ix_calls_scheduled_for", "scheduled_for"),
        Index("ix_calls_vapi_call_id", "vapi_call_id"),
    )


# =============================================================================
# AUTONOMOUS PAYMENTS MODULE
# =============================================================================


class SpendingRule(Base):
    """User-defined spending rules for autonomous purchases.

    These rules determine what Franklin can auto-approve vs. what needs
    explicit user confirmation.
    """

    __tablename__ = "spending_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Category this rule applies to
    category: Mapped[str] = mapped_column(String(50))  # PurchaseCategory or "all"

    # Spending limits
    max_per_transaction: Mapped[float] = mapped_column(Float, default=500.0)
    max_daily: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_weekly: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_monthly: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Auto-approval thresholds
    auto_approve_under: Mapped[float] = mapped_column(Float, default=100.0)  # Auto-approve under this
    notify_only_under: Mapped[float] = mapped_column(Float, default=500.0)  # Just notify, don't ask

    # Category-specific preferences (JSON)
    preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # For flights: {"class": "economy", "max_stops": 1, "preferred_airlines": ["Emirates"]}
    # For hotels: {"min_stars": 4, "preferred_chains": ["Marriott"]}

    # Merchant controls
    allowed_merchants: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Whitelist
    blocked_merchants: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Blacklist

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("ix_spending_rules_user_id", "user_id"),
        Index("ix_spending_rules_category", "category"),
        Index("uq_spending_rules_user_category", "user_id", "category", unique=True),
    )


class PaymentMethod(Base):
    """User payment methods (virtual cards, linked accounts).

    Virtual cards are the recommended approach - they have spending limits
    built in as a failsafe.
    """

    __tablename__ = "payment_methods"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Method details
    method_type: Mapped[str] = mapped_column(String(50))  # PaymentMethodType
    provider: Mapped[str] = mapped_column(String(50))  # privacy, lithic, stripe, etc.
    nickname: Mapped[str] = mapped_column(String(100))  # User-friendly name

    # Card details (encrypted)
    card_number_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expiry_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cvv_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # For API-based providers (Privacy.com, Lithic)
    external_card_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Billing address (for card transactions)
    billing_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    billing_address: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Card limits (from provider)
    spending_limit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    spending_limit_period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # daily, monthly, total

    # Usage tracking
    amount_spent: Mapped[float] = mapped_column(Float, default=0.0)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        Index("ix_payment_methods_user_id", "user_id"),
        Index("ix_payment_methods_provider", "provider"),
    )


class Purchase(Base):
    """Record of purchases made by Franklin on behalf of user."""

    __tablename__ = "purchases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE")
    )
    payment_method_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("payment_methods.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Purchase details
    category: Mapped[str] = mapped_column(String(50))  # PurchaseCategory
    merchant: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)

    # Amount
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD")

    # Status tracking
    status: Mapped[str] = mapped_column(String(50), default="pending")  # PurchaseStatus

    # Approval tracking
    approval_required: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approval_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # auto, whatsapp, telegram, etc.

    # Execution details
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    external_transaction_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    confirmation_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(default=0)

    # What was purchased (category-specific data)
    purchase_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # For flights: {"airline": "Emirates", "flight_number": "EK123", "departure": "...", "arrival": "..."}
    # For hotels: {"hotel": "Marriott Dubai", "check_in": "...", "check_out": "...", "room_type": "..."}

    # User's original request that led to this purchase
    original_request: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Linked conversation message
    conversation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    __table_args__ = (
        Index("ix_purchases_user_id", "user_id"),
        Index("ix_purchases_status", "status"),
        Index("ix_purchases_category", "category"),
        Index("ix_purchases_created_at", "created_at"),
    )
