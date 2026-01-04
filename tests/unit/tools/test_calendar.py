"""Unit tests for Calendar tool."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

import pytest

from src.tools.calendar import CalendarTool, CalendarEvent
from src.tools.base import ToolResult


@pytest.fixture
def calendar_tool():
    """Create a CalendarTool instance."""
    return CalendarTool()


@pytest.fixture
def user_id():
    """Generate a test user ID."""
    return uuid4()


class TestCalendarEvent:
    """Tests for CalendarEvent dataclass."""

    def test_to_dict(self):
        """Test event serialization."""
        event = CalendarEvent(
            id="evt1",
            title="Team Meeting",
            start=datetime(2025, 1, 15, 10, 0),
            end=datetime(2025, 1, 15, 11, 0),
            location="Room A",
            attendees=["alice@example.com"],
        )

        result = event.to_dict()

        assert result["id"] == "evt1"
        assert result["title"] == "Team Meeting"
        assert result["location"] == "Room A"
        assert result["attendees"] == ["alice@example.com"]
        assert "2025-01-15" in result["start"]

    def test_summary_timed_event(self):
        """Test summary for timed events."""
        event = CalendarEvent(
            id="evt1",
            title="Quick Call",
            start=datetime(2025, 1, 15, 14, 30),
            end=datetime(2025, 1, 15, 15, 0),
        )

        summary = event.summary()

        assert "Quick Call" in summary
        assert "Jan 15" in summary

    def test_summary_all_day_event(self):
        """Test summary for all-day events."""
        event = CalendarEvent(
            id="evt1",
            title="Company Holiday",
            start=datetime(2025, 1, 20),
            end=datetime(2025, 1, 21),
            is_all_day=True,
        )

        summary = event.summary()

        assert "Company Holiday" in summary
        assert "Jan 20" in summary

    def test_attendees_default_empty(self):
        """Test that attendees defaults to empty list."""
        event = CalendarEvent(
            id="evt1",
            title="Solo Work",
            start=datetime.now(),
            end=datetime.now() + timedelta(hours=1),
        )

        assert event.attendees == []


class TestCalendarToolMockMode:
    """Tests for Calendar tool in mock mode (no Google OAuth)."""

    @pytest.mark.asyncio
    async def test_list_events_returns_mock_data(self, calendar_tool, user_id):
        """Test that list_events returns mock data when not connected."""
        params = {
            "start_date": "2025-01-15",
            "end_date": "2025-01-22",
        }

        with patch.object(calendar_tool, "_get_calendar_service", return_value=None):
            result = await calendar_tool.execute("list_events", params, user_id)

        assert result.success is True
        assert result.metadata.get("mock") is True
        assert len(result.data) == 3
        assert any("Standup" in e["title"] for e in result.data)

    @pytest.mark.asyncio
    async def test_find_free_time_returns_mock_slots(self, calendar_tool, user_id):
        """Test that find_free_time returns mock slots when not connected."""
        params = {
            "start_date": "2025-01-15",
            "end_date": "2025-01-17",
            "duration_minutes": 30,
        }

        with patch.object(calendar_tool, "_get_calendar_service", return_value=None):
            result = await calendar_tool.execute("find_free_time", params, user_id)

        assert result.success is True
        assert result.metadata.get("mock") is True
        assert len(result.data) > 0
        assert "start" in result.data[0]
        assert "end" in result.data[0]

    @pytest.mark.asyncio
    async def test_create_event_returns_mock_confirmation(self, calendar_tool, user_id):
        """Test that create_event works in mock mode."""
        params = {
            "title": "Test Meeting",
            "start": "2025-01-15T10:00:00",
            "end": "2025-01-15T11:00:00",
            "location": "Zoom",
        }

        with patch.object(calendar_tool, "_get_calendar_service", return_value=None):
            result = await calendar_tool.execute("create_event", params, user_id)

        assert result.success is True
        assert result.metadata.get("mock") is True
        assert result.data["title"] == "Test Meeting"
        assert "connect_url" in result.metadata

    @pytest.mark.asyncio
    async def test_unknown_action_returns_error(self, calendar_tool, user_id):
        """Test that unknown actions return an error."""
        result = await calendar_tool.execute("invalid_action", {}, user_id)

        assert result.success is False
        assert "Unknown action" in result.error


class TestCalendarToolConnectedMode:
    """Tests for Calendar tool with mocked Google Calendar service."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock Google Calendar service."""
        service = AsyncMock()
        service.is_connected = AsyncMock(return_value=True)
        return service

    @pytest.mark.asyncio
    async def test_list_events_uses_real_service(self, calendar_tool, user_id, mock_service):
        """Test that list_events calls the real service when connected."""
        mock_events = [
            MagicMock(
                to_dict=lambda: {"id": "real1", "title": "Real Event"},
                summary_text=lambda: "Real Event - Jan 15",
                id="real1",
            )
        ]
        mock_service.list_events = AsyncMock(return_value=mock_events)

        params = {"start_date": "2025-01-15"}

        with patch.object(calendar_tool, "_get_calendar_service", return_value=mock_service):
            result = await calendar_tool.execute("list_events", params, user_id)

        assert result.success is True
        assert result.metadata.get("source") == "google_calendar"
        mock_service.list_events.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_event_uses_real_service(self, calendar_tool, user_id, mock_service):
        """Test that create_event calls the real service when connected."""
        mock_event = MagicMock(
            to_dict=lambda: {"id": "new1", "title": "New Meeting"},
            title="New Meeting",
            html_link="https://calendar.google.com/...",
        )
        mock_service.create_event = AsyncMock(return_value=mock_event)

        params = {
            "title": "New Meeting",
            "start": "2025-01-15T10:00:00",
            "end": "2025-01-15T11:00:00",
        }

        with patch.object(calendar_tool, "_get_calendar_service", return_value=mock_service):
            result = await calendar_tool.execute("create_event", params, user_id)

        assert result.success is True
        assert result.metadata.get("source") == "google_calendar"
        mock_service.create_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_handles_service_error(self, calendar_tool, user_id, mock_service):
        """Test that service errors are handled gracefully."""
        mock_service.list_events = AsyncMock(side_effect=Exception("API quota exceeded"))

        params = {"start_date": "2025-01-15"}

        with patch.object(calendar_tool, "_get_calendar_service", return_value=mock_service):
            result = await calendar_tool.execute("list_events", params, user_id)

        assert result.success is False
        assert "Google Calendar error" in result.error


class TestCalendarToolActions:
    """Tests for calendar tool action registration."""

    def test_actions_registered(self, calendar_tool):
        """Test that all expected actions are registered."""
        expected_actions = [
            "list_events",
            "find_free_time",
            "create_event",
            "update_event",
            "delete_event",
        ]

        registered = [a.name for a in calendar_tool.get_actions()]
        for action in expected_actions:
            assert action in registered

    def test_write_actions_require_approval(self, calendar_tool):
        """Test that write actions require confirmation."""
        from src.tools.base import ApprovalLevel

        write_actions = ["create_event", "update_event", "delete_event"]

        for action_name in write_actions:
            action = calendar_tool.get_action(action_name)
            assert action.approval_level == ApprovalLevel.CONFIRM

    def test_read_actions_no_approval(self, calendar_tool):
        """Test that read actions don't require approval."""
        from src.tools.base import ApprovalLevel

        read_actions = ["list_events", "find_free_time"]

        for action_name in read_actions:
            action = calendar_tool.get_action(action_name)
            assert action.approval_level == ApprovalLevel.NONE
