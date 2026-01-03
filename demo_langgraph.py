#!/usr/bin/env python3
"""Demo script for Franklin's LangGraph-based agentic system.

Run with: python demo_langgraph.py
"""

import asyncio
from uuid import uuid4

from src.graph import FranklinGraph, create_franklin_graph
from src.graph.state import create_initial_state
from src.tools.registry import register_all_tools


async def demo_graph_visualization():
    """Show the graph structure."""
    print("\n" + "=" * 60)
    print("LANGGRAPH STRUCTURE")
    print("=" * 60)

    graph = FranklinGraph()
    mermaid = graph.get_graph_visualization()
    print("\nMermaid Diagram:")
    print(mermaid)


async def demo_simple_conversation():
    """Demo a simple conversational flow."""
    print("\n" + "=" * 60)
    print("SIMPLE CONVERSATION FLOW")
    print("=" * 60)

    graph = FranklinGraph()
    user_id = str(uuid4())

    response = await graph.get_response(
        user_id=user_id,
        channel="demo",
        message="Hello! How are you today?",
    )

    print(f"\nUser: Hello! How are you today?")
    print(f"Franklin: {response}")


async def demo_tool_use():
    """Demo the graph using tools."""
    print("\n" + "=" * 60)
    print("TOOL USE FLOW")
    print("=" * 60)

    register_all_tools()
    graph = FranklinGraph()
    user_id = str(uuid4())

    # Flight search
    print("\n--- Flight Search ---")
    response = await graph.get_response(
        user_id=user_id,
        channel="demo",
        message="Search for flights from San Francisco to Tokyo on February 15th",
    )
    print(f"User: Search for flights from San Francisco to Tokyo on February 15th")
    print(f"Franklin: {response[:500]}...")

    # Account balance
    print("\n--- Account Balance ---")
    response = await graph.get_response(
        user_id=user_id,
        channel="demo",
        message="What's my account balance?",
    )
    print(f"User: What's my account balance?")
    print(f"Franklin: {response[:500]}...")

    # Stock quote
    print("\n--- Stock Quote ---")
    response = await graph.get_response(
        user_id=user_id,
        channel="demo",
        message="What's the price of Apple stock?",
    )
    print(f"User: What's the price of Apple stock?")
    print(f"Franklin: {response[:500]}...")


async def demo_approval_flow():
    """Demo the approval workflow."""
    print("\n" + "=" * 60)
    print("APPROVAL FLOW")
    print("=" * 60)

    graph = FranklinGraph()
    user_id = str(uuid4())
    conversation_id = str(uuid4())

    # Request something requiring approval
    print("\n--- Request Booking ---")
    response = await graph.get_response(
        user_id=user_id,
        channel="demo",
        message="Book me a flight to Tokyo",
        conversation_id=conversation_id,
    )
    print(f"User: Book me a flight to Tokyo")
    print(f"Franklin: {response}")


async def demo_streaming():
    """Demo streaming graph execution."""
    print("\n" + "=" * 60)
    print("STREAMING EXECUTION")
    print("=" * 60)

    register_all_tools()
    graph = FranklinGraph()
    user_id = str(uuid4())

    print("\nStreaming: 'What's the weather in Paris?'")
    print("-" * 40)

    async for event in graph.stream(
        user_id=user_id,
        channel="demo",
        message="What's the weather in Paris?",
    ):
        # Show which node produced this event
        for node_name, state_update in event.items():
            if node_name != "__end__":
                print(f"[{node_name}] → {list(state_update.keys())}")


async def demo_multi_turn():
    """Demo multi-turn conversation with checkpointing."""
    print("\n" + "=" * 60)
    print("MULTI-TURN CONVERSATION")
    print("=" * 60)

    graph = FranklinGraph()
    user_id = str(uuid4())
    conversation_id = str(uuid4())

    messages = [
        "I'm planning a trip to Japan",
        "What's the best time to visit?",
        "Search for flights in April",
    ]

    for msg in messages:
        print(f"\nUser: {msg}")
        response = await graph.get_response(
            user_id=user_id,
            channel="demo",
            message=msg,
            conversation_id=conversation_id,
        )
        print(f"Franklin: {response[:300]}...")


async def main():
    """Run all demos."""
    print("\n🤖 FRANKLIN LANGGRAPH DEMO")
    print("==========================")

    # Test imports first
    print("\nTesting imports...")
    try:
        from src.graph import FranklinGraph, AgentState
        from src.graph.nodes import parse_intent_node, agent_node
        print("✓ All LangGraph imports successful")
    except Exception as e:
        print(f"✗ Import error: {e}")
        return

    await demo_graph_visualization()
    await demo_simple_conversation()
    await demo_tool_use()
    await demo_approval_flow()
    await demo_streaming()
    await demo_multi_turn()

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)

    print("\nLangGraph Architecture:")
    print("""
    ┌─────────────────┐
    │  parse_intent   │  ← Entry point: understand user message
    └────────┬────────┘
             │
     ┌───────┴───────┐
     │               │
     ▼               ▼
  ┌──────┐    ┌───────────┐
  │agent │    │  respond  │  ← Conversation only
  └──┬───┘    └───────────┘
     │
     ├─────────────┬─────────────┐
     │             │             │
     ▼             ▼             ▼
  ┌──────┐   ┌──────────┐   ┌────────┐
  │tools │   │ approval │   │respond │
  └──┬───┘   └────┬─────┘   └────────┘
     │            │
     └────────────┤
                  ▼
            ┌──────────┐
            │ proactive│
            └────┬─────┘
                 │
                 ▼
                END
    """)

    print("\nKey features:")
    print("- StateGraph: Typed state flows between nodes")
    print("- Conditional edges: Route based on intent, tool needs, approval")
    print("- Checkpointing: Conversation memory via SQLite/Memory")
    print("- Tool binding: LangChain tools integrated with Claude")
    print("- Streaming: Real-time state updates")


if __name__ == "__main__":
    asyncio.run(main())
