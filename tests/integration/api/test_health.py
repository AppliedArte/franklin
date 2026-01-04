"""Integration tests for health and root endpoints."""

from __future__ import annotations

import pytest


class TestRootEndpoint:
    """Tests for root endpoint."""

    @pytest.mark.asyncio
    async def test_root_returns_status(self, client):
        """Test that root returns app status."""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["status"] == "running"


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_readiness_check(self, client):
        """Test readiness endpoint."""
        response = await client.get("/ready")

        assert response.status_code == 200
