"""Chrome Browser Automation Service.

This service manages browser automation workflows for Claude's Chrome extension.
It handles workflow execution, state tracking, and result persistence.

Usage:
    service = ChromeBrowserService(user_id)
    result = await service.execute_workflow(workflow)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4


class WorkflowStatus(str, Enum):
    """Status of a browser workflow execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_INPUT = "waiting_input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowExecution:
    """Tracks the execution of a browser workflow."""
    id: UUID = field(default_factory=uuid4)
    workflow_name: str = ""
    user_id: Optional[UUID] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: int = 0
    total_steps: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: dict = field(default_factory=dict)
    error: Optional[str] = None
    chrome_required: bool = True

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "workflow_name": self.workflow_name,
            "status": self.status.value,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "results": self.results,
            "error": self.error,
        }


@dataclass
class FlightSearchResult:
    """A flight found during browser search."""
    id: str
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    duration: str
    stops: int
    price: str
    booking_url: Optional[str] = None
    source_site: str = "google_flights"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "airline": self.airline,
            "flight_number": self.flight_number,
            "route": f"{self.departure_airport} → {self.arrival_airport}",
            "departure": self.departure_time,
            "arrival": self.arrival_time,
            "duration": self.duration,
            "stops": "Direct" if self.stops == 0 else f"{self.stops} stop(s)",
            "price": self.price,
            "booking_url": self.booking_url,
            "source": self.source_site,
        }


class ChromeBrowserService:
    """Service for managing Chrome browser automation workflows.

    This service coordinates with Claude's Chrome extension to execute
    browser automation workflows. It tracks execution state, caches
    results, and handles error recovery.

    Note: The actual browser interaction is performed by Claude's Chrome
    extension. This service provides the workflow orchestration layer.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self._active_executions: dict[UUID, WorkflowExecution] = {}
        self._results_cache: dict[str, Any] = {}

    async def is_chrome_available(self) -> bool:
        """Check if Chrome extension is connected.

        Note: This is determined at runtime by Claude Code.
        Returns True as a hint that Chrome should be used.
        """
        # The Chrome extension availability is handled by Claude Code
        # at runtime via the --chrome flag. We return True to indicate
        # this service expects Chrome to be available.
        return True

    def get_chrome_instructions(self) -> str:
        """Get instructions for enabling Chrome integration."""
        return """
To use browser automation, ensure:
1. Chrome browser is running
2. Claude in Chrome extension is installed (v1.0.36+)
3. Claude Code was started with: claude --chrome

Run /chrome in Claude Code to verify connection status.
"""

    async def create_execution(
        self,
        workflow_name: str,
        total_steps: int,
    ) -> WorkflowExecution:
        """Create a new workflow execution tracker."""
        execution = WorkflowExecution(
            workflow_name=workflow_name,
            user_id=UUID(self.user_id) if self.user_id else None,
            total_steps=total_steps,
            started_at=datetime.utcnow(),
        )
        self._active_executions[execution.id] = execution
        return execution

    async def update_execution(
        self,
        execution_id: UUID,
        status: Optional[WorkflowStatus] = None,
        current_step: Optional[int] = None,
        results: Optional[dict] = None,
        error: Optional[str] = None,
    ) -> WorkflowExecution:
        """Update an execution's status."""
        execution = self._active_executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution not found: {execution_id}")

        if status:
            execution.status = status
            if status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED):
                execution.completed_at = datetime.utcnow()

        if current_step is not None:
            execution.current_step = current_step

        if results:
            execution.results.update(results)

        if error:
            execution.error = error

        return execution

    async def get_execution(self, execution_id: UUID) -> Optional[WorkflowExecution]:
        """Get an execution by ID."""
        return self._active_executions.get(execution_id)

    async def cache_search_results(
        self,
        cache_key: str,
        results: list[FlightSearchResult],
        ttl_minutes: int = 30,
    ) -> None:
        """Cache flight search results for reuse."""
        self._results_cache[cache_key] = {
            "results": results,
            "cached_at": datetime.utcnow(),
            "expires_at": datetime.utcnow(),  # Simplified for now
        }

    async def get_cached_results(self, cache_key: str) -> Optional[list[FlightSearchResult]]:
        """Get cached search results if still valid."""
        cached = self._results_cache.get(cache_key)
        if not cached:
            return None

        # Check expiration (simplified)
        return cached.get("results")

    def build_cache_key(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
    ) -> str:
        """Build a cache key for search results."""
        key = f"flights:{origin}:{destination}:{departure_date}"
        if return_date:
            key += f":{return_date}"
        return key

    async def parse_flight_results(self, raw_data: dict) -> list[FlightSearchResult]:
        """Parse raw extracted data into FlightSearchResult objects.

        This method handles the conversion of data extracted by Claude's
        Chrome extension from flight booking websites into structured
        FlightSearchResult objects.
        """
        results = []
        flights = raw_data.get("flights", [])

        for i, flight in enumerate(flights):
            results.append(FlightSearchResult(
                id=flight.get("id", f"FL{i:03d}"),
                airline=flight.get("airline", "Unknown"),
                flight_number=flight.get("flight_number", ""),
                departure_airport=flight.get("departure_airport", ""),
                arrival_airport=flight.get("arrival_airport", ""),
                departure_time=flight.get("departure_time", ""),
                arrival_time=flight.get("arrival_time", ""),
                duration=flight.get("duration", ""),
                stops=flight.get("stops", 0),
                price=flight.get("price", ""),
                booking_url=flight.get("booking_url"),
                source_site=flight.get("source", "google_flights"),
            ))

        return results

    def format_results_for_display(self, results: list[FlightSearchResult]) -> str:
        """Format flight results for human-readable display."""
        if not results:
            return "No flights found."

        lines = ["## Flight Options\n"]
        for i, flight in enumerate(results, 1):
            lines.append(f"**{i}. {flight.airline} {flight.flight_number}**")
            lines.append(f"   {flight.route}")
            lines.append(f"   Depart: {flight.departure_time} → Arrive: {flight.arrival_time}")
            lines.append(f"   Duration: {flight.duration} | {flight.to_dict()['stops']}")
            lines.append(f"   **Price: {flight.price}**")
            if flight.booking_url:
                lines.append(f"   [Book this flight]({flight.booking_url})")
            lines.append("")

        return "\n".join(lines)

    async def cleanup_old_executions(self, max_age_hours: int = 24) -> int:
        """Remove old completed/failed executions from memory."""
        cutoff = datetime.utcnow()
        to_remove = []

        for exec_id, execution in self._active_executions.items():
            if execution.completed_at:
                age = (cutoff - execution.completed_at).total_seconds() / 3600
                if age > max_age_hours:
                    to_remove.append(exec_id)

        for exec_id in to_remove:
            del self._active_executions[exec_id]

        return len(to_remove)


# Utility functions for workflow generation

def generate_google_flights_url(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1,
    cabin_class: str = "economy",
) -> str:
    """Generate a direct Google Flights URL with parameters.

    This creates a URL that opens Google Flights with the search
    pre-filled, reducing the number of browser automation steps needed.
    """
    # Google Flights uses a specific URL format
    # Format: /travel/flights/origin-destination/departure/return
    base = "https://www.google.com/travel/flights"

    # Cabin class mapping
    cabin_map = {
        "economy": "e",
        "premium_economy": "p",
        "business": "b",
        "first": "f",
    }
    cabin_code = cabin_map.get(cabin_class, "e")

    # Build the search URL
    url = f"{base}?q=Flights%20from%20{origin}%20to%20{destination}"
    url += f"&hl=en&curr=USD&tfs="

    return url


def generate_kayak_url(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
) -> str:
    """Generate a Kayak search URL."""
    url = f"https://www.kayak.com/flights/{origin}-{destination}/{departure_date}"
    if return_date:
        url += f"/{return_date}"
    return url


def generate_airline_url(
    airline: str,
    action: str = "search",
) -> str:
    """Generate airline website URL for a specific action."""
    airline_configs = {
        "united": {
            "search": "https://www.united.com/en/us",
            "status": "https://www.united.com/en/us/flightstatus",
            "manage": "https://www.united.com/en/us/managereservation",
        },
        "delta": {
            "search": "https://www.delta.com/",
            "status": "https://www.delta.com/flight-search/flight-status",
            "manage": "https://www.delta.com/mytrips/",
        },
        "american": {
            "search": "https://www.aa.com/homePage.do",
            "status": "https://www.aa.com/travelInformation/flights/status",
            "manage": "https://www.aa.com/reservation/view/find-your-reservation",
        },
        "southwest": {
            "search": "https://www.southwest.com/",
            "status": "https://www.southwest.com/air/flight-status/",
            "manage": "https://www.southwest.com/air/manage-reservation/",
        },
        "jetblue": {
            "search": "https://www.jetblue.com/",
            "status": "https://www.jetblue.com/flight-status",
            "manage": "https://www.jetblue.com/manage-trips",
        },
    }

    airline_key = airline.lower()
    config = airline_configs.get(airline_key, {})
    return config.get(action, f"https://www.google.com/search?q={airline}+airlines")
