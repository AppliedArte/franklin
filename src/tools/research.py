"""Research Tool - Web search, data lookup, and information gathering."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

import httpx

from src.config import get_settings
from src.tools.base import Tool, ToolAction, ToolResult, ToolCategory, ApprovalLevel

settings = get_settings()


class ResearchTool(Tool):
    """Tool for researching information - web search, price lookups, etc."""

    name = "research"
    description = "Search the web, look up prices, find information"
    category = ToolCategory.RESEARCH
    version = "1.0.0"

    requires_auth = False  # Most research is free

    def _register_actions(self) -> None:
        """Register research actions."""
        self.register_action(ToolAction(
            name="web_search",
            description="Search the web for information",
            parameters={
                "query": {"type": "string", "description": "Search query", "required": True},
                "num_results": {"type": "integer", "default": 5},
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="price_lookup",
            description="Look up current prices for flights, hotels, products",
            parameters={
                "item_type": {"type": "string", "enum": ["flight", "hotel", "product", "stock"], "required": True},
                "query": {"type": "string", "description": "What to look up", "required": True},
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="weather",
            description="Get weather forecast for a location",
            parameters={
                "location": {"type": "string", "required": True},
                "days": {"type": "integer", "default": 3},
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="stock_quote",
            description="Get current stock price and info",
            parameters={
                "symbol": {"type": "string", "description": "Stock ticker symbol", "required": True},
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="currency_convert",
            description="Convert between currencies",
            parameters={
                "amount": {"type": "number", "required": True},
                "from_currency": {"type": "string", "required": True},
                "to_currency": {"type": "string", "required": True},
            },
            approval_level=ApprovalLevel.NONE,
        ))

    async def execute(self, action: str, params: dict, user_id: UUID) -> ToolResult:
        """Execute a research action."""
        if action == "web_search":
            return await self._web_search(params, user_id)
        elif action == "price_lookup":
            return await self._price_lookup(params, user_id)
        elif action == "weather":
            return await self._weather(params, user_id)
        elif action == "stock_quote":
            return await self._stock_quote(params, user_id)
        elif action == "currency_convert":
            return await self._currency_convert(params, user_id)
        else:
            return ToolResult(success=False, error=f"Unknown action: {action}")

    async def _web_search(self, params: dict, user_id: UUID) -> ToolResult:
        """Search the web."""
        # TODO: Integrate with search API (Serper, Brave, etc.)
        query = params["query"]
        mock_results = [
            {
                "title": f"Result 1 for: {query}",
                "url": "https://example.com/1",
                "snippet": f"This is a relevant result about {query}...",
            },
            {
                "title": f"Result 2 for: {query}",
                "url": "https://example.com/2",
                "snippet": f"Another helpful article about {query}...",
            },
        ]

        return ToolResult(
            success=True,
            data=mock_results,
            summary=f"Found {len(mock_results)} results for '{query}'",
            metadata={"mock": True},
        )

    async def _price_lookup(self, params: dict, user_id: UUID) -> ToolResult:
        """Look up prices."""
        item_type = params["item_type"]
        query = params["query"]

        if item_type == "flight":
            return ToolResult(
                success=True,
                data={"tip": "Use the travel tool for detailed flight searches"},
                summary=f"For flight prices, use: travel__search_flights",
            )
        elif item_type == "stock":
            return await self._stock_quote({"symbol": query}, user_id)
        else:
            return ToolResult(
                success=True,
                data={"query": query, "type": item_type, "note": "Price lookup not yet implemented for this type"},
                summary=f"Price lookup for {item_type}: {query}",
                metadata={"mock": True},
            )

    async def _weather(self, params: dict, user_id: UUID) -> ToolResult:
        """Get weather forecast."""
        location = params["location"]
        days = params.get("days", 3)

        # Mock weather data
        forecast = [
            {"day": "Today", "high": 72, "low": 58, "condition": "Sunny"},
            {"day": "Tomorrow", "high": 68, "low": 55, "condition": "Partly Cloudy"},
            {"day": "Day 3", "high": 65, "low": 52, "condition": "Rain"},
        ][:days]

        return ToolResult(
            success=True,
            data={"location": location, "forecast": forecast},
            summary=f"{location}: {forecast[0]['condition']}, {forecast[0]['high']}°F",
            metadata={"mock": True},
        )

    async def _stock_quote(self, params: dict, user_id: UUID) -> ToolResult:
        """Get stock quote."""
        symbol = params["symbol"].upper()

        # Mock stock data
        mock_quotes = {
            "AAPL": {"price": 185.92, "change": 2.34, "change_pct": 1.27},
            "GOOGL": {"price": 141.80, "change": -0.56, "change_pct": -0.39},
            "MSFT": {"price": 378.91, "change": 4.12, "change_pct": 1.10},
            "AMZN": {"price": 178.25, "change": 1.89, "change_pct": 1.07},
        }

        if symbol in mock_quotes:
            data = mock_quotes[symbol]
            change_str = f"+{data['change']:.2f}" if data['change'] > 0 else f"{data['change']:.2f}"
            return ToolResult(
                success=True,
                data={"symbol": symbol, **data},
                summary=f"{symbol}: ${data['price']:.2f} ({change_str}, {data['change_pct']:+.2f}%)",
                metadata={"mock": True},
            )
        else:
            return ToolResult(
                success=True,
                data={"symbol": symbol, "price": 100.00, "change": 0, "change_pct": 0},
                summary=f"{symbol}: $100.00 (mock data)",
                metadata={"mock": True},
            )

    async def _currency_convert(self, params: dict, user_id: UUID) -> ToolResult:
        """Convert currency."""
        amount = params["amount"]
        from_curr = params["from_currency"].upper()
        to_curr = params["to_currency"].upper()

        # Mock exchange rates (vs USD)
        rates = {
            "USD": 1.0,
            "EUR": 0.92,
            "GBP": 0.79,
            "JPY": 148.50,
            "CAD": 1.36,
            "AUD": 1.54,
            "CHF": 0.88,
        }

        if from_curr not in rates or to_curr not in rates:
            return ToolResult(
                success=False,
                error=f"Unknown currency: {from_curr if from_curr not in rates else to_curr}",
            )

        # Convert via USD
        usd_amount = amount / rates[from_curr]
        result = usd_amount * rates[to_curr]

        return ToolResult(
            success=True,
            data={
                "from": {"amount": amount, "currency": from_curr},
                "to": {"amount": round(result, 2), "currency": to_curr},
                "rate": round(rates[to_curr] / rates[from_curr], 4),
            },
            summary=f"{amount:,.2f} {from_curr} = {result:,.2f} {to_curr}",
            metadata={"mock": True},
        )
