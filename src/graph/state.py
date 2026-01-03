"""State definitions for Franklin's LangGraph agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any, Literal, Optional, Sequence, TypedDict
from uuid import UUID

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph.message import add_messages


class MessageType(str, Enum):
    """Types of messages in the conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"


class ApprovalStatus(str, Enum):
    """Status of pending approval."""
    NONE = "none"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AgentState(TypedDict):
    """
    State that flows through the Franklin agent graph.

    This is the central state object that gets passed between nodes.
    Using TypedDict for LangGraph compatibility.
    """
    # Core conversation
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str
    channel: str
    conversation_id: Optional[str]

    # User context (loaded from DB)
    user_profile: Optional[dict]
    profile_score: int

    # Intent & Planning
    intent: Optional[dict]  # Parsed intent
    plan: Optional[dict]  # Execution plan
    current_step: int

    # Tool execution
    tool_calls: list[dict]
    tool_results: list[dict]

    # Approval flow
    approval_status: str  # ApprovalStatus value
    pending_approval: Optional[dict]
    approval_response: Optional[str]

    # Proactive
    proactive_notifications: list[dict]

    # Control flow
    next_action: str  # What to do next
    should_respond: bool
    final_response: Optional[str]

    # Metadata
    started_at: Optional[str]
    completed_at: Optional[str]
    error: Optional[str]


def create_initial_state(
    user_id: str,
    channel: str,
    message: str,
    conversation_id: Optional[str] = None,
    user_profile: Optional[dict] = None,
) -> AgentState:
    """Create initial state for a new conversation turn."""
    return AgentState(
        messages=[HumanMessage(content=message)],
        user_id=user_id,
        channel=channel,
        conversation_id=conversation_id,
        user_profile=user_profile,
        profile_score=user_profile.get("profile_score", 0) if user_profile else 0,
        intent=None,
        plan=None,
        current_step=0,
        tool_calls=[],
        tool_results=[],
        approval_status=ApprovalStatus.NONE.value,
        pending_approval=None,
        approval_response=None,
        proactive_notifications=[],
        next_action="parse_intent",
        should_respond=False,
        final_response=None,
        started_at=datetime.utcnow().isoformat(),
        completed_at=None,
        error=None,
    )


def get_last_human_message(state: AgentState) -> Optional[str]:
    """Get the last human message from state."""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            return msg.content
    return None


def get_conversation_history(state: AgentState, limit: int = 10) -> list[dict]:
    """Get conversation history in simple format."""
    history = []
    for msg in state["messages"][-limit:]:
        if isinstance(msg, HumanMessage):
            history.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            history.append({"role": "assistant", "content": msg.content})
    return history
