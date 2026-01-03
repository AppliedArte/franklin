"""Franklin LangGraph - The main agent graph."""

from __future__ import annotations

from typing import Optional

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from src.graph.state import AgentState, create_initial_state
from src.graph.nodes import (
    parse_intent_node,
    agent_node,
    execute_tools_node,
    request_approval_node,
    execute_approved_node,
    respond_node,
    check_proactive_node,
    route_after_intent,
    route_after_agent,
)


def create_franklin_graph(checkpointer: Optional[MemorySaver] = None) -> StateGraph:
    """
    Create the Franklin agent graph.

    Graph Structure:
    ```
    START
      │
      ▼
    ┌─────────────────┐
    │  parse_intent   │ ──────────────────────────────┐
    └────────┬────────┘                               │
             │                                        │
             ▼ (needs action)                         │ (conversation only)
    ┌─────────────────┐                               │
    │     agent       │ ◄─────────────────┐           │
    └────────┬────────┘                   │           │
             │                            │           │
     ┌───────┴───────┬──────────┐         │           │
     │               │          │         │           │
     ▼               ▼          ▼         │           │
    ┌─────┐   ┌───────────┐  ┌──────┐     │           │
    │tools│   │  approval │  │respond│    │           │
    └──┬──┘   └─────┬─────┘  └──┬───┘     │           │
       │            │           │         │           │
       │            ▼           │         │           │
       │      ┌───────────┐     │         │           │
       │      │  respond  │     │         │           │
       │      │ (waiting) │     │         │           │
       │      └─────┬─────┘     │         │           │
       │            │           │         │           │
       │    (user approves)     │         │           │
       │            │           │         │           │
       │      ┌─────▼─────┐     │         │           │
       │      │ execute   │     │         │           │
       │      │ approved  │     │         │           │
       │      └─────┬─────┘     │         │           │
       │            │           │         │           │
       └────────────┴───────────┴─────────┘           │
                                                      │
                          ┌───────────────────────────┘
                          │
                          ▼
                    ┌───────────┐
                    │  respond  │
                    └─────┬─────┘
                          │
                          ▼
                    ┌───────────┐
                    │ proactive │
                    └─────┬─────┘
                          │
                          ▼
                        END
    ```
    """
    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("execute_tools", execute_tools_node)
    workflow.add_node("request_approval", request_approval_node)
    workflow.add_node("execute_approved", execute_approved_node)
    workflow.add_node("respond", respond_node)
    workflow.add_node("check_proactive", check_proactive_node)

    # Set entry point
    workflow.set_entry_point("parse_intent")

    # Add conditional edges from parse_intent
    workflow.add_conditional_edges(
        "parse_intent",
        route_after_intent,
        {
            "agent": "agent",
            "respond": "respond",
            "execute_approved": "execute_approved",
        }
    )

    # Add conditional edges from agent
    workflow.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "execute_tools": "execute_tools",
            "request_approval": "request_approval",
            "respond": "respond",
        }
    )

    # After tools, go back to agent
    workflow.add_edge("execute_tools", "agent")

    # After approval request, go to respond (waiting for user)
    workflow.add_edge("request_approval", "respond")

    # After executing approved action, go to respond
    workflow.add_edge("execute_approved", "respond")

    # After respond, check proactive then end
    workflow.add_edge("respond", "check_proactive")
    workflow.add_edge("check_proactive", END)

    # Compile with optional checkpointer
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    else:
        return workflow.compile()


class FranklinGraph:
    """
    High-level wrapper for the Franklin agent graph.

    Provides a simple interface for running the graph with
    conversation persistence via checkpointing.
    """

    def __init__(self, checkpoint_path: Optional[str] = None):
        """
        Initialize the Franklin graph.

        Args:
            checkpoint_path: Path to SQLite file for persistence.
                           If None, uses in-memory checkpointing.
        """
        if checkpoint_path:
            # Use SQLite for persistence
            self.checkpointer = AsyncSqliteSaver.from_conn_string(checkpoint_path)
        else:
            # Use in-memory for testing
            self.checkpointer = MemorySaver()

        self.graph = create_franklin_graph(self.checkpointer)

    async def run(
        self,
        user_id: str,
        channel: str,
        message: str,
        conversation_id: Optional[str] = None,
        user_profile: Optional[dict] = None,
    ) -> dict:
        """
        Run the graph for a single message.

        Args:
            user_id: User identifier
            channel: Communication channel (whatsapp, telegram, web, etc.)
            message: User's message
            conversation_id: Optional conversation ID for threading
            user_profile: Optional user profile data

        Returns:
            Final state with response
        """
        # Create initial state
        initial_state = create_initial_state(
            user_id=user_id,
            channel=channel,
            message=message,
            conversation_id=conversation_id,
            user_profile=user_profile,
        )

        # Create thread config for checkpointing
        config = {
            "configurable": {
                "thread_id": conversation_id or f"{user_id}_{channel}",
            }
        }

        # Run the graph
        final_state = await self.graph.ainvoke(initial_state, config)

        return final_state

    async def get_response(
        self,
        user_id: str,
        channel: str,
        message: str,
        conversation_id: Optional[str] = None,
        user_profile: Optional[dict] = None,
    ) -> str:
        """
        Run the graph and return just the response text.

        This is the main method for integration with adapters.
        """
        final_state = await self.run(
            user_id=user_id,
            channel=channel,
            message=message,
            conversation_id=conversation_id,
            user_profile=user_profile,
        )

        # Get the response
        response = final_state.get("final_response", "")

        # Append proactive notifications if any
        proactive = final_state.get("proactive_notifications", [])
        if proactive:
            response += "\n\n---\n"
            for p in proactive:
                response += f"💡 {p['message']}\n"

        return response

    async def stream(
        self,
        user_id: str,
        channel: str,
        message: str,
        conversation_id: Optional[str] = None,
        user_profile: Optional[dict] = None,
    ):
        """
        Stream the graph execution for real-time updates.

        Yields state updates as they happen.
        """
        initial_state = create_initial_state(
            user_id=user_id,
            channel=channel,
            message=message,
            conversation_id=conversation_id,
            user_profile=user_profile,
        )

        config = {
            "configurable": {
                "thread_id": conversation_id or f"{user_id}_{channel}",
            }
        }

        async for event in self.graph.astream(initial_state, config):
            yield event

    def get_graph_visualization(self) -> str:
        """Get Mermaid diagram of the graph."""
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception:
            return "Graph visualization not available"


# Singleton instance for import
_franklin_graph: Optional[FranklinGraph] = None


def get_franklin_graph(checkpoint_path: Optional[str] = None) -> FranklinGraph:
    """Get or create the Franklin graph singleton."""
    global _franklin_graph
    if _franklin_graph is None:
        _franklin_graph = FranklinGraph(checkpoint_path)
    return _franklin_graph
