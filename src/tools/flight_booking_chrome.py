"""Flight Booking Tool - Browser automation via Claude Chrome extension.

This tool leverages Claude's Chrome extension for browser-based flight booking.
Instead of API calls, it generates structured browser workflows that Claude
can execute through the Chrome extension's automation capabilities.

Usage:
    Run Claude Code with: claude --chrome
    Then use this tool to search and book flights through actual airline websites.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from src.tools.base import (
    Tool, ToolAction, ToolResult, ToolCategory, ApprovalLevel
)


class BookingSite(str, Enum):
    """Supported flight booking websites."""
    GOOGLE_FLIGHTS = "google_flights"
    KAYAK = "kayak"
    EXPEDIA = "expedia"
    UNITED = "united"
    DELTA = "delta"
    AMERICAN = "american"
    SOUTHWEST = "southwest"
    JETBLUE = "jetblue"


@dataclass
class BrowserStep:
    """A single step in a browser automation workflow."""
    action: str  # navigate, click, type, scroll, wait, extract
    target: Optional[str] = None  # CSS selector, URL, or description
    value: Optional[str] = None  # Value to type or data to extract
    description: str = ""  # Human-readable description
    wait_for: Optional[str] = None  # Element to wait for after action

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "target": self.target,
            "value": self.value,
            "description": self.description,
            "wait_for": self.wait_for,
        }


@dataclass
class BrowserWorkflow:
    """A sequence of browser steps to accomplish a task."""
    name: str
    description: str
    steps: list[BrowserStep] = field(default_factory=list)
    requires_login: bool = False
    site: BookingSite = BookingSite.GOOGLE_FLIGHTS

    def to_prompt(self) -> str:
        """Convert workflow to natural language instructions for Claude Chrome."""
        lines = [f"## {self.name}", "", self.description, ""]

        for i, step in enumerate(self.steps, 1):
            lines.append(f"{i}. {step.description}")
            if step.action == "navigate":
                lines.append(f"   - Go to: {step.target}")
            elif step.action == "type":
                lines.append(f"   - Type '{step.value}' in {step.target}")
            elif step.action == "click":
                lines.append(f"   - Click on {step.target}")
            elif step.action == "extract":
                lines.append(f"   - Extract {step.value} from the page")
            if step.wait_for:
                lines.append(f"   - Wait for: {step.wait_for}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "site": self.site.value,
            "requires_login": self.requires_login,
            "steps": [s.to_dict() for s in self.steps],
            "prompt": self.to_prompt(),
        }


@dataclass
class FlightSearchParams:
    """Parameters for a flight search."""
    origin: str
    destination: str
    departure_date: date
    return_date: Optional[date] = None
    passengers: int = 1
    cabin_class: str = "economy"
    nonstop_only: bool = False

    def validate(self) -> Optional[str]:
        """Validate search parameters. Returns error message if invalid."""
        if len(self.origin) != 3:
            return "Origin must be a 3-letter airport code (e.g., SFO)"
        if len(self.destination) != 3:
            return "Destination must be a 3-letter airport code (e.g., JFK)"
        if self.departure_date < date.today():
            return "Departure date cannot be in the past"
        if self.return_date and self.return_date < self.departure_date:
            return "Return date must be after departure date"
        if self.passengers < 1 or self.passengers > 9:
            return "Passengers must be between 1 and 9"
        return None


class FlightBookingChromeTool(Tool):
    """Tool for booking flights via browser automation with Claude Chrome extension.

    This tool generates browser workflows that Claude can execute through
    its Chrome extension integration. It supports multiple booking sites
    and handles the full booking flow from search to purchase.

    Key Features:
    - Uses real airline/booking websites (no API dependencies)
    - Leverages your existing login sessions (rewards, payment methods)
    - Can compare prices across multiple sites
    - Handles the actual booking process with user approval

    Requires:
    - Claude Code with --chrome flag
    - Claude in Chrome extension installed
    - Chrome browser running
    """

    name = "flight_booking_chrome"
    description = "Book flights using browser automation via Claude Chrome extension"
    category = ToolCategory.TRAVEL
    version = "1.0.0"

    requires_auth = False  # Uses browser session, not API keys
    auth_type = None

    # Approval thresholds - bookings always require approval
    cost_threshold_auto = Decimal("0")
    cost_threshold_notify = Decimal("500")

    def __init__(self):
        super().__init__()
        self.default_site = BookingSite.GOOGLE_FLIGHTS

    def _register_actions(self) -> None:
        """Register flight booking actions."""

        self.register_action(ToolAction(
            name="search_flights",
            description="Search for flights using browser automation. Opens Google Flights or another booking site to find available flights.",
            parameters={
                "origin": {
                    "type": "string",
                    "description": "Origin airport code (e.g., 'SFO', 'JFK', 'LAX')",
                    "required": True,
                },
                "destination": {
                    "type": "string",
                    "description": "Destination airport code (e.g., 'NRT', 'LHR', 'CDG')",
                    "required": True,
                },
                "departure_date": {
                    "type": "string",
                    "description": "Departure date in YYYY-MM-DD format",
                    "required": True,
                },
                "return_date": {
                    "type": "string",
                    "description": "Return date for round trip (YYYY-MM-DD). Omit for one-way.",
                },
                "passengers": {
                    "type": "integer",
                    "description": "Number of passengers (1-9)",
                    "default": 1,
                },
                "cabin_class": {
                    "type": "string",
                    "enum": ["economy", "premium_economy", "business", "first"],
                    "description": "Cabin class preference",
                    "default": "economy",
                },
                "nonstop_only": {
                    "type": "boolean",
                    "description": "Only show nonstop flights",
                    "default": False,
                },
                "site": {
                    "type": "string",
                    "enum": [s.value for s in BookingSite],
                    "description": "Booking site to use",
                    "default": "google_flights",
                },
            },
            approval_level=ApprovalLevel.NONE,  # Search is read-only
        ))

        self.register_action(ToolAction(
            name="compare_prices",
            description="Compare flight prices across multiple booking sites",
            parameters={
                "origin": {
                    "type": "string",
                    "description": "Origin airport code",
                    "required": True,
                },
                "destination": {
                    "type": "string",
                    "description": "Destination airport code",
                    "required": True,
                },
                "departure_date": {
                    "type": "string",
                    "description": "Departure date (YYYY-MM-DD)",
                    "required": True,
                },
                "return_date": {
                    "type": "string",
                    "description": "Return date (YYYY-MM-DD)",
                },
                "sites": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Sites to compare (default: google_flights, kayak, expedia)",
                },
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="book_flight",
            description="Book a flight after selecting from search results. Requires explicit approval.",
            parameters={
                "booking_url": {
                    "type": "string",
                    "description": "URL to the flight booking page",
                    "required": True,
                },
                "passenger_info": {
                    "type": "object",
                    "description": "Passenger details (name, DOB, etc.)",
                    "required": True,
                },
                "payment_method": {
                    "type": "string",
                    "description": "Payment method to use (saved card name or 'manual')",
                },
            },
            approval_level=ApprovalLevel.STRICT,  # Always require approval for booking
        ))

        self.register_action(ToolAction(
            name="track_price",
            description="Set up price tracking for a flight route using Google Flights",
            parameters={
                "origin": {
                    "type": "string",
                    "description": "Origin airport code",
                    "required": True,
                },
                "destination": {
                    "type": "string",
                    "description": "Destination airport code",
                    "required": True,
                },
                "departure_date": {
                    "type": "string",
                    "description": "Departure date (YYYY-MM-DD)",
                    "required": True,
                },
                "return_date": {
                    "type": "string",
                    "description": "Return date (YYYY-MM-DD)",
                },
            },
            approval_level=ApprovalLevel.NOTIFY,
        ))

        self.register_action(ToolAction(
            name="check_airline_status",
            description="Check flight status or manage existing booking on airline website",
            parameters={
                "airline": {
                    "type": "string",
                    "description": "Airline name or code (e.g., 'United', 'UA', 'Delta')",
                    "required": True,
                },
                "confirmation_code": {
                    "type": "string",
                    "description": "Booking confirmation code",
                },
                "flight_number": {
                    "type": "string",
                    "description": "Flight number (e.g., 'UA123')",
                },
                "flight_date": {
                    "type": "string",
                    "description": "Flight date (YYYY-MM-DD)",
                },
            },
            approval_level=ApprovalLevel.NONE,
        ))

    async def execute(self, action: str, params: dict, user_id: UUID) -> ToolResult:
        """Execute a flight booking action."""
        handlers = {
            "search_flights": self._search_flights,
            "compare_prices": self._compare_prices,
            "book_flight": self._book_flight,
            "track_price": self._track_price,
            "check_airline_status": self._check_airline_status,
        }

        handler = handlers.get(action)
        if not handler:
            return ToolResult(
                success=False,
                error=f"Unknown action: {action}",
            )

        return await handler(params, user_id)

    async def _search_flights(self, params: dict, user_id: UUID) -> ToolResult:
        """Generate a browser workflow to search for flights."""
        # Parse and validate params
        try:
            search_params = FlightSearchParams(
                origin=params["origin"].upper(),
                destination=params["destination"].upper(),
                departure_date=datetime.strptime(params["departure_date"], "%Y-%m-%d").date(),
                return_date=datetime.strptime(params["return_date"], "%Y-%m-%d").date() if params.get("return_date") else None,
                passengers=params.get("passengers", 1),
                cabin_class=params.get("cabin_class", "economy"),
                nonstop_only=params.get("nonstop_only", False),
            )
        except (KeyError, ValueError) as e:
            return ToolResult(success=False, error=f"Invalid parameters: {e}")

        validation_error = search_params.validate()
        if validation_error:
            return ToolResult(success=False, error=validation_error)

        # Get the requested site
        site_name = params.get("site", "google_flights")
        try:
            site = BookingSite(site_name)
        except ValueError:
            site = BookingSite.GOOGLE_FLIGHTS

        # Generate workflow for the site
        workflow = self._build_search_workflow(search_params, site)

        return ToolResult(
            success=True,
            data=workflow.to_dict(),
            summary=f"Ready to search flights from {search_params.origin} to {search_params.destination} on {site.value}",
            metadata={
                "workflow_type": "browser_automation",
                "site": site.value,
                "instructions": workflow.to_prompt(),
                "chrome_required": True,
            },
        )

    def _build_search_workflow(self, params: FlightSearchParams, site: BookingSite) -> BrowserWorkflow:
        """Build a browser workflow for flight search on the specified site."""

        if site == BookingSite.GOOGLE_FLIGHTS:
            return self._google_flights_search_workflow(params)
        elif site == BookingSite.KAYAK:
            return self._kayak_search_workflow(params)
        elif site == BookingSite.UNITED:
            return self._airline_search_workflow(params, "united", "https://www.united.com")
        elif site == BookingSite.DELTA:
            return self._airline_search_workflow(params, "delta", "https://www.delta.com")
        elif site == BookingSite.AMERICAN:
            return self._airline_search_workflow(params, "american", "https://www.aa.com")
        elif site == BookingSite.SOUTHWEST:
            return self._airline_search_workflow(params, "southwest", "https://www.southwest.com")
        else:
            # Default to Google Flights
            return self._google_flights_search_workflow(params)

    def _google_flights_search_workflow(self, params: FlightSearchParams) -> BrowserWorkflow:
        """Build workflow for Google Flights search."""
        trip_type = "round trip" if params.return_date else "one way"

        # Build Google Flights URL with parameters
        base_url = "https://www.google.com/travel/flights"

        steps = [
            BrowserStep(
                action="navigate",
                target=base_url,
                description="Open Google Flights",
                wait_for="flight search form",
            ),
            BrowserStep(
                action="click",
                target="origin input field",
                description="Click on the origin airport field",
            ),
            BrowserStep(
                action="type",
                target="origin input",
                value=params.origin,
                description=f"Enter origin airport: {params.origin}",
                wait_for="airport suggestion dropdown",
            ),
            BrowserStep(
                action="click",
                target="first airport suggestion",
                description="Select the airport from suggestions",
            ),
            BrowserStep(
                action="click",
                target="destination input field",
                description="Click on the destination airport field",
            ),
            BrowserStep(
                action="type",
                target="destination input",
                value=params.destination,
                description=f"Enter destination airport: {params.destination}",
                wait_for="airport suggestion dropdown",
            ),
            BrowserStep(
                action="click",
                target="first airport suggestion",
                description="Select the airport from suggestions",
            ),
            BrowserStep(
                action="click",
                target="departure date field",
                description="Click on departure date",
            ),
            BrowserStep(
                action="click",
                target=f"date {params.departure_date}",
                description=f"Select departure date: {params.departure_date}",
            ),
        ]

        if params.return_date:
            steps.append(BrowserStep(
                action="click",
                target=f"date {params.return_date}",
                description=f"Select return date: {params.return_date}",
            ))
        else:
            steps.append(BrowserStep(
                action="click",
                target="trip type dropdown",
                description="Change trip type to one-way",
            ))
            steps.append(BrowserStep(
                action="click",
                target="One way option",
                description="Select one-way trip",
            ))

        if params.cabin_class != "economy":
            steps.append(BrowserStep(
                action="click",
                target="cabin class dropdown",
                description="Open cabin class selector",
            ))
            steps.append(BrowserStep(
                action="click",
                target=f"{params.cabin_class} option",
                description=f"Select {params.cabin_class} class",
            ))

        if params.passengers > 1:
            steps.append(BrowserStep(
                action="click",
                target="passengers dropdown",
                description="Open passenger count selector",
            ))
            for _ in range(params.passengers - 1):
                steps.append(BrowserStep(
                    action="click",
                    target="add adult button",
                    description="Add passenger",
                ))

        steps.append(BrowserStep(
            action="click",
            target="Search button",
            description="Click Search to find flights",
            wait_for="flight results list",
        ))

        if params.nonstop_only:
            steps.append(BrowserStep(
                action="click",
                target="Stops filter",
                description="Open stops filter",
            ))
            steps.append(BrowserStep(
                action="click",
                target="Nonstop only checkbox",
                description="Filter to nonstop flights only",
            ))

        steps.append(BrowserStep(
            action="extract",
            value="flight options with prices, times, airlines, and durations",
            description="Read and summarize available flight options",
        ))

        return BrowserWorkflow(
            name=f"Search Flights: {params.origin} → {params.destination}",
            description=f"Search for {trip_type} flights from {params.origin} to {params.destination} "
                       f"departing {params.departure_date}" +
                       (f", returning {params.return_date}" if params.return_date else ""),
            steps=steps,
            site=BookingSite.GOOGLE_FLIGHTS,
        )

    def _kayak_search_workflow(self, params: FlightSearchParams) -> BrowserWorkflow:
        """Build workflow for Kayak search."""
        # Direct URL with parameters
        date_str = params.departure_date.strftime("%Y-%m-%d")
        url = f"https://www.kayak.com/flights/{params.origin}-{params.destination}/{date_str}"
        if params.return_date:
            url += f"/{params.return_date.strftime('%Y-%m-%d')}"

        steps = [
            BrowserStep(
                action="navigate",
                target=url,
                description=f"Open Kayak with {params.origin} to {params.destination}",
                wait_for="flight results",
            ),
            BrowserStep(
                action="wait",
                value="5 seconds",
                description="Wait for all results to load",
            ),
        ]

        if params.nonstop_only:
            steps.append(BrowserStep(
                action="click",
                target="Stops filter",
                description="Filter by stops",
            ))
            steps.append(BrowserStep(
                action="click",
                target="Nonstop checkbox",
                description="Select nonstop only",
            ))

        steps.append(BrowserStep(
            action="extract",
            value="flight options with prices, times, airlines, durations, and booking links",
            description="Read and summarize available flights",
        ))

        return BrowserWorkflow(
            name=f"Kayak Search: {params.origin} → {params.destination}",
            description=f"Search Kayak for flights from {params.origin} to {params.destination}",
            steps=steps,
            site=BookingSite.KAYAK,
        )

    def _airline_search_workflow(self, params: FlightSearchParams, airline: str, base_url: str) -> BrowserWorkflow:
        """Build workflow for direct airline website search."""
        steps = [
            BrowserStep(
                action="navigate",
                target=base_url,
                description=f"Open {airline.title()} website",
                wait_for="flight search form",
            ),
            BrowserStep(
                action="type",
                target="origin field",
                value=params.origin,
                description=f"Enter origin: {params.origin}",
            ),
            BrowserStep(
                action="type",
                target="destination field",
                value=params.destination,
                description=f"Enter destination: {params.destination}",
            ),
            BrowserStep(
                action="click",
                target="departure date picker",
                description="Open date picker",
            ),
            BrowserStep(
                action="click",
                target=f"date {params.departure_date}",
                description=f"Select {params.departure_date}",
            ),
        ]

        if params.return_date:
            steps.append(BrowserStep(
                action="click",
                target=f"date {params.return_date}",
                description=f"Select return date {params.return_date}",
            ))

        steps.extend([
            BrowserStep(
                action="click",
                target="search flights button",
                description="Search for flights",
                wait_for="flight results",
            ),
            BrowserStep(
                action="extract",
                value="available flights with prices and details",
                description="Read flight options",
            ),
        ])

        return BrowserWorkflow(
            name=f"{airline.title()} Search: {params.origin} → {params.destination}",
            description=f"Search {airline.title()} for flights",
            steps=steps,
            site=BookingSite(airline) if airline in [s.value for s in BookingSite] else BookingSite.GOOGLE_FLIGHTS,
            requires_login=True,  # Airline sites often need login for best prices
        )

    async def _compare_prices(self, params: dict, user_id: UUID) -> ToolResult:
        """Generate workflows to compare prices across multiple sites."""
        sites = params.get("sites", ["google_flights", "kayak", "expedia"])

        try:
            search_params = FlightSearchParams(
                origin=params["origin"].upper(),
                destination=params["destination"].upper(),
                departure_date=datetime.strptime(params["departure_date"], "%Y-%m-%d").date(),
                return_date=datetime.strptime(params["return_date"], "%Y-%m-%d").date() if params.get("return_date") else None,
            )
        except (KeyError, ValueError) as e:
            return ToolResult(success=False, error=f"Invalid parameters: {e}")

        workflows = []
        for site_name in sites:
            try:
                site = BookingSite(site_name)
                workflow = self._build_search_workflow(search_params, site)
                workflows.append(workflow.to_dict())
            except ValueError:
                continue

        instructions = f"""## Compare Flight Prices

Search these {len(workflows)} sites for the best price on {search_params.origin} → {search_params.destination}:

"""
        for i, w in enumerate(workflows, 1):
            instructions += f"{i}. **{w['name']}**\n"

        instructions += """
After searching all sites, create a comparison table with:
- Airline & flight numbers
- Departure/arrival times
- Total price
- Number of stops
- Direct booking link

Recommend the best option based on price and convenience."""

        return ToolResult(
            success=True,
            data={"workflows": workflows},
            summary=f"Ready to compare prices across {len(workflows)} sites",
            metadata={
                "workflow_type": "multi_site_comparison",
                "instructions": instructions,
                "chrome_required": True,
            },
        )

    async def _book_flight(self, params: dict, user_id: UUID) -> ToolResult:
        """Generate workflow to book a flight. Requires strict approval."""
        booking_url = params.get("booking_url")
        passenger_info = params.get("passenger_info", {})

        if not booking_url:
            return ToolResult(
                success=False,
                error="booking_url is required to proceed with booking",
            )

        steps = [
            BrowserStep(
                action="navigate",
                target=booking_url,
                description="Navigate to flight booking page",
                wait_for="passenger details form",
            ),
            BrowserStep(
                action="type",
                target="first name field",
                value=passenger_info.get("first_name", "[ASK USER]"),
                description="Enter passenger first name",
            ),
            BrowserStep(
                action="type",
                target="last name field",
                value=passenger_info.get("last_name", "[ASK USER]"),
                description="Enter passenger last name",
            ),
            BrowserStep(
                action="type",
                target="email field",
                value=passenger_info.get("email", "[ASK USER]"),
                description="Enter contact email",
            ),
            BrowserStep(
                action="type",
                target="phone field",
                value=passenger_info.get("phone", "[ASK USER]"),
                description="Enter phone number",
            ),
        ]

        if passenger_info.get("date_of_birth"):
            steps.append(BrowserStep(
                action="type",
                target="date of birth field",
                value=passenger_info["date_of_birth"],
                description="Enter date of birth",
            ))

        steps.extend([
            BrowserStep(
                action="click",
                target="continue to payment button",
                description="Proceed to payment",
                wait_for="payment form",
            ),
            BrowserStep(
                action="wait",
                value="user_confirmation",
                description="STOP: Ask user to review and confirm payment details before proceeding",
            ),
        ])

        workflow = BrowserWorkflow(
            name="Book Flight",
            description="Complete flight booking (requires user confirmation before payment)",
            steps=steps,
            requires_login=True,
        )

        return ToolResult(
            success=True,
            data=workflow.to_dict(),
            summary="Booking workflow ready - will require confirmation before payment",
            metadata={
                "workflow_type": "booking",
                "instructions": workflow.to_prompt(),
                "chrome_required": True,
                "requires_final_confirmation": True,
            },
        )

    async def _track_price(self, params: dict, user_id: UUID) -> ToolResult:
        """Set up price tracking on Google Flights."""
        try:
            origin = params["origin"].upper()
            destination = params["destination"].upper()
            departure_date = params["departure_date"]
        except KeyError as e:
            return ToolResult(success=False, error=f"Missing required parameter: {e}")

        steps = [
            BrowserStep(
                action="navigate",
                target="https://www.google.com/travel/flights",
                description="Open Google Flights",
            ),
            BrowserStep(
                action="type",
                target="origin",
                value=origin,
                description=f"Enter origin: {origin}",
            ),
            BrowserStep(
                action="type",
                target="destination",
                value=destination,
                description=f"Enter destination: {destination}",
            ),
            BrowserStep(
                action="click",
                target="departure date",
                description="Select dates",
            ),
            BrowserStep(
                action="click",
                target=f"date {departure_date}",
                description="Select departure date",
            ),
            BrowserStep(
                action="click",
                target="Search button",
                description="Search flights",
                wait_for="results",
            ),
            BrowserStep(
                action="click",
                target="Track prices toggle/button",
                description="Enable price tracking",
            ),
            BrowserStep(
                action="extract",
                value="confirmation that price tracking is enabled",
                description="Confirm tracking is active",
            ),
        ]

        workflow = BrowserWorkflow(
            name=f"Track Prices: {origin} → {destination}",
            description="Enable Google Flights price alerts for this route",
            steps=steps,
            site=BookingSite.GOOGLE_FLIGHTS,
        )

        return ToolResult(
            success=True,
            data=workflow.to_dict(),
            summary=f"Ready to set up price tracking for {origin} → {destination}",
            metadata={
                "workflow_type": "price_tracking",
                "instructions": workflow.to_prompt(),
                "chrome_required": True,
            },
        )

    async def _check_airline_status(self, params: dict, user_id: UUID) -> ToolResult:
        """Check flight status or manage booking on airline website."""
        airline = params.get("airline", "").lower()
        confirmation_code = params.get("confirmation_code")
        flight_number = params.get("flight_number")
        flight_date = params.get("flight_date")

        # Map airline names to URLs
        airline_urls = {
            "united": "https://www.united.com",
            "ua": "https://www.united.com",
            "delta": "https://www.delta.com",
            "dl": "https://www.delta.com",
            "american": "https://www.aa.com",
            "aa": "https://www.aa.com",
            "southwest": "https://www.southwest.com",
            "wn": "https://www.southwest.com",
            "jetblue": "https://www.jetblue.com",
            "b6": "https://www.jetblue.com",
            "alaska": "https://www.alaskaair.com",
            "as": "https://www.alaskaair.com",
        }

        base_url = airline_urls.get(airline)
        if not base_url:
            return ToolResult(
                success=False,
                error=f"Unknown airline: {airline}. Supported: {', '.join(airline_urls.keys())}",
            )

        if confirmation_code:
            # Manage booking flow
            steps = [
                BrowserStep(
                    action="navigate",
                    target=f"{base_url}/manageres",
                    description=f"Open {airline.title()} manage booking page",
                ),
                BrowserStep(
                    action="type",
                    target="confirmation code field",
                    value=confirmation_code,
                    description="Enter confirmation code",
                ),
                BrowserStep(
                    action="click",
                    target="find reservation button",
                    description="Look up reservation",
                    wait_for="reservation details",
                ),
                BrowserStep(
                    action="extract",
                    value="booking details, flight times, seat assignments, and available actions",
                    description="Read reservation information",
                ),
            ]
            workflow_name = f"Manage Booking: {confirmation_code}"
        elif flight_number:
            # Flight status flow
            steps = [
                BrowserStep(
                    action="navigate",
                    target=f"{base_url}/flightstatus",
                    description=f"Open {airline.title()} flight status page",
                ),
                BrowserStep(
                    action="type",
                    target="flight number field",
                    value=flight_number,
                    description=f"Enter flight number: {flight_number}",
                ),
            ]
            if flight_date:
                steps.append(BrowserStep(
                    action="type",
                    target="date field",
                    value=flight_date,
                    description=f"Enter date: {flight_date}",
                ))
            steps.extend([
                BrowserStep(
                    action="click",
                    target="check status button",
                    description="Check flight status",
                    wait_for="status results",
                ),
                BrowserStep(
                    action="extract",
                    value="flight status, departure/arrival times, gate info, delays",
                    description="Read flight status",
                ),
            ])
            workflow_name = f"Flight Status: {flight_number}"
        else:
            return ToolResult(
                success=False,
                error="Provide either confirmation_code or flight_number",
            )

        workflow = BrowserWorkflow(
            name=workflow_name,
            description=f"Check {airline.title()} for flight information",
            steps=steps,
        )

        return ToolResult(
            success=True,
            data=workflow.to_dict(),
            summary=f"Ready to check {airline.title()} for {workflow_name}",
            metadata={
                "workflow_type": "flight_status",
                "instructions": workflow.to_prompt(),
                "chrome_required": True,
            },
        )
