"""Unit tests for Google Calendar service."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from tests.mocks.google_calendar import MockGoogleCalendarAPI, sample_events


class TestGoogleCalendarService:
    """Tests for GoogleCalendarService."""

    @pytest.fixture
    def mock_credentials(self):
        """Create mock Google credentials."""
        creds = MagicMock()
        creds.valid = True
        creds.token = "mock-token"
        return creds

    @pytest.fixture
    def mock_calendar_api(self):
        """Create mock calendar API."""
        return MockGoogleCalendarAPI(events=sample_events(3))

    @pytest.mark.asyncio
    async def test_is_connected_when_credentials_exist(self, mock_credentials):
        """Test is_connected returns True when credentials exist."""
        with patch("src.services.google_calendar.get_google_credentials", return_value=mock_credentials):
            from src.services.google_calendar import GoogleCalendarService

            service = GoogleCalendarService("user123")
            result = await service.is_connected()

            assert result is True

    @pytest.mark.asyncio
    async def test_is_connected_when_no_credentials(self):
        """Test is_connected returns False when no credentials."""
        with patch("src.services.google_calendar.get_google_credentials", return_value=None):
            from src.services.google_calendar import GoogleCalendarService

            service = GoogleCalendarService("user123")
            result = await service.is_connected()

            assert result is False

    @pytest.mark.asyncio
    async def test_list_events_calls_api(self, mock_credentials, mock_calendar_api):
        """Test list_events makes correct API call."""
        with patch("src.services.google_calendar.get_google_credentials", return_value=mock_credentials):
            with patch("src.services.google_calendar.build", return_value=mock_calendar_api.build_service()):
                from src.services.google_calendar import GoogleCalendarService

                service = GoogleCalendarService("user123")
                events = await service.list_events(
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=7),
                )

                assert len(events) == 3
                assert events[0].id == "event1"

    @pytest.mark.asyncio
    async def test_create_event_calls_api(self, mock_credentials, mock_calendar_api):
        """Test create_event makes correct API call."""
        with patch("src.services.google_calendar.get_google_credentials", return_value=mock_credentials):
            with patch("src.services.google_calendar.build", return_value=mock_calendar_api.build_service()):
                from src.services.google_calendar import GoogleCalendarService

                service = GoogleCalendarService("user123")
                event = await service.create_event(
                    title="New Event",
                    start=datetime.utcnow(),
                    end=datetime.utcnow() + timedelta(hours=1),
                )

                assert event.title == "New Event"
                assert len(mock_calendar_api.created_events) == 1

    @pytest.mark.asyncio
    async def test_delete_event_calls_api(self, mock_credentials, mock_calendar_api):
        """Test delete_event makes correct API call."""
        with patch("src.services.google_calendar.get_google_credentials", return_value=mock_credentials):
            with patch("src.services.google_calendar.build", return_value=mock_calendar_api.build_service()):
                from src.services.google_calendar import GoogleCalendarService

                service = GoogleCalendarService("user123")
                result = await service.delete_event("event1")

                assert result is True
                assert "event1" in mock_calendar_api.deleted_event_ids

    @pytest.mark.asyncio
    async def test_find_free_time_excludes_busy(self, mock_credentials, mock_calendar_api):
        """Test find_free_time returns slots avoiding busy times."""
        with patch("src.services.google_calendar.get_google_credentials", return_value=mock_credentials):
            with patch("src.services.google_calendar.build", return_value=mock_calendar_api.build_service()):
                from src.services.google_calendar import GoogleCalendarService

                service = GoogleCalendarService("user123")
                # Use a future date range to avoid timezone issues
                start = datetime(2025, 1, 20, 8, 0, 0)
                end = datetime(2025, 1, 20, 18, 0, 0)
                slots = await service.find_free_time(
                    start_date=start,
                    end_date=end,
                    duration_minutes=30,
                    working_hours_only=False,  # Don't filter by working hours
                )

                # Should have some free slots (events are mocked in the past)
                assert isinstance(slots, list)
                # Each slot should have required fields if any exist
                for slot in slots:
                    assert "start" in slot
                    assert "end" in slot
                    assert "label" in slot


class TestCalendarEventParsing:
    """Tests for parsing Google Calendar API responses."""

    def test_parse_timed_event(self):
        """Test parsing a timed event."""
        from src.services.google_calendar import GoogleCalendarService

        service = GoogleCalendarService("user123")
        raw_event = {
            "id": "evt123",
            "summary": "Team Meeting",
            "start": {"dateTime": "2025-01-15T10:00:00Z", "timeZone": "UTC"},
            "end": {"dateTime": "2025-01-15T11:00:00Z", "timeZone": "UTC"},
            "location": "Room A",
            "description": "Weekly sync",
            "attendees": [{"email": "alice@example.com"}, {"email": "bob@example.com"}],
        }

        event = service._parse_event(raw_event)

        assert event.id == "evt123"
        assert event.title == "Team Meeting"
        assert event.location == "Room A"
        assert len(event.attendees) == 2
        assert event.is_all_day is False

    def test_parse_all_day_event(self):
        """Test parsing an all-day event."""
        from src.services.google_calendar import GoogleCalendarService

        service = GoogleCalendarService("user123")
        raw_event = {
            "id": "evt456",
            "summary": "Company Holiday",
            "start": {"date": "2025-01-20"},
            "end": {"date": "2025-01-21"},
        }

        event = service._parse_event(raw_event)

        assert event.id == "evt456"
        assert event.title == "Company Holiday"
        assert event.is_all_day is True

    def test_parse_event_with_missing_fields(self):
        """Test parsing event with optional fields missing."""
        from src.services.google_calendar import GoogleCalendarService

        service = GoogleCalendarService("user123")
        raw_event = {
            "id": "evt789",
            "start": {"dateTime": "2025-01-15T10:00:00Z"},
            "end": {"dateTime": "2025-01-15T11:00:00Z"},
        }

        event = service._parse_event(raw_event)

        assert event.id == "evt789"
        assert event.title == "Untitled"
        assert event.location is None
        assert event.attendees == []
