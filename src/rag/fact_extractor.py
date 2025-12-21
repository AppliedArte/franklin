"""Extract facts from conversations to build user knowledge base."""

import json
import uuid
from typing import Optional

from anthropic import AsyncAnthropic
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.rag.ingestion import DocumentIngestionService

settings = get_settings()


FACT_EXTRACTION_PROMPT = """You are analyzing a conversation between Franklin (an AI wealth advisor) and a user.
Extract any NEW facts learned about the user from the latest exchange.

Focus on:
- Financial goals and aspirations
- Investment preferences and risk tolerance
- Current holdings or portfolio details
- Income, net worth, or financial situation
- Personal circumstances that affect finances (family, job, location)
- Investment experience and knowledge level
- Specific interests (crypto, real estate, startups, etc.)
- Concerns or pain points
- Timeline and liquidity needs

Rules:
- Only extract facts explicitly stated or clearly implied
- Don't infer or assume beyond what's said
- Each fact should be a standalone, clear statement
- Assign a category to each fact
- Rate confidence 0.0-1.0 based on how explicit the information is

Categories: goals, preferences, holdings, income, net_worth, experience, interests, concerns, timeline, personal, other

Return JSON array:
[
  {"category": "goals", "fact": "Wants to retire by age 55", "confidence": 0.9},
  {"category": "holdings", "fact": "Currently holds $500k in index funds", "confidence": 1.0}
]

If no new facts, return empty array: []

Latest exchange to analyze:
User: {user_message}
Franklin: {assistant_message}
"""


class FactExtractor:
    """Extract facts from conversations and store them."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.ingestion = DocumentIngestionService()

    async def extract_and_store_facts(
        self,
        db: AsyncSession,
        user_id: str,
        user_message: str,
        assistant_message: str,
        conversation_id: Optional[str] = None,
    ) -> list[dict]:
        """Extract facts from a conversation exchange and store them."""
        # Use Haiku for fast, cheap extraction
        response = await self.client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": FACT_EXTRACTION_PROMPT.format(
                        user_message=user_message,
                        assistant_message=assistant_message,
                    ),
                }
            ],
        )

        # Parse the response
        try:
            response_text = response.content[0].text.strip()
            # Handle markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            facts = json.loads(response_text)
        except (json.JSONDecodeError, IndexError):
            return []

        if not facts:
            return []

        # Store each fact
        stored_facts = []
        for fact_data in facts:
            if not isinstance(fact_data, dict):
                continue

            category = fact_data.get("category", "other")
            fact_text = fact_data.get("fact", "")
            confidence = float(fact_data.get("confidence", 1.0))

            if not fact_text:
                continue

            user_fact = await self.ingestion.ingest_user_fact(
                db=db,
                user_id=user_id,
                category=category,
                fact=fact_text,
                source="conversation",
                conversation_id=conversation_id,
                confidence=confidence,
            )

            stored_facts.append({
                "id": user_fact.id,
                "category": category,
                "fact": fact_text,
                "confidence": confidence,
            })

        return stored_facts

    async def close(self):
        """Cleanup resources."""
        await self.ingestion.close()
