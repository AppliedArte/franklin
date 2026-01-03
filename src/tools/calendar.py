"""Calendar Tool - Google Calendar integration for scheduling."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
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
        if action == "list_events":
            return await self._list_events(params, user_id)
        elif action == "find_free_time":
            return await self._find_free_time(params, user_id)
        elif action == "create_event":
            return await self._create_event(params, user_id)
        elif action == "update_event":
            return await self._update_event(params, user_id)
        elif action == "delete_event":
            return await self._delete_event(params, user_id)
        else:
            return ToolResult(success=False, error=f"Unknown action: {action}")

    async def _list_events(self, params: dict, user_id: UUID) -> ToolResult:
        """List calendar events."""
        # TODO: Integrate with Google Calendar API
        # For now, return mock data

        start_date = datetime.strptime(params["start_date"], "%Y-%m-%d")
        mock_events = [
            CalendarEvent(
                id="evt1",
                title="Team Standup",
                start=start_date.replace(hour=9, minute=0),
                end=start_date.replace(hour=9, minute=30),
                location="Zoom",
            ),
            CalendarEvent(
                id="evt2",
                title="Quarterly Review",
                start=start_date.replace(hour=14, minute=0),
                end=start_date.replace(hour=15, minute=30),
                location="Conference Room A",
                attendees=["boss@company.com", "team@company.com"],
            ),
            CalendarEvent(
                id="evt3",
                title="Flight to Tokyo",
                start=(start_date + timedelta(days=7)).replace(hour=10, minute=30),
                end=(start_date + timedelta(days=7)).replace(hour=14, minute=45),
                description="UA837 SFO→NRT",
            ),
        ]

        return ToolResult(
            success=True,
            data=[e.to_dict() for e in mock_events],
            summary=f"Found {len(mock_events)} events",
            options=[{"label": e.summary(), "value": e.id} for e in mock_events],
            metadata={"mock": True},
        )

    async def _find_free_time(self, params: dict, user_id: UUID) -> ToolResult:
        """Find free time slots."""
        start_date = datetime.strptime(params["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(params["end_date"], "%Y-%m-%d")
        duration = params["duration_minutes"]
        working_hours = params.get("working_hours_only", True)

        # Mock free slots
        free_slots = []
        current = start_date.replace(hour=9, minute=0)

        while current < end_date:
            if current.weekday() < 5:  # Weekdays only
                # Add a few slots per day
                for hour in [10, 14, 16]:
                    slot_start = current.replace(hour=hour, minute=0)
                    slot_end = slot_start + timedelta(minutes=duration)
                    if slot_end.hour <= 18:  # Within working hours
                        free_slots.append({
                            "start": slot_start.isoformat(),
                            "end": slot_end.isoformat(),
                            "label": slot_start.strftime("%a %b %d, %I:%M %p"),
                        })
            current += timedelta(days=1)

        return ToolResult(
            success=True,
            data=free_slots[:10],  # Limit to 10 slots
            summary=f"Found {len(free_slots)} available time slots",
            options=free_slots[:10],
            metadata={"mock": True},
        )

    async def _create_event(self, params: dict, user_id: UUID) -> ToolResult:
        """Create a calendar event."""
        # TODO: Integrate with Google Calendar API
        event = CalendarEvent(
            id=f"new_{datetime.utcnow().timestamp()}",
            title=params["title"],
            start=datetime.fromisoformat(params["start"]),
            end=datetime.fromisoformat(params["end"]),
            location=params.get("location"),
            description=params.get("description"),
            attendees=params.get("attendees", []),
        )

        return ToolResult(
            success=True,
            data=event.to_dict(),
            summary=f"Created event: {event.title}",
            metadata={"mock": True, "approval_was_given": True},
        )

    async def _update_event(self, params: dict, user_id: UUID) -> ToolResult:
        """Update a calendar event."""
        return ToolResult(
            success=True,
            summary=f"Updated event {params['event_id']}",
            metadata={"mock": True},
        )

    async def _delete_event(self, params: dict, user_id: UUID) -> ToolResult:
        """Delete a calendar event."""
        return ToolResult(
            success=True,
            summary=f"Deleted event {params['event_id']}",
            metadata={"mock": True},
        )
