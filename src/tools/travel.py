"""Travel Tool - Flight search, booking, and itinerary management."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

import httpx

from src.config import get_settings
from src.tools.base import (
    Tool, ToolAction, ToolResult, ToolCategory, ApprovalLevel, ApprovalRequired
)

settings = get_settings()


@dataclass
class FlightOption:
    """A flight search result."""
    id: str
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    stops: int
    price: Decimal
    currency: str = "USD"
    cabin_class: str = "economy"
    booking_url: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "airline": self.airline,
            "flight_number": self.flight_number,
            "route": f"{self.departure_airport} → {self.arrival_airport}",
            "departure": self.departure_time.isoformat(),
            "arrival": self.arrival_time.isoformat(),
            "duration": f"{self.duration_minutes // 60}h {self.duration_minutes % 60}m",
            "stops": "Direct" if self.stops == 0 else f"{self.stops} stop(s)",
            "price": f"${self.price:.2f}",
            "cabin": self.cabin_class,
        }

    def summary(self) -> str:
        return (
            f"{self.airline} {self.flight_number}: "
            f"{self.departure_airport}→{self.arrival_airport} "
            f"${self.price:.2f} ({'Direct' if self.stops == 0 else f'{self.stops} stops'})"
        )


class TravelTool(Tool):
    """Tool for searching and booking flights."""

    name = "travel"
    description = "Search for flights, book travel, and manage itineraries"
    category = ToolCategory.TRAVEL
    version = "1.0.0"

    requires_auth = True
    auth_type = "api_key"  # Amadeus or similar

    # Approval thresholds for travel
    cost_threshold_auto = Decimal("0")  # Never auto-approve bookings
    cost_threshold_notify = Decimal("500")

    def __init__(self):
        super().__init__()
        self.amadeus_client_id = getattr(settings, 'amadeus_client_id', '')
        self.amadeus_client_secret = getattr(settings, 'amadeus_client_secret', '')
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None

    def _register_actions(self) -> None:
        """Register travel actions."""
        self.register_action(ToolAction(
            name="search_flights",
            description="Search for available flights between two cities",
            parameters={
                "origin": {"type": "string", "description": "Origin airport code (e.g., 'SFO')", "required": True},
                "destination": {"type": "string", "description": "Destination airport code (e.g., 'NRT')", "required": True},
                "departure_date": {"type": "string", "description": "Departure date (YYYY-MM-DD)", "required": True},
                "return_date": {"type": "string", "description": "Return date for round trip (YYYY-MM-DD)"},
                "passengers": {"type": "integer", "description": "Number of passengers", "default": 1},
                "cabin_class": {"type": "string", "enum": ["economy", "premium_economy", "business", "first"]},
                "max_stops": {"type": "integer", "description": "Maximum number of stops (0 for direct only)"},
            },
            approval_level=ApprovalLevel.NONE,  # Search is free
        ))

        self.register_action(ToolAction(
            name="book_flight",
            description="Book a selected flight",
            parameters={
                "flight_id": {"type": "string", "description": "Flight offer ID from search results", "required": True},
                "passengers": {"type": "array", "items": {"type": "object"}, "description": "Passenger details"},
                "payment_method": {"type": "string", "description": "Payment method ID"},
            },
            approval_level=ApprovalLevel.CONFIRM,  # Always require approval for booking
        ))

        self.register_action(ToolAction(
            name="get_itinerary",
            description="Get details of a booked trip",
            parameters={
                "booking_reference": {"type": "string", "description": "Booking confirmation code", "required": True},
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="cancel_booking",
            description="Cancel a flight booking",
            parameters={
                "booking_reference": {"type": "string", "description": "Booking confirmation code", "required": True},
            },
            approval_level=ApprovalLevel.STRICT,  # Require extra verification
        ))

    async def _get_amadeus_token(self) -> Optional[str]:
        """Get or refresh Amadeus API token."""
        if self._access_token and self._token_expires and datetime.utcnow() < self._token_expires:
            return self._access_token

        if not self.amadeus_client_id or not self.amadeus_client_secret:
            return None

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.amadeus.com/v1/security/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.amadeus_client_id,
                    "client_secret": self.amadeus_client_secret,
                },
            )
            if response.status_code == 200:
                data = response.json()
                self._access_token = data["access_token"]
                self._token_expires = datetime.utcnow() + timedelta(seconds=data["expires_in"] - 60)
                return self._access_token
        return None

    async def execute(self, action: str, params: dict, user_id: UUID) -> ToolResult:
        """Execute a travel action."""
        if action == "search_flights":
            return await self._search_flights(params, user_id)
        elif action == "book_flight":
            return await self._book_flight(params, user_id)
        elif action == "get_itinerary":
            return await self._get_itinerary(params, user_id)
        elif action == "cancel_booking":
            return await self._cancel_booking(params, user_id)
        else:
            return ToolResult(success=False, error=f"Unknown action: {action}")

    async def _search_flights(self, params: dict, user_id: UUID) -> ToolResult:
        """Search for flights using Amadeus API."""
        # Check for API credentials
        token = await self._get_amadeus_token()

        if not token:
            # Return mock data for testing/demo
            return await self._mock_search(params)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.amadeus.com/v2/shopping/flight-offers",
                    headers={"Authorization": f"Bearer {token}"},
                    params={
                        "originLocationCode": params["origin"],
                        "destinationLocationCode": params["destination"],
                        "departureDate": params["departure_date"],
                        "returnDate": params.get("return_date"),
                        "adults": params.get("passengers", 1),
                        "travelClass": params.get("cabin_class", "ECONOMY").upper(),
                        "nonStop": params.get("max_stops") == 0,
                        "max": 10,
                    },
                )

                if response.status_code != 200:
                    return ToolResult(
                        success=False,
                        error=f"Amadeus API error: {response.status_code}",
                    )

                data = response.json()
                flights = self._parse_amadeus_response(data)

                return ToolResult(
                    success=True,
                    data=flights,
                    summary=f"Found {len(flights)} flight options",
                    options=[f.to_dict() for f in flights],
                )

        except Exception as e:
            return ToolResult(success=False, error=str(e))

    async def _mock_search(self, params: dict) -> ToolResult:
        """Return mock flight data for testing."""
        origin = params["origin"]
        dest = params["destination"]
        dep_date = datetime.strptime(params["departure_date"], "%Y-%m-%d")

        mock_flights = [
            FlightOption(
                id="FL001",
                airline="United Airlines",
                flight_number="UA837",
                departure_airport=origin,
                arrival_airport=dest,
                departure_time=dep_date.replace(hour=10, minute=30),
                arrival_time=dep_date.replace(hour=14, minute=45) + timedelta(days=1),
                duration_minutes=795,
                stops=0,
                price=Decimal("1249.00"),
                cabin_class=params.get("cabin_class", "economy"),
            ),
            FlightOption(
                id="FL002",
                airline="ANA",
                flight_number="NH7",
                departure_airport=origin,
                arrival_airport=dest,
                departure_time=dep_date.replace(hour=13, minute=0),
                arrival_time=dep_date.replace(hour=16, minute=30) + timedelta(days=1),
                duration_minutes=750,
                stops=0,
                price=Decimal("1589.00"),
                cabin_class=params.get("cabin_class", "economy"),
            ),
            FlightOption(
                id="FL003",
                airline="Delta",
                flight_number="DL275",
                departure_airport=origin,
                arrival_airport=dest,
                departure_time=dep_date.replace(hour=8, minute=15),
                arrival_time=dep_date.replace(hour=18, minute=45) + timedelta(days=1),
                duration_minutes=930,
                stops=1,
                price=Decimal("987.00"),
                cabin_class=params.get("cabin_class", "economy"),
            ),
        ]

        return ToolResult(
            success=True,
            data=[f.to_dict() for f in mock_flights],
            summary=f"Found {len(mock_flights)} flights from {origin} to {dest}",
            options=[f.to_dict() for f in mock_flights],
            metadata={"mock": True, "note": "Demo data - connect Amadeus API for real results"},
        )

    def _parse_amadeus_response(self, data: dict) -> list[FlightOption]:
        """Parse Amadeus API response into FlightOption objects."""
        flights = []
        for offer in data.get("data", []):
            segments = offer["itineraries"][0]["segments"]
            first_seg = segments[0]
            last_seg = segments[-1]

            flights.append(FlightOption(
                id=offer["id"],
                airline=first_seg["carrierCode"],
                flight_number=f"{first_seg['carrierCode']}{first_seg['number']}",
                departure_airport=first_seg["departure"]["iataCode"],
                arrival_airport=last_seg["arrival"]["iataCode"],
                departure_time=datetime.fromisoformat(first_seg["departure"]["at"]),
                arrival_time=datetime.fromisoformat(last_seg["arrival"]["at"]),
                duration_minutes=self._parse_duration(offer["itineraries"][0]["duration"]),
                stops=len(segments) - 1,
                price=Decimal(offer["price"]["total"]),
                currency=offer["price"]["currency"],
            ))
        return flights

    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to minutes."""
        # PT13H15M -> 795 minutes
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration)
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            return hours * 60 + minutes
        return 0

    async def _book_flight(self, params: dict, user_id: UUID) -> ToolResult:
        """Book a flight (requires approval)."""
        # This would integrate with Amadeus booking API
        # For now, return approval required
        return ToolResult(
            success=False,
            error="Booking requires approval",
            metadata={
                "approval_required": True,
                "flight_id": params.get("flight_id"),
            }
        )

    async def _get_itinerary(self, params: dict, user_id: UUID) -> ToolResult:
        """Get booking details."""
        # Would fetch from database or Amadeus
        return ToolResult(
            success=False,
            error="Itinerary lookup not yet implemented",
        )

    async def _cancel_booking(self, params: dict, user_id: UUID) -> ToolResult:
        """Cancel a booking (requires strict approval)."""
        return ToolResult(
            success=False,
            error="Cancellation requires strict approval",
            metadata={"approval_required": True},
        )
