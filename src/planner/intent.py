"""Intent parsing - understanding what the user wants to do."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from anthropic import AsyncAnthropic

from src.config import get_settings

settings = get_settings()


class IntentCategory(str, Enum):
    """High-level intent categories."""
    TRAVEL = "travel"
    FINANCE = "finance"
    CALENDAR = "calendar"
    EMAIL = "email"
    RESEARCH = "research"
    CONVERSATION = "conversation"  # Just chatting
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Parsed user intent."""
    id: UUID = field(default_factory=uuid4)
    category: IntentCategory = IntentCategory.UNKNOWN
    action: str = ""  # e.g., "book_flight", "check_balance", "schedule_meeting"
    parameters: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    requires_clarification: bool = False
    clarification_questions: list[str] = field(default_factory=list)
    raw_message: str = ""
    parsed_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "category": self.category.value,
            "action": self.action,
            "parameters": self.parameters,
            "confidence": self.confidence,
            "requires_clarification": self.requires_clarification,
        }


# Intent recognition prompt
INTENT_SYSTEM_PROMPT = """You are an intent parser for Franklin, a personal AI assistant.

Given a user message, extract:
1. The primary intent category (travel, finance, calendar, email, research, conversation)
2. The specific action they want
3. Any parameters mentioned

Respond ONLY with valid JSON in this exact format:
{
    "category": "travel|finance|calendar|email|research|conversation",
    "action": "specific_action_name",
    "parameters": {
        "param1": "value1",
        "param2": "value2"
    },
    "confidence": 0.0 to 1.0,
    "requires_clarification": true/false,
    "clarification_questions": ["question1", "question2"]
}

Action mappings:
- travel: search_flights, book_flight, get_itinerary, cancel_booking
- finance: list_accounts, get_transactions, spending_summary, tax_summary, estimate_taxes, prepare_tax_documents, submit_tax_return, schedule_payment
- calendar: list_events, find_free_time, create_event, update_event, delete_event
- email: draft, send, search, read, reply
- research: web_search, price_lookup, weather, stock_quote, currency_convert
- conversation: greeting, thanks, question, clarification

Extract dates, times, locations, amounts, and other relevant parameters.
If critical information is missing, set requires_clarification to true and provide questions.
"""


class IntentParser:
    """Parses user messages to extract intent."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.default_llm_model

    async def parse(self, message: str, context: Optional[dict] = None) -> Intent:
        """Parse a user message to extract intent."""
        import json

        # Build context-aware prompt
        user_prompt = f"User message: {message}"
        if context:
            user_prompt += f"\n\nContext: {json.dumps(context)}"

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.1,  # Low temp for consistent parsing
                system=INTENT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )

            # Parse the JSON response
            response_text = response.content[0].text.strip()

            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            parsed = json.loads(response_text)

            return Intent(
                category=IntentCategory(parsed.get("category", "unknown")),
                action=parsed.get("action", ""),
                parameters=parsed.get("parameters", {}),
                confidence=parsed.get("confidence", 0.5),
                requires_clarification=parsed.get("requires_clarification", False),
                clarification_questions=parsed.get("clarification_questions", []),
                raw_message=message,
            )

        except json.JSONDecodeError:
            # If parsing fails, return conversation intent
            return Intent(
                category=IntentCategory.CONVERSATION,
                action="unknown",
                parameters={"message": message},
                confidence=0.3,
                raw_message=message,
            )
        except Exception as e:
            return Intent(
                category=IntentCategory.UNKNOWN,
                action="error",
                parameters={"error": str(e), "message": message},
                confidence=0.0,
                raw_message=message,
            )

    async def parse_with_tools(self, message: str, available_tools: list[dict]) -> Intent:
        """Parse intent with awareness of available tools."""
        # Create a more specific prompt with tool info
        tools_summary = []
        for tool in available_tools:
            tools_summary.append(f"- {tool['name']}: {tool.get('description', '')}")

        context = {"available_tools": tools_summary}
        return await self.parse(message, context)
