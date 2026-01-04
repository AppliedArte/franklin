"""Shared pytest fixtures for Franklin tests."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from cryptography.fernet import Fernet
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment before importing app
os.environ["APP_ENV"] = "development"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["OAUTH_ENCRYPTION_KEY"] = Fernet.generate_key().decode()
os.environ["GOOGLE_OAUTH_CLIENT_ID"] = "test-client-id"
os.environ["GOOGLE_OAUTH_CLIENT_SECRET"] = "test-client-secret"

from src.db.database import Base
from src.db.models import User, UserProfile, UserOAuthCredential, OAuthProvider
from src.main import app


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create test database engine (in-memory SQLite)."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Enable foreign keys for SQLite
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_db_session(db_session):
    """Override the app's database dependency."""
    from src.db.database import get_db

    async def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()


# =============================================================================
# HTTP Client Fixtures
# =============================================================================

@pytest.fixture
async def client(override_db_session) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for API tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# =============================================================================
# User Fixtures
# =============================================================================

@pytest.fixture
def user_id() -> str:
    """Generate a random user ID."""
    return str(uuid4())


@pytest.fixture
async def test_user(db_session: AsyncSession, user_id: str) -> User:
    """Create a test user in the database."""
    user = User(
        id=user_id,
        name="Test User",
        email="test@example.com",
        phone="+15551234567",
        lead_status="new",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user_with_profile(db_session: AsyncSession, test_user: User) -> User:
    """Create a test user with financial profile."""
    profile = UserProfile(
        id=str(uuid4()),
        user_id=test_user.id,
        net_worth=1000000,
        annual_income=250000,
        risk_tolerance="moderate",
        primary_goal="wealth preservation",
        profile_score=75,
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(test_user)
    return test_user


# =============================================================================
# OAuth Fixtures
# =============================================================================

@pytest.fixture
def google_oauth_tokens() -> dict:
    """Sample Google OAuth tokens."""
    return {
        "access_token": "ya29.test-access-token",
        "refresh_token": "1//test-refresh-token",
        "token_expiry": datetime.utcnow() + timedelta(hours=1),
        "scopes": [
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events",
        ],
    }


@pytest.fixture
async def user_with_google_oauth(
    db_session: AsyncSession, test_user: User, google_oauth_tokens: dict
) -> User:
    """Create a test user with Google OAuth credentials."""
    from src.api.oauth import encrypt_token

    credential = UserOAuthCredential(
        id=str(uuid4()),
        user_id=test_user.id,
        provider=OAuthProvider.GOOGLE.value,
        access_token_encrypted=encrypt_token(google_oauth_tokens["access_token"]),
        refresh_token_encrypted=encrypt_token(google_oauth_tokens["refresh_token"]),
        token_expiry=google_oauth_tokens["token_expiry"],
        scopes=google_oauth_tokens["scopes"],
        is_valid=True,
    )
    db_session.add(credential)
    await db_session.commit()
    return test_user


@pytest.fixture
async def expired_google_oauth(
    db_session: AsyncSession, test_user: User, google_oauth_tokens: dict
) -> User:
    """Create a test user with expired Google OAuth credentials."""
    from src.api.oauth import encrypt_token

    credential = UserOAuthCredential(
        id=str(uuid4()),
        user_id=test_user.id,
        provider=OAuthProvider.GOOGLE.value,
        access_token_encrypted=encrypt_token(google_oauth_tokens["access_token"]),
        refresh_token_encrypted=encrypt_token(google_oauth_tokens["refresh_token"]),
        token_expiry=datetime.utcnow() - timedelta(hours=1),  # Expired
        scopes=google_oauth_tokens["scopes"],
        is_valid=True,
    )
    db_session.add(credential)
    await db_session.commit()
    return test_user


# =============================================================================
# Calendar Fixtures
# =============================================================================

@pytest.fixture
def sample_calendar_events() -> list[dict]:
    """Sample calendar events for mocking."""
    now = datetime.utcnow()
    return [
        {
            "id": "event1",
            "summary": "Team Standup",
            "start": {"dateTime": now.replace(hour=9).isoformat() + "Z"},
            "end": {"dateTime": now.replace(hour=9, minute=30).isoformat() + "Z"},
            "location": "Zoom",
        },
        {
            "id": "event2",
            "summary": "Quarterly Review",
            "start": {"dateTime": now.replace(hour=14).isoformat() + "Z"},
            "end": {"dateTime": now.replace(hour=15, minute=30).isoformat() + "Z"},
            "location": "Conference Room A",
            "attendees": [{"email": "boss@example.com"}],
        },
    ]


# =============================================================================
# LLM Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_llm_response() -> dict:
    """Default mock LLM response."""
    return {
        "content": "I understand you want to schedule a meeting. Let me check your calendar.",
        "tool_calls": [],
    }


@pytest.fixture
def mock_intent_response() -> dict:
    """Mock intent parsing response."""
    return {
        "needs_action": True,
        "category": "calendar",
        "action": "list upcoming events",
        "confidence": 0.95,
    }
