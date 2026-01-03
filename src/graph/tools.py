"""LangGraph tool wrappers for Franklin's capabilities."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

from src.tools.registry import registry, register_all_tools
from src.tools.base import ApprovalLevel


# Ensure tools are registered
register_all_tools()


# ============================================================
# TRAVEL TOOLS
# ============================================================

class SearchFlightsInput(BaseModel):
    """Input for flight search."""
    origin: str = Field(description="Origin airport code (e.g., 'SFO')")
    destination: str = Field(description="Destination airport code (e.g., 'NRT')")
    departure_date: str = Field(description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(default=None, description="Return date for round trip")
    passengers: int = Field(default=1, description="Number of passengers")
    cabin_class: str = Field(default="economy", description="Cabin class")


class BookFlightInput(BaseModel):
    """Input for flight booking."""
    flight_id: str = Field(description="Flight offer ID from search results")
    passenger_name: str = Field(description="Primary passenger name")


# ============================================================
# CALENDAR TOOLS
# ============================================================

class ListEventsInput(BaseModel):
    """Input for listing calendar events."""
    start_date: str = Field(description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD)")
    max_results: int = Field(default=10, description="Maximum events to return")


class CreateEventInput(BaseModel):
    """Input for creating calendar event."""
    title: str = Field(description="Event title")
    start: str = Field(description="Start datetime (ISO format)")
    end: str = Field(description="End datetime (ISO format)")
    location: Optional[str] = Field(default=None, description="Event location")
    description: Optional[str] = Field(default=None, description="Event description")


class FindFreeTimeInput(BaseModel):
    """Input for finding free time."""
    start_date: str = Field(description="Start of search range (YYYY-MM-DD)")
    end_date: str = Field(description="End of search range (YYYY-MM-DD)")
    duration_minutes: int = Field(description="Required duration in minutes")


# ============================================================
# FINANCE TOOLS
# ============================================================

class ListAccountsInput(BaseModel):
    """Input for listing accounts."""
    account_type: str = Field(default="all", description="Filter by account type")


class SpendingSummaryInput(BaseModel):
    """Input for spending summary."""
    period: str = Field(description="Time period: week, month, quarter, year")


class TaxSummaryInput(BaseModel):
    """Input for tax summary."""
    year: int = Field(description="Tax year")


# ============================================================
# EMAIL TOOLS
# ============================================================

class DraftEmailInput(BaseModel):
    """Input for drafting email."""
    to: list[str] = Field(description="Recipient email addresses")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")


class SendEmailInput(BaseModel):
    """Input for sending email."""
    draft_id: Optional[str] = Field(default=None, description="Draft ID to send")
    to: Optional[list[str]] = Field(default=None, description="Recipients if not using draft")
    subject: Optional[str] = Field(default=None, description="Subject if not using draft")
    body: Optional[str] = Field(default=None, description="Body if not using draft")


class SearchEmailInput(BaseModel):
    """Input for searching emails."""
    query: str = Field(description="Search query")
    folder: str = Field(default="all", description="Folder to search")


# ============================================================
# RESEARCH TOOLS
# ============================================================

class WebSearchInput(BaseModel):
    """Input for web search."""
    query: str = Field(description="Search query")
    num_results: int = Field(default=5, description="Number of results")


class StockQuoteInput(BaseModel):
    """Input for stock quote."""
    symbol: str = Field(description="Stock ticker symbol")


class WeatherInput(BaseModel):
    """Input for weather lookup."""
    location: str = Field(description="Location to get weather for")
    days: int = Field(default=3, description="Number of forecast days")


# ============================================================
# TOOL CREATION
# ============================================================

async def execute_tool(tool_name: str, action: str, params: dict, user_id: str) -> dict:
    """Execute a tool action and return result."""
    tool = registry.get(tool_name)
    if not tool:
        return {"success": False, "error": f"Tool not found: {tool_name}"}

    try:
        result = await tool.execute(action, params, UUID(user_id))
        return {
            "success": result.success,
            "data": result.data,
            "summary": result.summary,
            "error": result.error,
            "options": result.options,
            "requires_approval": tool.get_approval_level(action) in (
                ApprovalLevel.CONFIRM, ApprovalLevel.STRICT
            ),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_langchain_tools() -> list[BaseTool]:
    """Get all tools as LangChain tools."""
    tools = []

    # Travel tools
    tools.append(StructuredTool.from_function(
        coroutine=lambda **kwargs: execute_tool("travel", "search_flights", kwargs, kwargs.pop("_user_id", "")),
        name="search_flights",
        description="Search for available flights between two cities. Returns flight options with prices.",
        args_schema=SearchFlightsInput,
    ))

    # Calendar tools
    tools.append(StructuredTool.from_function(
        coroutine=lambda **kwargs: execute_tool("calendar", "list_events", kwargs, kwargs.pop("_user_id", "")),
        name="list_calendar_events",
        description="List upcoming calendar events for a date range.",
        args_schema=ListEventsInput,
    ))

    tools.append(StructuredTool.from_function(
        coroutine=lambda **kwargs: execute_tool("calendar", "find_free_time", kwargs, kwargs.pop("_user_id", "")),
        name="find_free_time",
        description="Find available time slots in the calendar.",
        args_schema=FindFreeTimeInput,
    ))

    # Finance tools
    tools.append(StructuredTool.from_function(
        coroutine=lambda **kwargs: execute_tool("finance", "list_accounts", kwargs, kwargs.pop("_user_id", "")),
        name="list_accounts",
        description="List connected bank accounts and their balances.",
        args_schema=ListAccountsInput,
    ))

    tools.append(StructuredTool.from_function(
        coroutine=lambda **kwargs: execute_tool("finance", "spending_summary", kwargs, kwargs.pop("_user_id", "")),
        name="spending_summary",
        description="Get spending summary by category for a time period.",
        args_schema=SpendingSummaryInput,
    ))

    tools.append(StructuredTool.from_function(
        coroutine=lambda **kwargs: execute_tool("finance", "tax_summary", kwargs, kwargs.pop("_user_id", "")),
        name="tax_summary",
        description="Get tax-relevant summary for a year including income, deductions, and estimated liability.",
        args_schema=TaxSummaryInput,
    ))

    # Email tools
    tools.append(StructuredTool.from_function(
        coroutine=lambda **kwargs: execute_tool("email", "draft", kwargs, kwargs.pop("_user_id", "")),
        name="draft_email",
        description="Create an email draft. Does not send - requires separate approval.",
        args_schema=DraftEmailInput,
    ))

    tools.append(StructuredTool.from_function(
        coroutine=lambda **kwargs: execute_tool("email", "search", kwargs, kwargs.pop("_user_id", "")),
        name="search_emails",
        description="Search emails in inbox.",
        args_schema=SearchEmailInput,
    ))

    # Research tools
    tools.append(StructuredTool.from_function(
        coroutine=lambda **kwargs: execute_tool("research", "web_search", kwargs, kwargs.pop("_user_id", "")),
        name="web_search",
        description="Search the web for information.",
        args_schema=WebSearchInput,
    ))

    tools.append(StructuredTool.from_function(
        coroutine=lambda **kwargs: execute_tool("research", "stock_quote", kwargs, kwargs.pop("_user_id", "")),
        name="stock_quote",
        description="Get current stock price and info for a ticker symbol.",
        args_schema=StockQuoteInput,
    ))

    tools.append(StructuredTool.from_function(
        coroutine=lambda **kwargs: execute_tool("research", "weather", kwargs, kwargs.pop("_user_id", "")),
        name="weather",
        description="Get weather forecast for a location.",
        args_schema=WeatherInput,
    ))

    return tools


# Tools requiring approval (for routing)
APPROVAL_REQUIRED_TOOLS = {
    "book_flight",
    "create_calendar_event",
    "update_calendar_event",
    "delete_calendar_event",
    "send_email",
    "reply_email",
    "schedule_payment",
    "submit_tax_return",
}
