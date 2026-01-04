"""Google Calendar API service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.api.oauth import get_google_credentials


@dataclass
class CalendarEvent:
    """A calendar event from Google Calendar."""
    id: str
    title: str
    start: datetime
    end: datetime
    location: Optional[str] = None
    description: Optional[str] = None
    attendees: list[str] = None
    is_all_day: bool = False
    calendar_id: str = "primary"
    html_link: Optional[str] = None

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
            "html_link": self.html_link,
        }

    def summary_text(self) -> str:
        time_str = self.start.strftime("%b %d, %I:%M %p") if not self.is_all_day else self.start.strftime("%b %d")
        return f"{self.title} - {time_str}"


class GoogleCalendarService:
    """Service for interacting with Google Calendar API."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self._service = None

    async def _get_service(self):
        """Get authenticated Google Calendar service."""
        if self._service:
            return self._service

        credentials = await get_google_credentials(self.user_id)
        if not credentials:
            raise ValueError("User has not connected Google Calendar")

        self._service = build("calendar", "v3", credentials=credentials)
        return self._service

    async def is_connected(self) -> bool:
        """Check if user has connected Google Calendar."""
        credentials = await get_google_credentials(self.user_id)
        return credentials is not None

    async def list_events(
        self,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        calendar_id: str = "primary",
        max_results: int = 10,
    ) -> list[CalendarEvent]:
        """List calendar events in a date range."""
        service = await self._get_service()
        if not end_date:
            end_date = start_date + timedelta(days=7)

        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=start_date.isoformat() + "Z",
                timeMax=end_date.isoformat() + "Z",
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            events = events_result.get("items", [])
            return [self._parse_event(e) for e in events]
        except HttpError as e:
            raise ValueError(f"Google Calendar API error: {e}")

    async def get_event(self, event_id: str, calendar_id: str = "primary") -> CalendarEvent:
        """Get a specific event by ID."""
        service = await self._get_service()
        try:
            event = service.events().get(
                calendarId=calendar_id,
                eventId=event_id,
            ).execute()
            return self._parse_event(event)
        except HttpError as e:
            raise ValueError(f"Event not found: {e}")

    async def create_event(
        self,
        title: str,
        start: datetime,
        end: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[list[str]] = None,
        calendar_id: str = "primary",
        send_notifications: bool = True,
    ) -> CalendarEvent:
        """Create a new calendar event."""
        service = await self._get_service()

        event_body = {
            "summary": title,
            "start": {"dateTime": start.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end.isoformat(), "timeZone": "UTC"},
        }

        if description:
            event_body["description"] = description
        if location:
            event_body["location"] = location
        if attendees:
            event_body["attendees"] = [{"email": email} for email in attendees]

        try:
            event = service.events().insert(
                calendarId=calendar_id,
                body=event_body,
                sendUpdates="all" if send_notifications else "none",
            ).execute()
            return self._parse_event(event)

        except HttpError as e:
            raise ValueError(f"Failed to create event: {e}")

    async def update_event(
        self,
        event_id: str,
        title: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: str = "primary",
        send_notifications: bool = True,
    ) -> CalendarEvent:
        """Update an existing calendar event."""
        service = await self._get_service()
        existing = await self.get_event(event_id, calendar_id)

        event_body = {
            "summary": title or existing.title,
            "start": {"dateTime": (start or existing.start).isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": (end or existing.end).isoformat(), "timeZone": "UTC"},
        }

        if description is not None:
            event_body["description"] = description
        elif existing.description:
            event_body["description"] = existing.description

        if location is not None:
            event_body["location"] = location
        elif existing.location:
            event_body["location"] = existing.location

        try:
            event = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event_body,
                sendUpdates="all" if send_notifications else "none",
            ).execute()
            return self._parse_event(event)
        except HttpError as e:
            raise ValueError(f"Failed to update event: {e}")

    async def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
        send_notifications: bool = True,
    ) -> bool:
        """Delete a calendar event."""
        service = await self._get_service()
        try:
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates="all" if send_notifications else "none",
            ).execute()
            return True
        except HttpError as e:
            raise ValueError(f"Failed to delete event: {e}")

    async def find_free_time(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int,
        calendar_id: str = "primary",
        working_hours_only: bool = True,
        working_hours: tuple[int, int] = (9, 18),  # 9 AM to 6 PM
    ) -> list[dict]:
        """Find free time slots in the calendar."""
        # Get all events in the range
        events = await self.list_events(
            start_date=start_date,
            end_date=end_date,
            calendar_id=calendar_id,
            max_results=100,
        )

        # Build list of busy times
        busy_times = [(e.start, e.end) for e in events]

        free_slots = []
        current = start_date

        while current < end_date and len(free_slots) < 20:
            if working_hours_only and current.weekday() >= 5:
                current = current.replace(hour=0, minute=0, second=0) + timedelta(days=1)
                continue

            if working_hours_only:
                work_start = current.replace(hour=working_hours[0], minute=0, second=0, microsecond=0)
                work_end = current.replace(hour=working_hours[1], minute=0, second=0, microsecond=0)

                if current < work_start:
                    current = work_start
                if current >= work_end:
                    current = (current + timedelta(days=1)).replace(hour=working_hours[0], minute=0, second=0, microsecond=0)
                    continue

            slot_end = current + timedelta(minutes=duration_minutes)

            is_free = True
            for busy_start, busy_end in busy_times:
                if current < busy_end and slot_end > busy_start:
                    is_free = False
                    current = busy_end
                    break

            if is_free:
                if working_hours_only:
                    work_end = current.replace(hour=working_hours[1], minute=0, second=0, microsecond=0)
                    if slot_end <= work_end:
                        free_slots.append({
                            "start": current.isoformat(),
                            "end": slot_end.isoformat(),
                            "label": current.strftime("%a %b %d, %I:%M %p"),
                        })
                else:
                    free_slots.append({
                        "start": current.isoformat(),
                        "end": slot_end.isoformat(),
                        "label": current.strftime("%a %b %d, %I:%M %p"),
                    })
                current += timedelta(minutes=30)

        return free_slots

    def _parse_event(self, event: dict) -> CalendarEvent:
        """Parse a Google Calendar event into our dataclass."""
        start_data = event.get("start", {})
        end_data = event.get("end", {})
        is_all_day = "date" in start_data

        if is_all_day:
            start = datetime.fromisoformat(start_data["date"])
            end = datetime.fromisoformat(end_data["date"])
        else:
            start_str = start_data.get("dateTime", "")
            end_str = end_data.get("dateTime", "")
            start = datetime.fromisoformat(start_str.replace("Z", "+00:00").split("+")[0])
            end = datetime.fromisoformat(end_str.replace("Z", "+00:00").split("+")[0])

        attendees = [a["email"] for a in event.get("attendees", []) if a.get("email")]

        return CalendarEvent(
            id=event.get("id", ""),
            title=event.get("summary", "Untitled"),
            start=start,
            end=end,
            location=event.get("location"),
            description=event.get("description"),
            attendees=attendees,
            is_all_day=is_all_day,
            html_link=event.get("htmlLink"),
        )
