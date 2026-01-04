"""OAuth endpoints for third-party service authentication."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import Fernet

from src.config import get_settings
from src.db.database import get_session
from src.db.models import UserOAuthCredential, OAuthProvider

settings = get_settings()
router = APIRouter()

# Google OAuth scopes for Calendar
GOOGLE_CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

# Google OAuth scopes for Gmail
GOOGLE_GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
]

# Combined scopes for full Google integration
GOOGLE_ALL_SCOPES = GOOGLE_CALENDAR_SCOPES + GOOGLE_GMAIL_SCOPES


def get_fernet() -> Optional[Fernet]:
    """Get Fernet instance for token encryption."""
    if not settings.oauth_encryption_key:
        return None
    return Fernet(settings.oauth_encryption_key.encode())


def encrypt_token(token: str) -> str:
    """Encrypt a token for storage."""
    fernet = get_fernet()
    return fernet.encrypt(token.encode()).decode() if fernet else token


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a stored token."""
    fernet = get_fernet()
    if not fernet:
        return encrypted_token
    try:
        return fernet.decrypt(encrypted_token.encode()).decode()
    except Exception:
        return encrypted_token


def get_google_flow(state: Optional[str] = None, scopes: Optional[list] = None) -> Flow:
    """Create Google OAuth flow with specified scopes."""
    if not settings.google_oauth_client_id or not settings.google_oauth_client_secret:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured. Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET."
        )

    client_config = {
        "web": {
            "client_id": settings.google_oauth_client_id,
            "client_secret": settings.google_oauth_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.google_oauth_redirect_uri],
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=scopes or GOOGLE_CALENDAR_SCOPES,
        state=state,
    )
    flow.redirect_uri = settings.google_oauth_redirect_uri
    return flow


@router.get("/google/authorize")
async def google_authorize(user_id: str = Query(..., description="User ID to associate with OAuth")):
    """
    Redirect user to Google OAuth consent screen for Calendar.

    The user_id is stored in the OAuth state parameter so we know
    which user to associate the tokens with after the callback.
    """
    flow = get_google_flow(state=user_id)
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return RedirectResponse(url=authorization_url)


@router.get("/google/gmail/authorize")
async def gmail_authorize(user_id: str = Query(..., description="User ID to associate with OAuth")):
    """
    Redirect user to Google OAuth consent screen for Gmail access.

    This endpoint requests Gmail scopes for email reading and management.
    """
    flow = get_google_flow(state=f"gmail:{user_id}", scopes=GOOGLE_GMAIL_SCOPES)
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return RedirectResponse(url=authorization_url)


@router.get("/google/all/authorize")
async def google_all_authorize(user_id: str = Query(..., description="User ID to associate with OAuth")):
    """
    Redirect user to Google OAuth for both Calendar and Gmail access.
    """
    flow = get_google_flow(state=f"all:{user_id}", scopes=GOOGLE_ALL_SCOPES)
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return RedirectResponse(url=authorization_url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),  # Contains user_id, optionally prefixed with scope type
    error: Optional[str] = Query(None),
):
    """
    Handle OAuth callback from Google.

    Exchange the authorization code for tokens and store them.
    State format: [scope_type:]user_id where scope_type is 'gmail', 'all', or absent for calendar.
    """
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")

    # Parse state to get scope type and user_id
    if state.startswith("gmail:"):
        scope_type = "gmail"
        user_id = state[6:]  # Remove "gmail:" prefix
        default_scopes = GOOGLE_GMAIL_SCOPES
        success_message = "Gmail connected successfully!"
    elif state.startswith("all:"):
        scope_type = "all"
        user_id = state[4:]  # Remove "all:" prefix
        default_scopes = GOOGLE_ALL_SCOPES
        success_message = "Google Calendar and Gmail connected successfully!"
    else:
        scope_type = "calendar"
        user_id = state
        default_scopes = GOOGLE_CALENDAR_SCOPES
        success_message = "Google Calendar connected successfully!"

    flow = get_google_flow(state=state, scopes=default_scopes)
    flow.fetch_token(code=code)
    credentials = flow.credentials

    async with get_session() as session:
        result = await session.execute(
            select(UserOAuthCredential).where(
                UserOAuthCredential.user_id == user_id,
                UserOAuthCredential.provider == OAuthProvider.GOOGLE.value,
            )
        )
        existing = result.scalar_one_or_none()

        # Merge scopes if user already has credentials
        new_scopes = list(credentials.scopes) if credentials.scopes else default_scopes
        if existing and existing.scopes:
            # Combine existing scopes with new ones (remove duplicates)
            combined_scopes = list(set(existing.scopes + new_scopes))
            new_scopes = combined_scopes

        if existing:
            existing.access_token_encrypted = encrypt_token(credentials.token)
            if credentials.refresh_token:
                existing.refresh_token_encrypted = encrypt_token(credentials.refresh_token)
            existing.token_expiry = credentials.expiry
            existing.scopes = new_scopes
            existing.is_valid = True
            existing.error_message = None
            existing.updated_at = datetime.utcnow()
        else:
            oauth_cred = UserOAuthCredential(
                id=str(uuid4()),
                user_id=user_id,
                provider=OAuthProvider.GOOGLE.value,
                access_token_encrypted=encrypt_token(credentials.token),
                refresh_token_encrypted=encrypt_token(credentials.refresh_token) if credentials.refresh_token else None,
                token_expiry=credentials.expiry,
                scopes=new_scopes,
                is_valid=True,
            )
            session.add(oauth_cred)

        await session.commit()

    return {"status": "success", "message": success_message}


@router.get("/google/status")
async def google_status(user_id: str = Query(...)):
    """Check if user has connected Google Calendar."""
    async with get_session() as session:
        result = await session.execute(
            select(UserOAuthCredential).where(
                UserOAuthCredential.user_id == user_id,
                UserOAuthCredential.provider == OAuthProvider.GOOGLE.value,
            )
        )
        credential = result.scalar_one_or_none()

        if not credential:
            return {"connected": False}

        return {
            "connected": True,
            "is_valid": credential.is_valid,
            "scopes": credential.scopes,
            "connected_at": credential.created_at.isoformat(),
            "expires_at": credential.token_expiry.isoformat() if credential.token_expiry else None,
        }


@router.delete("/google/revoke")
async def google_revoke(user_id: str = Query(...)):
    """Disconnect Google Calendar (revoke OAuth tokens)."""
    async with get_session() as session:
        result = await session.execute(
            select(UserOAuthCredential).where(
                UserOAuthCredential.user_id == user_id,
                UserOAuthCredential.provider == OAuthProvider.GOOGLE.value,
            )
        )
        credential = result.scalar_one_or_none()

        if not credential:
            raise HTTPException(status_code=404, detail="Google not connected")

        await session.delete(credential)
        await session.commit()

    return {"status": "success", "message": "Google Calendar disconnected"}


async def get_google_credentials(user_id: str) -> Optional[Credentials]:
    """
    Get valid Google credentials for a user.

    Automatically refreshes the token if expired.
    Returns None if user hasn't connected Google.
    """
    async with get_session() as session:
        result = await session.execute(
            select(UserOAuthCredential).where(
                UserOAuthCredential.user_id == user_id,
                UserOAuthCredential.provider == OAuthProvider.GOOGLE.value,
            )
        )
        credential = result.scalar_one_or_none()

        if not credential or not credential.is_valid:
            return None

        creds = Credentials(
            token=decrypt_token(credential.access_token_encrypted),
            refresh_token=decrypt_token(credential.refresh_token_encrypted) if credential.refresh_token_encrypted else None,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_oauth_client_id,
            client_secret=settings.google_oauth_client_secret,
            scopes=credential.scopes,
        )

        if credential.token_expiry and credential.token_expiry < datetime.utcnow() + timedelta(minutes=5):
            if not creds.refresh_token:
                credential.is_valid = False
                credential.error_message = "Token expired and no refresh token available"
                await session.commit()
                return None

            try:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                credential.access_token_encrypted = encrypt_token(creds.token)
                credential.token_expiry = creds.expiry
                credential.last_refreshed_at = datetime.utcnow()
                await session.commit()
            except Exception as e:
                credential.is_valid = False
                credential.error_message = str(e)
                await session.commit()
                return None

        return creds


async def has_gmail_scopes(user_id: str) -> bool:
    """Check if user has Gmail OAuth scopes."""
    async with get_session() as session:
        result = await session.execute(
            select(UserOAuthCredential).where(
                UserOAuthCredential.user_id == user_id,
                UserOAuthCredential.provider == OAuthProvider.GOOGLE.value,
            )
        )
        credential = result.scalar_one_or_none()

        if not credential or not credential.is_valid or not credential.scopes:
            return False

        # Check if at least readonly Gmail scope is present
        return "https://www.googleapis.com/auth/gmail.readonly" in credential.scopes
