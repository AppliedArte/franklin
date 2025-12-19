"""Context Assembly System - Boardy-style context loading.

Before each LLM call, assemble:
1. User profile (financial snapshot, goals, preferences)
2. Conversation history (recent messages)
3. Internal notes (system observations about user)

This is the key to personalized, consistent responses across channels.
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, UserProfile, Conversation, Message


class ContextAssembler:
    """Assembles context for LLM calls, Boardy-style."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.max_history_messages = 20
        self.max_history_hours = 48

    async def assemble(
        self,
        user: User,
        conversation: Conversation,
    ) -> dict:
        """
        Assemble full context for an LLM call.

        Returns:
            dict with keys: profile_context, recent_messages, internal_notes, summary
        """
        context = {
            "profile_context": self._build_profile_context(user.profile),
            "recent_messages": await self._get_recent_messages(user, conversation),
            "internal_notes": self._get_internal_notes(user.profile),
            "conversation_summary": conversation.summary,
        }

        return context

    def _build_profile_context(self, profile: Optional[UserProfile]) -> str:
        """Build human-readable profile context for system prompt."""
        if not profile:
            return "No profile information available yet. This is a new user."

        sections = []

        # Financial snapshot
        financial = []
        if profile.annual_income:
            financial.append(f"Annual income: ${profile.annual_income:,.0f}")
        if profile.net_worth:
            financial.append(f"Net worth: ${profile.net_worth:,.0f}")
        if profile.liquid_assets:
            financial.append(f"Liquid assets: ${profile.liquid_assets:,.0f}")
        if profile.monthly_expenses:
            financial.append(f"Monthly expenses: ${profile.monthly_expenses:,.0f}")

        if financial:
            sections.append("**Financial Snapshot**\n" + "\n".join(f"- {f}" for f in financial))

        # Goals
        goals = []
        if profile.primary_goal:
            goals.append(f"Primary goal: {profile.primary_goal}")
        if profile.goal_timeline:
            goals.append(f"Timeline: {profile.goal_timeline}")
        if profile.risk_tolerance:
            goals.append(f"Risk tolerance: {profile.risk_tolerance}")
        if profile.interests:
            goals.append(f"Interests: {', '.join(profile.interests)}")

        if goals:
            sections.append("**Goals & Preferences**\n" + "\n".join(f"- {g}" for g in goals))

        # Investments
        if profile.existing_investments:
            inv_summary = self._summarize_investments(profile.existing_investments)
            sections.append(f"**Current Investments**\n{inv_summary}")

        # Debts
        if profile.debts:
            debt_summary = self._summarize_debts(profile.debts)
            sections.append(f"**Debts/Obligations**\n{debt_summary}")

        # Profile completeness
        sections.append(f"**Profile completeness: {profile.profile_score}%**")

        if not sections:
            return "Limited profile information. Still learning about this user."

        return "\n\n".join(sections)

    def _summarize_investments(self, investments: dict) -> str:
        """Summarize investment data into readable format."""
        if isinstance(investments, list):
            return "\n".join(f"- {inv}" for inv in investments[:5])
        elif isinstance(investments, dict):
            items = []
            for category, details in investments.items():
                if isinstance(details, (int, float)):
                    items.append(f"- {category}: ${details:,.0f}")
                else:
                    items.append(f"- {category}: {details}")
            return "\n".join(items[:5])
        return str(investments)[:200]

    def _summarize_debts(self, debts: dict) -> str:
        """Summarize debt data into readable format."""
        if isinstance(debts, list):
            return "\n".join(f"- {debt}" for debt in debts[:5])
        elif isinstance(debts, dict):
            items = []
            for category, amount in debts.items():
                if isinstance(amount, (int, float)):
                    items.append(f"- {category}: ${amount:,.0f}")
                else:
                    items.append(f"- {category}: {amount}")
            return "\n".join(items[:5])
        return str(debts)[:200]

    async def _get_recent_messages(
        self,
        user: User,
        current_conversation: Conversation,
    ) -> list[dict]:
        """Get recent messages across conversations for context."""
        cutoff = datetime.utcnow() - timedelta(hours=self.max_history_hours)

        # Get messages from current conversation
        messages = []
        for msg in current_conversation.messages[-self.max_history_messages:]:
            if msg.created_at > cutoff:
                messages.append({
                    "role": msg.role,
                    "content": msg.content,
                    "channel": msg.channel,
                    "timestamp": msg.created_at.isoformat(),
                })

        # If we need more context, get from other recent conversations
        if len(messages) < 5:
            result = await self.db.execute(
                select(Conversation)
                .where(
                    Conversation.user_id == user.id,
                    Conversation.id != current_conversation.id,
                    Conversation.updated_at > cutoff,
                )
                .order_by(Conversation.updated_at.desc())
                .limit(2)
            )
            other_convos = result.scalars().all()

            for conv in other_convos:
                for msg in conv.messages[-5:]:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content,
                        "channel": msg.channel,
                        "timestamp": msg.created_at.isoformat(),
                    })

        # Sort by timestamp and limit
        messages.sort(key=lambda x: x["timestamp"])
        return messages[-self.max_history_messages:]

    def _get_internal_notes(self, profile: Optional[UserProfile]) -> list[str]:
        """Get internal behavior notes (Boardy-style observations)."""
        if not profile or not profile.internal_notes:
            return []

        return profile.internal_notes[-10:]  # Last 10 notes

    async def add_internal_note(
        self,
        user: User,
        note: str,
    ) -> None:
        """Add an internal observation note to user profile."""
        if not user.profile:
            return

        if not user.profile.internal_notes:
            user.profile.internal_notes = []

        # Add timestamped note
        timestamped_note = f"[{datetime.utcnow().isoformat()}] {note}"
        user.profile.internal_notes.append(timestamped_note)

        # Keep only last 50 notes
        if len(user.profile.internal_notes) > 50:
            user.profile.internal_notes = user.profile.internal_notes[-50:]

    def build_system_context(self, context: dict) -> str:
        """
        Build the full system context string for LLM.

        This is injected into the system prompt to give the LLM
        full awareness of the user's profile and history.
        """
        parts = []

        # Profile
        if context.get("profile_context"):
            parts.append(f"## User Profile\n{context['profile_context']}")

        # Internal notes (behavior observations)
        if context.get("internal_notes"):
            notes = "\n".join(f"- {note}" for note in context["internal_notes"][-5:])
            parts.append(f"## Internal Observations\n{notes}")

        # Conversation summary
        if context.get("conversation_summary"):
            parts.append(f"## Conversation Summary\n{context['conversation_summary']}")

        return "\n\n".join(parts) if parts else "No prior context available."
