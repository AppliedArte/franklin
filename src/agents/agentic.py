"""Agentic Orchestrator - Franklin's brain powered by LangGraph.

Enhances the base orchestrator with:
- LangGraph-based agent execution
- Tool use capabilities
- Multi-step planning with conditional routing
- Approval management with checkpointing
- Proactive notifications
"""

from __future__ import annotations

import uuid
from typing import Optional, Tuple
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.orchestrator import ConversationOrchestrator
from src.graph import FranklinGraph, create_franklin_graph
from src.graph.state import ApprovalStatus
from src.proactive import ProactiveEngine
from src.config import get_settings

settings = get_settings()


class AgenticOrchestrator(ConversationOrchestrator):
    """
    Enhanced orchestrator using LangGraph for agentic behavior.

    This orchestrator uses a graph-based approach where:
    - Nodes represent distinct operations (parse, act, respond)
    - Edges define control flow based on state
    - Checkpointing enables conversation continuity
    - Tool execution is handled within the graph
    """

    def __init__(self, db: AsyncSession, checkpoint_path: Optional[str] = None):
        """
        Initialize the agentic orchestrator.

        Args:
            db: Database session for user/conversation management
            checkpoint_path: Optional path to SQLite file for graph state persistence
        """
        super().__init__(db)

        # Initialize LangGraph
        self.franklin_graph = FranklinGraph(checkpoint_path)
        self.proactive = ProactiveEngine()

        # Track pending states per user for complex flows
        self._pending_states: dict[str, dict] = {}

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
        Handle incoming message using LangGraph agent.

        The graph handles:
        1. Intent parsing
        2. Tool selection and execution
        3. Approval flow management
        4. Response generation
        """
        # 1. Get or create user (from base orchestrator)
        user = await self._get_or_create_user(channel, channel_user_id)

        # 2. Get or create conversation
        conversation = await self._get_or_create_conversation(
            user, channel, conversation_id
        )

        # 3. Store incoming message
        await self._store_message(
            conversation, "user", message_content, channel, metadata
        )

        # 4. Build user profile context
        user_profile = None
        if user.profile:
            user_profile = {
                "profile_score": user.profile.profile_score,
                "primary_goal": user.profile.primary_goal,
                "risk_tolerance": user.profile.risk_tolerance,
                "settings": {
                    "low_balance_threshold": 500,  # Default, would come from settings
                },
            }

        # 5. Check for pending approval state
        pending_state = self._pending_states.get(user.id)
        if pending_state and pending_state.get("approval_status") == ApprovalStatus.PENDING.value:
            # User might be responding to approval request
            # The graph will detect this in parse_intent_node
            pass

        # 6. Run the LangGraph agent
        try:
            final_state = await self.franklin_graph.run(
                user_id=user.id,
                channel=channel,
                message=message_content,
                conversation_id=str(conversation.id),
                user_profile=user_profile,
            )

            # Extract response
            response = final_state.get("final_response", "")

            # Add proactive notifications
            proactive = final_state.get("proactive_notifications", [])
            if proactive:
                response += "\n\n---\n"
                for p in proactive:
                    response += f"💡 {p['message']}\n"

            # Track pending approval state
            if final_state.get("approval_status") == ApprovalStatus.PENDING.value:
                self._pending_states[user.id] = {
                    "approval_status": ApprovalStatus.PENDING.value,
                    "pending_approval": final_state.get("pending_approval"),
                }
            else:
                # Clear pending state
                self._pending_states.pop(user.id, None)

        except Exception as e:
            # Fallback to base orchestrator on graph error
            import logging
            logging.error(f"LangGraph error: {e}")
            context = await self.context_assembler.assemble(user, conversation)
            response = await self._route_and_respond(user, context, message_content)

        # 7. Store AI response
        await self._store_message(
            conversation, "assistant", response, channel, None
        )

        # 8. Update profile if new information extracted
        await self._update_profile_from_conversation(user, message_content, response)

        # 9. Extract facts for RAG
        await self._extract_facts(user.id, conversation.id, message_content, response)

        await self.db.commit()

        if return_metadata:
            profile_score = user.profile.profile_score if user.profile else 0
            return response, str(conversation.id), profile_score

        return response

    async def get_pending_approvals(self, user_id: str) -> list[dict]:
        """Get pending approvals for a user."""
        pending = self._pending_states.get(user_id, {})
        if pending.get("approval_status") == ApprovalStatus.PENDING.value:
            return [pending.get("pending_approval", {})]
        return []

    async def cancel_pending_approval(self, user_id: str) -> bool:
        """Cancel a pending approval."""
        if user_id in self._pending_states:
            del self._pending_states[user_id]
            return True
        return False

    async def enable_proactive(self, user_id: str) -> None:
        """Enable all proactive triggers for a user."""
        from uuid import UUID
        self.proactive.enable_all_defaults(UUID(user_id))

    async def get_notifications(self, user_id: str) -> list[dict]:
        """Get pending notifications for a user."""
        from uuid import UUID
        notifications = await self.proactive.get_pending_notifications(UUID(user_id))
        return [n.to_dict() for n in notifications]

    def get_graph_visualization(self) -> str:
        """Get Mermaid diagram of the agent graph."""
        return self.franklin_graph.get_graph_visualization()

    async def stream_response(
        self,
        channel: str,
        channel_user_id: str,
        message_content: str,
        conversation_id: Optional[str] = None,
    ):
        """
        Stream the agent response for real-time UI updates.

        Yields state updates as the graph executes.
        """
        user = await self._get_or_create_user(channel, channel_user_id)
        conversation = await self._get_or_create_conversation(
            user, channel, conversation_id
        )

        user_profile = None
        if user.profile:
            user_profile = {
                "profile_score": user.profile.profile_score,
            }

        async for event in self.franklin_graph.stream(
            user_id=user.id,
            channel=channel,
            message=message_content,
            conversation_id=str(conversation.id),
            user_profile=user_profile,
        ):
            yield event


# For backwards compatibility
def create_agentic_orchestrator(db: AsyncSession, checkpoint_path: Optional[str] = None) -> AgenticOrchestrator:
    """Factory function to create an AgenticOrchestrator."""
    return AgenticOrchestrator(db, checkpoint_path)
