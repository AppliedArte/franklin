"""Travel Tool - Flight search using Kiwi Tequila API.

Kiwi's Tequila API is free for startups - just register at tequila.kiwi.com
and get an API key instantly. No approval process required.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

import httpx

from src.config import get_settings
from src.tools.base import (
    Tool, ToolAction, ToolResult, ToolCategory, ApprovalLevel
)

settings = get_settings()

# Kiwi Tequila API
TEQUILA_BASE_URL = "https://tequila-api.kiwi.com"
TEQUILA_SEARCH_URL = f"{TEQUILA_BASE_URL}/v2/search"
TEQUILA_LOCATIONS_URL = f"{TEQUILA_BASE_URL}/locations/query"


@dataclass
class FlightOption:
    """A flight search result."""
    id: str
    airline: str
    airline_name: str
    flight_numbers: str
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
    baggage_included: bool = False

    def to_dict(self) -> dict:
        hours, mins = divmod(self.duration_minutes, 60)
        return {
            "id": self.id,
            "airline": self.airline_name,
            "airline_code": self.airline,
            "flight_numbers": self.flight_numbers,
            "route": f"{self.departure_airport} → {self.arrival_airport}",
            "departure": self.departure_time.strftime("%Y-%m-%d %H:%M"),
            "arrival": self.arrival_time.strftime("%Y-%m-%d %H:%M"),
            "duration": f"{hours}h {mins}m",
            "stops": "Direct" if self.stops == 0 else f"{self.stops} stop(s)",
            "price": f"${self.price:.2f}",
            "currency": self.currency,
            "cabin": self.cabin_class,
            "booking_url": self.booking_url,
            "baggage": "Included" if self.baggage_included else "Not included",
        }

    def summary(self) -> str:
        return (
            f"{self.airline_name}: {self.departure_airport}→{self.arrival_airport} "
            f"${self.price:.2f} ({'Direct' if self.stops == 0 else f'{self.stops} stops'})"
        )


class TravelTool(Tool):
    """Tool for searching flights using Kiwi Tequila API.

    Tequila is free for startups - register at https://tequila.kiwi.com
    to get your API key instantly. No approval process.

    Features:
    - Real-time flight prices from 750+ airlines
    - Direct booking links
    - Multi-city and nomad searches
    - Virtual interlining (connecting flights from different airlines)
    """

    name = "travel"
    description = "Search for flights using Kiwi to find the best prices"
    category = ToolCategory.TRAVEL
    version = "2.0.0"

    requires_auth = True
    auth_type = "api_key"

    # Approval thresholds
    cost_threshold_auto = Decimal("0")
    cost_threshold_notify = Decimal("500")

    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'kiwi_api_key', '')

    def _register_actions(self) -> None:
        """Register travel actions."""
        self.register_action(ToolAction(
            name="search_flights",
            description="Search for available flights between two cities",
            parameters={
                "origin": {
                    "type": "string",
                    "description": "Origin airport/city code (e.g., 'SFO', 'NYC', 'LON')",
                    "required": True,
                },
                "destination": {
                    "type": "string",
                    "description": "Destination airport/city code (e.g., 'NRT', 'PAR')",
                    "required": True,
                },
                "departure_date": {
                    "type": "string",
                    "description": "Departure date (YYYY-MM-DD)",
                    "required": True,
                },
                "return_date": {
                    "type": "string",
                    "description": "Return date for round trip (YYYY-MM-DD). Omit for one-way.",
                },
                "passengers": {
                    "type": "integer",
                    "description": "Number of adult passengers",
                    "default": 1,
                },
                "cabin_class": {
                    "type": "string",
                    "enum": ["economy", "premium_economy", "business", "first"],
                    "description": "Cabin class preference",
                    "default": "economy",
                },
                "max_stops": {
                    "type": "integer",
                    "description": "Maximum stops (0 for direct only)",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return",
                    "default": 10,
                },
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="search_multicity",
            description="Search for multi-city itineraries",
            parameters={
                "legs": {
                    "type": "array",
                    "description": "List of legs: [{from, to, date}, ...]",
                    "required": True,
                },
                "passengers": {
                    "type": "integer",
                    "default": 1,
                },
            },
            approval_level=ApprovalLevel.NONE,
        ))

    async def execute(self, action: str, params: dict, user_id: UUID) -> ToolResult:
        """Execute a travel action."""
        if action == "search_flights":
            return await self._search_flights(params, user_id)
        elif action == "search_multicity":
            return await self._search_multicity(params, user_id)
        else:
            return ToolResult(success=False, error=f"Unknown action: {action}")

    async def _search_flights(self, params: dict, user_id: UUID) -> ToolResult:
        """Search for flights using Kiwi Tequila API."""
        try:
            origin = params["origin"].upper()
            destination = params["destination"].upper()
            departure_date = datetime.strptime(params["departure_date"], "%Y-%m-%d")
            return_date = (datetime.strptime(params["return_date"], "%Y-%m-%d")
                          if params.get("return_date") else None)
        except (KeyError, ValueError) as e:
            return ToolResult(success=False, error=f"Invalid parameters: {e}")

        if not self.api_key:
            return await self._mock_search(params)

        try:
            cabin_map = {"economy": "M", "premium_economy": "W", "business": "C", "first": "F"}
            dep_date_str = departure_date.strftime("%d/%m/%Y")

            query_params = {
                "fly_from": origin,
                "fly_to": destination,
                "date_from": dep_date_str,
                "date_to": dep_date_str,
                "adults": params.get("passengers", 1),
                "curr": "USD",
                "limit": params.get("max_results", 10),
                "sort": "price",
                "flight_type": "round" if return_date else "oneway",
                "selected_cabins": cabin_map.get(params.get("cabin_class", "economy"), "M"),
            }

            if return_date:
                ret_date_str = return_date.strftime("%d/%m/%Y")
                query_params.update({"return_from": ret_date_str, "return_to": ret_date_str})

            if params.get("max_stops") is not None:
                query_params["max_stopovers"] = params["max_stops"]

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    TEQUILA_SEARCH_URL,
                    headers={"apikey": self.api_key},
                    params=query_params,
                )

                if response.status_code == 401:
                    return ToolResult(
                        success=False,
                        error="Invalid Kiwi API key. Get one free at tequila.kiwi.com",
                    )

                if response.status_code != 200:
                    return ToolResult(
                        success=False,
                        error=f"Kiwi API error ({response.status_code}): {response.text}",
                    )

                flights = self._parse_kiwi_response(response.json())

                if not flights:
                    return ToolResult(
                        success=True,
                        data=[],
                        summary=f"No flights found from {origin} to {destination}",
                    )

                flight_dicts = [f.to_dict() for f in flights]
                return ToolResult(
                    success=True,
                    data=flight_dicts,
                    summary=f"Found {len(flights)} flights from {origin} to {destination}",
                    options=flight_dicts,
                    metadata={
                        "source": "kiwi",
                        "origin": origin,
                        "destination": destination,
                        "currency": "USD",
                    },
                )

        except httpx.TimeoutException:
            return ToolResult(success=False, error="Search timed out. Try again.")
        except Exception as e:
            return await self._mock_search(params)

    def _parse_kiwi_response(self, data: dict) -> list[FlightOption]:
        """Parse Kiwi API response into FlightOption objects."""
        flights = []

        for itinerary in data.get("data", []):
            try:
                route = itinerary.get("route", [])
                if not route:
                    continue

                # Collect flight numbers
                flight_nums = [f"{leg.get('airline', '')}{leg.get('flight_no', '')}"
                              for leg in route]

                # Primary airline
                airline_code = route[0].get("airline", "XX")
                airlines_list = itinerary.get("airlines", [airline_code])
                airline_name = airlines_list[0] if airlines_list else airline_code

                # Times (Unix timestamps)
                departure_time = datetime.fromtimestamp(itinerary.get("dTime", 0))
                arrival_time = datetime.fromtimestamp(itinerary.get("aTime", 0))

                # Count outbound stops only (for round trips)
                stops = sum(1 for i, leg in enumerate(route)
                           if leg.get("return") == 0 and i > 0)

                flights.append(FlightOption(
                    id=itinerary.get("id", ""),
                    airline=airline_code,
                    airline_name=airline_name,
                    flight_numbers=", ".join(flight_nums[:3]),
                    departure_airport=itinerary.get("flyFrom", ""),
                    arrival_airport=itinerary.get("flyTo", ""),
                    departure_time=departure_time,
                    arrival_time=arrival_time,
                    duration_minutes=self._parse_duration(itinerary.get("fly_duration", "0h 0m")),
                    stops=stops,
                    price=Decimal(str(itinerary.get("price", 0))),
                    booking_url=itinerary.get("deep_link", ""),
                    baggage_included=itinerary.get("baglimit", {}).get("hold_weight", 0) > 0,
                ))

            except (KeyError, ValueError, TypeError):
                continue

        return flights

    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string like '13h 45m' to minutes."""
        parts = duration_str.replace("h", " ").replace("m", " ").split()
        try:
            hours = int(parts[0]) * 60 if len(parts) >= 1 else 0
            mins = int(parts[1]) if len(parts) >= 2 else 0
            return hours + mins
        except (ValueError, IndexError):
            return 0

    async def _search_multicity(self, params: dict, user_id: UUID) -> ToolResult:
        """Search for multi-city flights."""
        # Multi-city requires different endpoint
        return ToolResult(
            success=False,
            error="Multi-city search not yet implemented. Use multiple one-way searches.",
        )

    async def _mock_search(self, params: dict) -> ToolResult:
        """Return mock flight data for testing."""
        origin = params["origin"].upper()
        dest = params["destination"].upper()
        dep_date = datetime.strptime(params["departure_date"], "%Y-%m-%d")
        cabin = params.get("cabin_class", "economy")

        # Mock flight data with varied prices, durations, and stops
        mock_data = [
            ("KIWI001", "UA", "United Airlines", "UA837", 10, 30, 14, 45, 795, 0, "1249.00", True),
            ("KIWI002", "NH", "ANA", "NH7", 13, 0, 16, 30, 750, 0, "1589.00", True),
            ("KIWI003", "DL", "Delta", "DL275, DL431", 8, 15, 18, 45, 930, 1, "987.00", False),
            ("KIWI004", "AA", "American Airlines", "AA173, AA29", 15, 45, 21, 30, 825, 1, "1105.00", True),
        ]

        mock_flights = [
            FlightOption(
                id=id, airline=code, airline_name=name, flight_numbers=flights,
                departure_airport=origin, arrival_airport=dest,
                departure_time=dep_date.replace(hour=dh, minute=dm),
                arrival_time=dep_date.replace(hour=ah, minute=am) + timedelta(days=1),
                duration_minutes=dur, stops=stops, price=Decimal(price),
                cabin_class=cabin, booking_url="https://kiwi.com/booking/...",
                baggage_included=bag
            )
            for id, code, name, flights, dh, dm, ah, am, dur, stops, price, bag in mock_data
        ]

        flight_dicts = [f.to_dict() for f in mock_flights]
        return ToolResult(
            success=True,
            data=flight_dicts,
            summary=f"Found {len(mock_flights)} flights from {origin} to {dest}",
            options=flight_dicts,
            metadata={
                "mock": True,
                "source": "demo",
                "note": "Demo data - add KIWI_API_KEY for real results. Get free key at tequila.kiwi.com",
            },
        )
