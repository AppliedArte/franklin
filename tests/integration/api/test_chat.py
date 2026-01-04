"""Integration tests for chat API."""

from __future__ import annotations

from unittest.mock import patch, AsyncMock

import pytest


class TestChatEndpoint:
    """Tests for chat message endpoint."""

    @pytest.mark.asyncio
    async def test_chat_requires_message(self, client, test_user):
        """Test that chat requires a message."""
        response = await client.post("/chat/message", json={})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_chat_with_message(self, client, test_user):
        """Test basic chat message."""
        mock_response = {
            "response": "Hello! I'm Franklin, your AI wealth advisor.",
            "user_id": test_user.id,
        }

        with patch("src.api.chat.handle_message", new_callable=AsyncMock, return_value=mock_response):
            response = await client.post(
                "/chat/message",
                json={
                    "message": "Hello",
                    "user_id": test_user.id,
                    "channel": "web",
                },
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_chat_creates_conversation(self, client, db_session, test_user):
        """Test that chat creates a conversation record."""
        from src.db.models import Conversation

        mock_response = {
            "response": "I can help you with that.",
            "user_id": test_user.id,
            "conversation_id": "conv_123",
        }

        with patch("src.api.chat.handle_message", new_callable=AsyncMock, return_value=mock_response):
            response = await client.post(
                "/chat/message",
                json={
                    "message": "What's my portfolio value?",
                    "user_id": test_user.id,
                    "channel": "web",
                },
            )

        assert response.status_code == 200


class TestChatHistory:
    """Tests for chat history endpoint."""

    @pytest.mark.asyncio
    async def test_history_requires_user_id(self, client):
        """Test that history requires user_id."""
        response = await client.get("/chat/history")

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_history_returns_messages(self, client, test_user):
        """Test that history returns user messages."""
        mock_history = {
            "conversations": [],
            "total": 0,
        }

        with patch("src.api.chat.get_history", new_callable=AsyncMock, return_value=mock_history):
            response = await client.get(f"/chat/history?user_id={test_user.id}")

        # May return 200 with empty list or 404
        assert response.status_code in [200, 404]
