"""Calendar Tool - Google Calendar integration for scheduling."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from src.config import get_settings
from src.tools.base import Tool, ToolAction, ToolResult, ToolCategory, ApprovalLevel

settings = get_settings()


@dataclass
class CalendarEvent:
    """A calendar event."""
    id: str
    title: str
    start: datetime
    end: datetime
    location: Optional[str] = None
    description: Optional[str] = None
    attendees: list[str] = None
    is_all_day: bool = False
    calendar_id: str = "primary"

    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "location": self.location,
            "description": self.description,
            "attendees": self.attendees,
            "is_all_day": self.is_all_day,
        }

    def summary(self) -> str:
        time_str = self.start.strftime("%b %d, %I:%M %p") if not self.is_all_day else self.start.strftime("%b %d")
        return f"{self.title} - {time_str}"


class CalendarTool(Tool):
    """Tool for managing calendar and scheduling."""

    name = "calendar"
    description = "View calendar, schedule events, find free time, and manage appointments"
    category = ToolCategory.CALENDAR
    version = "1.0.0"

    requires_auth = True
    auth_type = "oauth2"  # Google OAuth

    def _register_actions(self) -> None:
        """Register calendar actions."""
        self.register_action(ToolAction(
            name="list_events",
            description="List upcoming calendar events",
            parameters={
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)", "required": True},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "calendar_id": {"type": "string", "description": "Calendar ID (default: primary)"},
                "max_results": {"type": "integer", "description": "Maximum events to return", "default": 10},
            },
            approval_level=ApprovalLevel.NONE,  # Read-only
        ))

        self.register_action(ToolAction(
            name="find_free_time",
            description="Find available time slots in the calendar",
            parameters={
                "start_date": {"type": "string", "description": "Start of search range (YYYY-MM-DD)", "required": True},
                "end_date": {"type": "string", "description": "End of search range (YYYY-MM-DD)", "required": True},
                "duration_minutes": {"type": "integer", "description": "Required duration in minutes", "required": True},
                "working_hours_only": {"type": "boolean", "description": "Only return slots during working hours", "default": True},
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="create_event",
            description="Create a new calendar event",
            parameters={
                "title": {"type": "string", "description": "Event title", "required": True},
                "start": {"type": "string", "description": "Start datetime (ISO format)", "required": True},
                "end": {"type": "string", "description": "End datetime (ISO format)", "required": True},
                "location": {"type": "string", "description": "Event location"},
                "description": {"type": "string", "description": "Event description"},
                "attendees": {"type": "array", "items": {"type": "string"}, "description": "Email addresses of attendees"},
                "send_notifications": {"type": "boolean", "description": "Send invite notifications", "default": True},
            },
            approval_level=ApprovalLevel.CONFIRM,  # Creating events needs approval
        ))

        self.register_action(ToolAction(
            name="update_event",
            description="Update an existing calendar event",
            parameters={
                "event_id": {"type": "string", "description": "Event ID to update", "required": True},
                "title": {"type": "string", "description": "New title"},
                "start": {"type": "string", "description": "New start datetime"},
                "end": {"type": "string", "description": "New end datetime"},
                "location": {"type": "string", "description": "New location"},
                "description": {"type": "string", "description": "New description"},
            },
            approval_level=ApprovalLevel.CONFIRM,
        ))

        self.register_action(ToolAction(
            name="delete_event",
            description="Delete a calendar event",
            parameters={
                "event_id": {"type": "string", "description": "Event ID to delete", "required": True},
                "notify_attendees": {"type": "boolean", "description": "Notify attendees of cancellation", "default": True},
            },
            approval_level=ApprovalLevel.CONFIRM,
        ))

    async def execute(self, action: str, params: dict, user_id: UUID) -> ToolResult:
        """Execute a calendar action."""
        actions = {
            "list_events": self._list_events,
            "find_free_time": self._find_free_time,
            "create_event": self._create_event,
            "update_event": self._update_event,
            "delete_event": self._delete_event,
        }
        handler = actions.get(action)
        if not handler:
            return ToolResult(success=False, error=f"Unknown action: {action}")
        return await handler(params, user_id)

    async def _get_calendar_service(self, user_id: UUID):
        """Get Google Calendar service for user, or None if not connected."""
        try:
            from src.services.google_calendar import GoogleCalendarService
            service = GoogleCalendarService(str(user_id))
            if await service.is_connected():
                return service
        except Exception:
            pass
        return None

    async def _list_events(self, params: dict, user_id: UUID) -> ToolResult:
        """List calendar events."""
        start_date = datetime.strptime(params["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(params["end_date"], "%Y-%m-%d") if params.get("end_date") else None
        calendar_id = params.get("calendar_id", "primary")
        max_results = params.get("max_results", 10)

        service = await self._get_calendar_service(user_id)
        if service:
            try:
                events = await service.list_events(
                    start_date=start_date,
                    end_date=end_date,
                    calendar_id=calendar_id,
                    max_results=max_results,
                )
                return ToolResult(
                    success=True,
                    data=[e.to_dict() for e in events],
                    summary=f"Found {len(events)} events",
                    options=[{"label": e.summary_text(), "value": e.id} for e in events],
                    metadata={"source": "google_calendar"},
                )
            except Exception as e:
                return ToolResult(success=False, error=f"Google Calendar error: {str(e)}")

        mock_events = [
            CalendarEvent("evt1", "Team Standup", start_date.replace(hour=9, minute=0),
                         start_date.replace(hour=9, minute=30), location="Zoom"),
            CalendarEvent("evt2", "Quarterly Review", start_date.replace(hour=14, minute=0),
                         start_date.replace(hour=15, minute=30), location="Conference Room A",
                         attendees=["boss@company.com", "team@company.com"]),
            CalendarEvent("evt3", "Flight to Tokyo",
                         (start_date + timedelta(days=7)).replace(hour=10, minute=30),
                         (start_date + timedelta(days=7)).replace(hour=14, minute=45),
                         description="UA837 SFO→NRT"),
        ]

        return ToolResult(
            success=True,
            data=[e.to_dict() for e in mock_events],
            summary=f"Found {len(mock_events)} events (connect Google Calendar for real data)",
            options=[{"label": e.summary(), "value": e.id} for e in mock_events],
            metadata={"mock": True, "connect_url": "/oauth/google/authorize"},
        )

    async def _find_free_time(self, params: dict, user_id: UUID) -> ToolResult:
        """Find free time slots."""
        start_date = datetime.strptime(params["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(params["end_date"], "%Y-%m-%d")
        duration = params["duration_minutes"]
        working_hours = params.get("working_hours_only", True)

        service = await self._get_calendar_service(user_id)
        if service:
            try:
                free_slots = await service.find_free_time(
                    start_date=start_date,
                    end_date=end_date,
                    duration_minutes=duration,
                    working_hours_only=working_hours,
                )
                return ToolResult(
                    success=True,
                    data=free_slots[:10],
                    summary=f"Found {len(free_slots)} available time slots",
                    options=free_slots[:10],
                    metadata={"source": "google_calendar"},
                )
            except Exception as e:
                return ToolResult(success=False, error=f"Google Calendar error: {str(e)}")

        free_slots = []
        current = start_date.replace(hour=9, minute=0)

        while current < end_date:
            if current.weekday() < 5:
                for hour in [10, 14, 16]:
                    slot_start = current.replace(hour=hour, minute=0)
                    slot_end = slot_start + timedelta(minutes=duration)
                    if slot_end.hour <= 18:
                        free_slots.append({
                            "start": slot_start.isoformat(),
                            "end": slot_end.isoformat(),
                            "label": slot_start.strftime("%a %b %d, %I:%M %p"),
                        })
            current += timedelta(days=1)

        return ToolResult(
            success=True,
            data=free_slots[:10],
            summary=f"Found {len(free_slots)} available time slots (connect Google Calendar for real data)",
            options=free_slots[:10],
            metadata={"mock": True, "connect_url": "/oauth/google/authorize"},
        )

    async def _create_event(self, params: dict, user_id: UUID) -> ToolResult:
        """Create a calendar event."""
        title = params["title"]
        start = datetime.fromisoformat(params["start"])
        end = datetime.fromisoformat(params["end"])
        location = params.get("location")
        description = params.get("description")
        attendees = params.get("attendees", [])
        send_notifications = params.get("send_notifications", True)

        service = await self._get_calendar_service(user_id)
        if service:
            try:
                event = await service.create_event(
                    title=title,
                    start=start,
                    end=end,
                    description=description,
                    location=location,
                    attendees=attendees,
                    send_notifications=send_notifications,
                )
                return ToolResult(
                    success=True,
                    data=event.to_dict(),
                    summary=f"Created event: {event.title}",
                    metadata={"source": "google_calendar", "html_link": event.html_link},
                )
            except Exception as e:
                return ToolResult(success=False, error=f"Google Calendar error: {str(e)}")

        event = CalendarEvent(f"new_{datetime.utcnow().timestamp()}", title, start, end,
                            location, description, attendees)
        return ToolResult(
            success=True,
            data=event.to_dict(),
            summary=f"Created event: {event.title} (mock - connect Google Calendar to save)",
            metadata={"mock": True, "connect_url": "/oauth/google/authorize"},
        )

    async def _update_event(self, params: dict, user_id: UUID) -> ToolResult:
        """Update a calendar event."""
        event_id = params["event_id"]
        title = params.get("title")
        start = datetime.fromisoformat(params["start"]) if params.get("start") else None
        end = datetime.fromisoformat(params["end"]) if params.get("end") else None
        location = params.get("location")
        description = params.get("description")

        service = await self._get_calendar_service(user_id)
        if service:
            try:
                event = await service.update_event(
                    event_id=event_id,
                    title=title,
                    start=start,
                    end=end,
                    location=location,
                    description=description,
                )
                return ToolResult(
                    success=True,
                    data=event.to_dict(),
                    summary=f"Updated event: {event.title}",
                    metadata={"source": "google_calendar"},
                )
            except Exception as e:
                return ToolResult(success=False, error=f"Google Calendar error: {str(e)}")

        return ToolResult(
            success=True,
            summary=f"Updated event {event_id} (mock - connect Google Calendar to save)",
            metadata={"mock": True, "connect_url": "/oauth/google/authorize"},
        )

    async def _delete_event(self, params: dict, user_id: UUID) -> ToolResult:
        """Delete a calendar event."""
        event_id = params["event_id"]
        notify_attendees = params.get("notify_attendees", True)

        service = await self._get_calendar_service(user_id)
        if service:
            try:
                await service.delete_event(
                    event_id=event_id,
                    send_notifications=notify_attendees,
                )
                return ToolResult(
                    success=True,
                    summary=f"Deleted event {event_id}",
                    metadata={"source": "google_calendar"},
                )
            except Exception as e:
                return ToolResult(success=False, error=f"Google Calendar error: {str(e)}")

        return ToolResult(
            success=True,
            summary=f"Deleted event {event_id} (mock - connect Google Calendar to save)",
            metadata={"mock": True, "connect_url": "/oauth/google/authorize"},
        )
