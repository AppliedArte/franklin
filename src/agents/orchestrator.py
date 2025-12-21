"""Conversation Orchestrator - Central hub for all conversations.

Inspired by Boardy AI's context loading model:
- Assembles context before each LLM call (profile + history + notes)
- Routes to appropriate specialist agent
- Maintains cross-channel session continuity
"""

import uuid
from typing import Optional, Tuple
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, UserProfile, Conversation, Message
from src.agents.profile_builder import ProfileBuilder
from src.agents.advisory import AdvisoryAgent
from src.utils.context import ContextAssembler
from src.rag.fact_extractor import FactExtractor


class ConversationOrchestrator:
    """Orchestrates conversations across all channels."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.context_assembler = ContextAssembler(db)
        self.profile_builder = ProfileBuilder()
        self.advisory_agent = AdvisoryAgent()
        self.fact_extractor = FactExtractor()

    async def handle_message(
        self,
        channel: str,
        channel_user_id: str,
        message_content: str,
        conversation_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        return_metadata: bool = False,
    ) -> str | Tuple[str, str, int]:
        """
        Handle an incoming message from any channel.

        Args:
            channel: Communication channel (whatsapp, voice, email, web)
            channel_user_id: User identifier for the channel
            message_content: The message content
            conversation_id: Optional existing conversation ID
            metadata: Optional channel-specific metadata
            return_metadata: If True, return (response, conversation_id, profile_score)

        Returns:
            AI response string, or tuple with metadata if return_metadata=True
        """
        # 1. Find or create user
        user = await self._get_or_create_user(channel, channel_user_id)

        # 2. Find or create conversation
        conversation = await self._get_or_create_conversation(
            user, channel, conversation_id
        )

        # 3. Store incoming message
        await self._store_message(
            conversation, "user", message_content, channel, metadata
        )

        # 4. Assemble context (Boardy-style: profile + history + notes)
        context = await self.context_assembler.assemble(user, conversation)

        # 5. Route to appropriate agent and generate response
        response = await self._route_and_respond(user, context, message_content)

        # 6. Store AI response
        await self._store_message(
            conversation, "assistant", response, channel, None
        )

        # 7. Update profile if new information was extracted
        await self._update_profile_from_conversation(user, message_content, response)

        # 8. Extract and store facts for RAG (runs async, non-blocking)
        await self._extract_facts(user.id, conversation.id, message_content, response)

        # 9. Commit changes
        await self.db.commit()

        if return_metadata:
            profile_score = user.profile.profile_score if user.profile else 0
            return response, conversation.id, profile_score

        return response

    async def _get_or_create_user(self, channel: str, channel_user_id: str) -> User:
        """Find existing user or create new one."""
        # Build query based on channel
        if channel == "whatsapp":
            query = select(User).where(User.whatsapp_id == channel_user_id)
        elif channel == "email":
            query = select(User).where(User.email == channel_user_id)
        elif channel == "web":
            query = select(User).where(User.id == channel_user_id)
        else:
            # Phone for voice
            query = select(User).where(User.phone == channel_user_id)

        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if user:
            return user

        # Create new user
        user = User(id=str(uuid.uuid4()))

        if channel == "whatsapp":
            user.whatsapp_id = channel_user_id
            # Extract phone from WhatsApp ID (format: whatsapp:+1234567890)
            if channel_user_id.startswith("whatsapp:"):
                user.phone = channel_user_id.replace("whatsapp:", "")
        elif channel == "email":
            user.email = channel_user_id
        elif channel == "voice":
            user.phone = channel_user_id
        # For web, the channel_user_id is the user ID

        # Create empty profile
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=user.id,
            profile_score=0,
            internal_notes=[],
        )

        self.db.add(user)
        self.db.add(profile)
        await self.db.flush()

        # Reload to get profile relationship
        result = await self.db.execute(
            select(User).where(User.id == user.id)
        )
        return result.scalar_one()

    async def _get_or_create_conversation(
        self,
        user: User,
        channel: str,
        conversation_id: Optional[str] = None,
    ) -> Conversation:
        """Find active conversation or create new one."""
        # If conversation_id provided, try to find it
        if conversation_id:
            result = await self.db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()
            if conversation:
                return conversation

        # Find recent active conversation for this user/channel
        cutoff = datetime.utcnow() - timedelta(hours=24)
        result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.user_id == user.id,
                Conversation.channel == channel,
                Conversation.is_active == True,
                Conversation.updated_at > cutoff,
            )
            .order_by(Conversation.updated_at.desc())
            .limit(1)
        )
        conversation = result.scalar_one_or_none()

        if conversation:
            conversation.updated_at = datetime.utcnow()
            return conversation

        # Create new conversation
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user.id,
            channel=channel,
            is_active=True,
        )
        self.db.add(conversation)
        await self.db.flush()

        return conversation

    async def _store_message(
        self,
        conversation: Conversation,
        role: str,
        content: str,
        channel: str,
        metadata: Optional[dict],
    ) -> Message:
        """Store a message in the conversation."""
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            role=role,
            content=content,
            channel=channel,
            metadata=metadata,
        )
        self.db.add(message)
        await self.db.flush()

        return message

    async def _route_and_respond(
        self,
        user: User,
        context: dict,
        message: str,
    ) -> str:
        """Route to appropriate agent and generate response."""
        profile = user.profile
        profile_score = profile.profile_score if profile else 0

        # Build messages for LLM
        messages = self._build_llm_messages(context, message)

        # Build profile context string
        profile_context = context.get("profile_summary", "")

        # Routing logic based on profile completeness and user intent
        if profile_score < 30:
            # Still building profile - use Profile Builder
            response = await self.profile_builder.generate(messages)
        else:
            # Profile sufficient - use Advisory Agent with RAG
            response = await self.advisory_agent.generate_with_rag(
                db=self.db,
                user_id=user.id,
                messages=messages,
                profile_context=profile_context,
            )

        return response

    def _build_llm_messages(self, context: dict, current_message: str) -> list[dict]:
        """Build LLM message history from context."""
        messages = []

        # Add recent conversation history
        for msg in context.get("recent_messages", []):
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": current_message,
        })

        return messages

    async def _update_profile_from_conversation(
        self,
        user: User,
        user_message: str,
        ai_response: str,
    ) -> None:
        """Extract and update profile information from conversation."""
        if not user.profile:
            return

        # Use Profile Builder to extract any new information
        extracted = await self.profile_builder.extract_profile_info(
            user_message,
            ai_response,
            user.profile,
        )

        if extracted:
            # Update profile with extracted information
            for key, value in extracted.items():
                if hasattr(user.profile, key) and value is not None:
                    setattr(user.profile, key, value)

            # Recalculate profile score
            user.profile.profile_score = self._calculate_profile_score(user.profile)
            user.profile.updated_at = datetime.utcnow()

    def _calculate_profile_score(self, profile: UserProfile) -> int:
        """Calculate profile completeness score (0-100)."""
        score = 0
        weights = {
            "annual_income": 15,
            "net_worth": 15,
            "liquid_assets": 10,
            "monthly_expenses": 10,
            "primary_goal": 20,
            "goal_timeline": 10,
            "risk_tolerance": 15,
            "interests": 5,
        }

        for field, weight in weights.items():
            value = getattr(profile, field, None)
            if value is not None:
                if isinstance(value, list) and len(value) > 0:
                    score += weight
                elif not isinstance(value, list) and value:
                    score += weight

        return min(score, 100)

    async def _extract_facts(
        self,
        user_id: str,
        conversation_id: str,
        user_message: str,
        ai_response: str,
    ) -> None:
        """Extract facts from conversation and store for RAG."""
        try:
            facts = await self.fact_extractor.extract_and_store_facts(
                db=self.db,
                user_id=user_id,
                user_message=user_message,
                assistant_message=ai_response,
                conversation_id=conversation_id,
            )
            if facts:
                # Log extracted facts for debugging
                import logging
                logging.debug(f"Extracted {len(facts)} facts for user {user_id}: {facts}")
        except Exception as e:
            # Don't fail the conversation if fact extraction fails
            import logging
            logging.warning(f"Fact extraction failed for user {user_id}: {e}")
