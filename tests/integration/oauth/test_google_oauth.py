"""Integration tests for Google OAuth flow."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import select

from src.db.models import UserOAuthCredential, OAuthProvider


class TestGoogleOAuthStatus:
    """Tests for OAuth status endpoint."""

    @pytest.mark.asyncio
    async def test_status_returns_not_connected(self, client, test_user):
        """Test status when user has no OAuth credentials."""
        response = await client.get(f"/oauth/google/status?user_id={test_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is False

    @pytest.mark.asyncio
    async def test_status_returns_connected(self, client, user_with_google_oauth):
        """Test status when user has valid OAuth credentials."""
        response = await client.get(f"/oauth/google/status?user_id={user_with_google_oauth.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is True
        assert data["is_valid"] is True
        assert "scopes" in data


class TestGoogleOAuthAuthorize:
    """Tests for OAuth authorize endpoint."""

    @pytest.mark.asyncio
    async def test_authorize_redirects_to_google(self, client, test_user):
        """Test that authorize redirects to Google OAuth."""
        mock_flow = MagicMock()
        mock_flow.authorization_url.return_value = (
            "https://accounts.google.com/o/oauth2/auth?...",
            test_user.id,
        )

        with patch("src.api.oauth.get_google_flow", return_value=mock_flow):
            response = await client.get(
                f"/oauth/google/authorize?user_id={test_user.id}",
                follow_redirects=False,
            )

        assert response.status_code == 307
        assert "accounts.google.com" in response.headers["location"]

    @pytest.mark.asyncio
    async def test_authorize_without_user_id_fails(self, client):
        """Test that authorize fails without user_id."""
        response = await client.get("/oauth/google/authorize")

        assert response.status_code == 422


class TestGoogleOAuthCallback:
    """Tests for OAuth callback endpoint."""

    @pytest.mark.asyncio
    async def test_callback_stores_tokens(self, client, db_session, test_user):
        """Test that callback stores tokens in database."""
        mock_credentials = MagicMock()
        mock_credentials.token = "ya29.new-access-token"
        mock_credentials.refresh_token = "1//new-refresh-token"
        mock_credentials.expiry = datetime.utcnow() + timedelta(hours=1)
        mock_credentials.scopes = ["https://www.googleapis.com/auth/calendar.readonly"]

        mock_flow = MagicMock()
        mock_flow.credentials = mock_credentials

        with patch("src.api.oauth.get_google_flow", return_value=mock_flow):
            response = await client.get(
                f"/oauth/google/callback?code=test_code&state={test_user.id}"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Verify token was stored
        result = await db_session.execute(
            select(UserOAuthCredential).where(
                UserOAuthCredential.user_id == test_user.id
            )
        )
        credential = result.scalar_one_or_none()
        assert credential is not None
        assert credential.provider == OAuthProvider.GOOGLE.value
        assert credential.is_valid is True

    @pytest.mark.asyncio
    async def test_callback_updates_existing_tokens(
        self, client, db_session, user_with_google_oauth
    ):
        """Test that callback updates existing tokens."""
        mock_credentials = MagicMock()
        mock_credentials.token = "ya29.updated-access-token"
        mock_credentials.refresh_token = "1//updated-refresh-token"
        mock_credentials.expiry = datetime.utcnow() + timedelta(hours=2)
        mock_credentials.scopes = ["https://www.googleapis.com/auth/calendar.events"]

        mock_flow = MagicMock()
        mock_flow.credentials = mock_credentials

        with patch("src.api.oauth.get_google_flow", return_value=mock_flow):
            response = await client.get(
                f"/oauth/google/callback?code=test_code&state={user_with_google_oauth.id}"
            )

        assert response.status_code == 200

        # Verify there's still only one credential
        result = await db_session.execute(
            select(UserOAuthCredential).where(
                UserOAuthCredential.user_id == user_with_google_oauth.id
            )
        )
        credentials = result.scalars().all()
        assert len(credentials) == 1

    @pytest.mark.asyncio
    async def test_callback_with_error_fails(self, client, test_user):
        """Test that callback handles OAuth errors."""
        response = await client.get(
            f"/oauth/google/callback?code=test&state={test_user.id}&error=access_denied"
        )

        assert response.status_code == 400
        data = response.json()
        assert "access_denied" in data["detail"]


class TestGoogleOAuthRevoke:
    """Tests for OAuth revoke endpoint."""

    @pytest.mark.asyncio
    async def test_revoke_deletes_credentials(self, client, db_session, user_with_google_oauth):
        """Test that revoke removes credentials from database."""
        response = await client.delete(
            f"/oauth/google/revoke?user_id={user_with_google_oauth.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Verify credentials were deleted
        result = await db_session.execute(
            select(UserOAuthCredential).where(
                UserOAuthCredential.user_id == user_with_google_oauth.id
            )
        )
        credential = result.scalar_one_or_none()
        assert credential is None

    @pytest.mark.asyncio
    async def test_revoke_nonexistent_fails(self, client, test_user):
        """Test that revoking non-existent credentials fails."""
        response = await client.delete(f"/oauth/google/revoke?user_id={test_user.id}")

        assert response.status_code == 404


class TestTokenEncryption:
    """Tests for OAuth token encryption."""

    def test_encrypt_decrypt_roundtrip(self):
        """Test that tokens can be encrypted and decrypted."""
        from src.api.oauth import encrypt_token, decrypt_token

        original = "ya29.test-access-token"
        encrypted = encrypt_token(original)
        decrypted = decrypt_token(encrypted)

        assert decrypted == original
        assert encrypted != original

    def test_decrypt_handles_unencrypted(self):
        """Test that decrypt handles already-decrypted tokens."""
        from src.api.oauth import decrypt_token

        # If no encryption key, token should pass through
        with patch("src.api.oauth.get_fernet", return_value=None):
            result = decrypt_token("plain-token")
            assert result == "plain-token"
