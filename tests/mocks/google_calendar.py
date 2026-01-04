"""Mock Google Calendar API for testing."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4


class MockGoogleCalendarAPI:
    """Mock Google Calendar API service for testing."""

    def __init__(self, events: Optional[list[dict]] = None):
        self.events = events or []
        self._created_events = []
        self._updated_events = []
        self._deleted_event_ids = []

    def build_service(self):
        """Return a mock service that behaves like the real one."""
        service = MagicMock()
        service.events.return_value = self._events_resource()
        return service

    def _events_resource(self):
        """Create mock events resource."""
        resource = MagicMock()

        # list() method
        list_mock = MagicMock()
        list_mock.execute.return_value = {"items": self.events}
        resource.list.return_value = list_mock

        # get() method
        def get_event(calendarId, eventId):
            mock = MagicMock()
            event = next((e for e in self.events if e["id"] == eventId), None)
            if event:
                mock.execute.return_value = event
            else:
                from googleapiclient.errors import HttpError
                mock.execute.side_effect = HttpError(
                    resp=MagicMock(status=404),
                    content=b"Event not found",
                )
            return mock
        resource.get.side_effect = get_event

        # insert() method
        def insert_event(calendarId, body, sendUpdates="none"):
            mock = MagicMock()
            new_event = {
                "id": f"evt_{uuid4().hex[:12]}",
                "htmlLink": f"https://calendar.google.com/event?eid={uuid4().hex[:16]}",
                **body,
            }
            self._created_events.append(new_event)
            self.events.append(new_event)
            mock.execute.return_value = new_event
            return mock
        resource.insert.side_effect = insert_event

        # update() method
        def update_event(calendarId, eventId, body, sendUpdates="none"):
            mock = MagicMock()
            updated = {"id": eventId, **body}
            self._updated_events.append(updated)
            # Update in events list
            for i, e in enumerate(self.events):
                if e["id"] == eventId:
                    self.events[i] = updated
                    break
            mock.execute.return_value = updated
            return mock
        resource.update.side_effect = update_event

        # delete() method
        def delete_event(calendarId, eventId, sendUpdates="none"):
            mock = MagicMock()
            self._deleted_event_ids.append(eventId)
            self.events = [e for e in self.events if e["id"] != eventId]
            mock.execute.return_value = None
            return mock
        resource.delete.side_effect = delete_event

        return resource

    @property
    def created_events(self) -> list[dict]:
        """Get all events created during tests."""
        return self._created_events

    @property
    def updated_events(self) -> list[dict]:
        """Get all events updated during tests."""
        return self._updated_events

    @property
    def deleted_event_ids(self) -> list[str]:
        """Get all event IDs deleted during tests."""
        return self._deleted_event_ids

    def reset(self):
        """Reset all tracked operations."""
        self._created_events.clear()
        self._updated_events.clear()
        self._deleted_event_ids.clear()


def create_mock_credentials(valid: bool = True, expired: bool = False):
    """Create mock Google OAuth credentials."""
    creds = MagicMock()
    creds.valid = valid
    creds.expired = expired
    creds.token = "ya29.mock-access-token"
    creds.refresh_token = "1//mock-refresh-token"
    creds.expiry = datetime.utcnow() + timedelta(hours=-1 if expired else 1)
    creds.scopes = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
    ]

    def mock_refresh(request):
        creds.token = "ya29.refreshed-token"
        creds.expiry = datetime.utcnow() + timedelta(hours=1)
        creds.expired = False
        creds.valid = True
    creds.refresh = mock_refresh

    return creds


def sample_events(count: int = 3) -> list[dict]:
    """Generate sample calendar events."""
    now = datetime.utcnow()
    events = []

    for i in range(count):
        start = now.replace(hour=9 + i * 2, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        events.append({
            "id": f"event{i+1}",
            "summary": f"Meeting {i+1}",
            "start": {"dateTime": start.isoformat() + "Z", "timeZone": "UTC"},
            "end": {"dateTime": end.isoformat() + "Z", "timeZone": "UTC"},
            "location": f"Room {i+1}",
            "htmlLink": f"https://calendar.google.com/event?eid=event{i+1}",
        })

    return events
