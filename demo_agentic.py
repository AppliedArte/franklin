#!/usr/bin/env python3
"""Demo script for Franklin's agentic capabilities.

Run with: python demo_agentic.py
"""

import asyncio
from uuid import uuid4

from src.planner import IntentParser, Planner
from src.executor import Executor
from src.tools.registry import registry, register_all_tools
from src.proactive import ProactiveEngine, UserContext


async def demo_intent_parsing():
    """Demo intent parsing."""
    print("\n" + "=" * 60)
    print("INTENT PARSING DEMO")
    print("=" * 60)

    parser = IntentParser()

    test_messages = [
        "Book me a flight to Tokyo next month",
        "What's my checking account balance?",
        "Schedule a meeting with John tomorrow at 2pm",
        "How's the weather in Paris?",
        "Hello, how are you?",
        "Submit my tax return",
        "Search for flights from SFO to NYC on January 15th",
    ]

    for msg in test_messages:
        print(f"\n> '{msg}'")
        intent = await parser.parse(msg)
        print(f"  Category: {intent.category.value}")
        print(f"  Action: {intent.action}")
        print(f"  Params: {intent.parameters}")
        print(f"  Confidence: {intent.confidence:.2f}")
        if intent.requires_clarification:
            print(f"  Needs clarification: {intent.clarification_questions}")


async def demo_tool_execution():
    """Demo tool execution."""
    print("\n" + "=" * 60)
    print("TOOL EXECUTION DEMO")
    print("=" * 60)

    # Register tools
    register_all_tools()

    user_id = uuid4()

    # Demo travel search
    print("\n--- Flight Search ---")
    travel_tool = registry.get("travel")
    result = await travel_tool.execute(
        "search_flights",
        {
            "origin": "SFO",
            "destination": "NRT",
            "departure_date": "2024-02-15",
        },
        user_id,
    )
    print(f"Success: {result.success}")
    print(f"Summary: {result.summary}")
    if result.options:
        print("Options:")
        for opt in result.options[:3]:
            print(f"  - {opt}")

    # Demo finance
    print("\n--- Account Balance ---")
    finance_tool = registry.get("finance")
    result = await finance_tool.execute("list_accounts", {}, user_id)
    print(f"Summary: {result.summary}")

    # Demo research
    print("\n--- Stock Quote ---")
    research_tool = registry.get("research")
    result = await research_tool.execute(
        "stock_quote", {"symbol": "AAPL"}, user_id
    )
    print(f"Summary: {result.summary}")


async def demo_planning():
    """Demo task planning."""
    print("\n" + "=" * 60)
    print("PLANNING DEMO")
    print("=" * 60)

    parser = IntentParser()
    planner = Planner()

    # Parse an intent
    msg = "Book me a flight to Tokyo for my trip next month"
    print(f"\n> '{msg}'")

    intent = await parser.parse(msg)
    print(f"Intent: {intent.category.value} - {intent.action}")

    # Create a plan
    plan = await planner.create_plan(intent)
    print(f"\nPlan: {plan.description}")
    print(f"Steps:")
    for step in plan.steps:
        approval = f" [APPROVAL: {step.approval_level.value}]" if step.approval_level.value != "none" else ""
        print(f"  {step.order}. {step.tool}.{step.action}{approval}")
        print(f"     {step.description}")


async def demo_proactive():
    """Demo proactive notifications."""
    print("\n" + "=" * 60)
    print("PROACTIVE ENGINE DEMO")
    print("=" * 60)

    engine = ProactiveEngine()
    user_id = uuid4()

    # Enable defaults
    engine.enable_all_defaults(user_id)
    print(f"Enabled {len(engine.get_user_rules(user_id))} rules for user")

    # Simulate context with upcoming trip
    context = UserContext(
        user_id=user_id,
        calendar_events=[
            {
                "title": "Tokyo Trip",
                "start": "2024-02-01T10:00:00",
                "location": "Tokyo, Japan",
            }
        ],
        accounts=[
            {"name": "Checking", "type": "checking", "balance": 350},  # Below threshold
        ],
        settings={
            "low_balance_threshold": 500,
        },
    )

    # Check triggers
    notifications = await engine.check_triggers(user_id, context)

    if notifications:
        print(f"\nTriggered {len(notifications)} notification(s):")
        for n in notifications:
            print(f"  [{n.action_type.value}] {n.message}")
    else:
        print("\nNo notifications triggered")


async def demo_full_flow():
    """Demo the full agentic flow."""
    print("\n" + "=" * 60)
    print("FULL AGENTIC FLOW DEMO")
    print("=" * 60)

    # Initialize components
    register_all_tools()
    parser = IntentParser()
    planner = Planner()
    executor = Executor(registry)

    user_id = uuid4()

    # User request
    msg = "Search for flights from San Francisco to Tokyo on February 15th"
    print(f"\nUser: {msg}")

    # 1. Parse intent
    intent = await parser.parse(msg)
    print(f"\n[Intent] {intent.category.value}: {intent.action}")

    # 2. Create plan
    plan = await planner.create_plan(intent)
    print(f"[Plan] {plan.description} ({len(plan.steps)} steps)")

    # 3. Execute plan
    result = await executor.execute_plan(plan, user_id, "demo")

    if result.requires_approval:
        print(f"\n[Approval Required]")
        print(result.approval.to_message() if result.approval else "")
    else:
        print(f"\n[Result] {result.summary}")
        if result.options_for_user:
            print("\nOptions:")
            for i, opt in enumerate(result.options_for_user[:3], 1):
                if isinstance(opt, dict):
                    print(f"  {i}. {opt.get('route', '')} - {opt.get('price', '')}")


async def main():
    """Run all demos."""
    print("\n🤖 FRANKLIN AGENTIC SYSTEM DEMO")
    print("================================")

    await demo_intent_parsing()
    await demo_tool_execution()
    await demo_planning()
    await demo_proactive()
    await demo_full_flow()

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Set up API keys in .env (Amadeus, Plaid, Google Calendar)")
    print("2. Use AgenticOrchestrator instead of ConversationOrchestrator")
    print("3. Enable proactive triggers for your users")
    print("4. Monitor approval requests via get_pending_approvals()")


if __name__ == "__main__":
    asyncio.run(main())
