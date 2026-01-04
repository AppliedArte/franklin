"""Global tool registry and convenience functions."""

from typing import Optional

from src.tools.base import Tool, ToolRegistry, ToolCategory

# Global registry instance
registry = ToolRegistry()


def get_tool(name: str) -> Optional[Tool]:
    """Get a tool by name from the global registry."""
    return registry.get(name)


def list_tools(category: Optional[ToolCategory] = None) -> list[Tool]:
    """List all tools, optionally filtered by category."""
    if category:
        return registry.list_by_category(category)
    return registry.list()


def register_all_tools() -> None:
    """Register all available tools. Call on startup."""
    # Import tools here to avoid circular imports
    from src.tools.travel import TravelTool
    from src.tools.calendar import CalendarTool
    from src.tools.email import EmailTool
    from src.tools.gmail import GmailTool
    from src.tools.finance import FinanceTool
    from src.tools.research import ResearchTool
    from src.tools.flight_booking_chrome import FlightBookingChromeTool
    from src.tools.payments import PaymentsTool

    registry.register(TravelTool())
    registry.register(CalendarTool())
    registry.register(EmailTool())  # Sending emails via Resend
    registry.register(GmailTool())  # Reading/managing Gmail
    registry.register(FinanceTool())
    registry.register(ResearchTool())
    registry.register(FlightBookingChromeTool())
    registry.register(PaymentsTool())
