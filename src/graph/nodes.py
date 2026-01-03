"""Node functions for Franklin's LangGraph agent."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_anthropic import ChatAnthropic

from src.config import get_settings
from src.graph.state import AgentState, ApprovalStatus, get_last_human_message
from src.graph.tools import get_langchain_tools, execute_tool, APPROVAL_REQUIRED_TOOLS
from src.persona import PERSONA_BACKGROUND
from src.proactive import ProactiveEngine, UserContext

settings = get_settings()

# Initialize LLM
llm = ChatAnthropic(
    model=settings.default_llm_model,
    api_key=settings.anthropic_api_key,
    temperature=0.7,
    max_tokens=2048,
)

# LLM with tools bound
tools = get_langchain_tools()
llm_with_tools = llm.bind_tools(tools)

# Proactive engine
proactive_engine = ProactiveEngine()


# ============================================================
# SYSTEM PROMPTS
# ============================================================

FRANKLIN_SYSTEM = f"""{PERSONA_BACKGROUND}

You are Franklin, a personal AI assistant with the ability to take actions on behalf of the user.

CAPABILITIES:
- Search and book flights (booking requires approval)
- Manage calendar and schedule events (modifications require approval)
- Draft and send emails (sending requires approval)
- View financial accounts and transactions
- Prepare tax documents (submission requires strict approval)
- Research information, weather, stock prices

IMPORTANT RULES:
1. For read-only operations (search, view, lookup), execute immediately
2. For write operations (book, send, create, delete), always request approval first
3. Be concise and action-oriented - you're here to get things done
4. If you need more information, ask the user directly
5. When presenting options (flights, times, etc.), format them clearly

When using tools, always explain what you're doing and present results clearly.
"""


# ============================================================
# NODE FUNCTIONS
# ============================================================

async def parse_intent_node(state: AgentState) -> dict:
    """
    Parse the user's message to understand intent.

    This node analyzes the message and determines:
    - Is this actionable? (needs tools)
    - Is this a response to pending approval?
    - Is this just conversation?
    """
    message = get_last_human_message(state)
    if not message:
        return {"next_action": "respond", "should_respond": True}

    # Check if this is an approval response
    message_lower = message.lower().strip()
    if state.get("approval_status") == ApprovalStatus.PENDING.value:
        if message_lower in ("approve", "yes", "ok", "confirm", "y", "proceed"):
            return {
                "approval_status": ApprovalStatus.APPROVED.value,
                "approval_response": "approved",
                "next_action": "execute_approved",
            }
        elif message_lower in ("cancel", "no", "reject", "n", "stop", "abort"):
            return {
                "approval_status": ApprovalStatus.REJECTED.value,
                "approval_response": "rejected",
                "next_action": "respond",
                "final_response": "Understood, I've cancelled that action.",
                "should_respond": True,
            }
        elif message_lower.isdigit():
            # User selected an option by number
            return {
                "approval_status": ApprovalStatus.APPROVED.value,
                "approval_response": f"option_{message_lower}",
                "next_action": "execute_approved",
            }

    # Use LLM to determine if this needs tools
    intent_prompt = f"""Analyze this user message and determine the intent:

Message: "{message}"

Respond with JSON:
{{
    "needs_action": true/false,  // Does this require using tools?
    "category": "travel|calendar|finance|email|research|conversation",
    "action": "brief description of what user wants",
    "confidence": 0.0-1.0
}}

Only set needs_action=true if the user is asking you to DO something (search, book, schedule, send, etc.)
Set needs_action=false for questions, greetings, or general conversation."""

    response = await llm.ainvoke([
        SystemMessage(content="You are an intent classifier. Respond only with valid JSON."),
        HumanMessage(content=intent_prompt),
    ])

    try:
        # Parse JSON from response
        content = response.content
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()
        intent = json.loads(content)
    except (json.JSONDecodeError, IndexError):
        intent = {"needs_action": False, "category": "conversation", "confidence": 0.5}

    if intent.get("needs_action") and intent.get("confidence", 0) > 0.5:
        return {
            "intent": intent,
            "next_action": "agent",
        }
    else:
        return {
            "intent": intent,
            "next_action": "respond",
            "should_respond": True,
        }


async def agent_node(state: AgentState) -> dict:
    """
    Main agent node - uses LLM with tools to handle requests.

    This is the ReAct-style agent that decides what tools to call.
    """
    messages = [SystemMessage(content=FRANKLIN_SYSTEM)] + list(state["messages"])

    response = await llm_with_tools.ainvoke(messages)

    # Check if there are tool calls
    if response.tool_calls:
        tool_calls = []
        for tc in response.tool_calls:
            tool_calls.append({
                "id": tc["id"],
                "name": tc["name"],
                "args": tc["args"],
            })

        # Check if any tool requires approval
        needs_approval = any(tc["name"] in APPROVAL_REQUIRED_TOOLS for tc in tool_calls)

        if needs_approval:
            # Find the tool that needs approval
            approval_tool = next(tc for tc in tool_calls if tc["name"] in APPROVAL_REQUIRED_TOOLS)
            return {
                "messages": [response],
                "tool_calls": tool_calls,
                "next_action": "request_approval",
                "pending_approval": {
                    "tool": approval_tool["name"],
                    "args": approval_tool["args"],
                    "description": f"Execute {approval_tool['name']}",
                },
            }
        else:
            return {
                "messages": [response],
                "tool_calls": tool_calls,
                "next_action": "execute_tools",
            }
    else:
        # No tool calls - just a response
        return {
            "messages": [response],
            "next_action": "respond",
            "should_respond": True,
            "final_response": response.content,
        }


async def execute_tools_node(state: AgentState) -> dict:
    """
    Execute tool calls and return results.
    """
    tool_calls = state.get("tool_calls", [])
    if not tool_calls:
        return {"next_action": "agent"}

    tool_results = []
    tool_messages = []

    for tc in tool_calls:
        # Add user_id to args
        args = tc["args"].copy()
        args["_user_id"] = state["user_id"]

        # Execute the tool
        result = await execute_tool(
            tool_name=tc["name"].split("_")[0] if "_" in tc["name"] else "research",
            action=tc["name"],
            params=args,
            user_id=state["user_id"],
        )

        tool_results.append({
            "tool": tc["name"],
            "result": result,
        })

        # Create tool message
        tool_messages.append(ToolMessage(
            content=json.dumps(result),
            tool_call_id=tc["id"],
        ))

    return {
        "messages": tool_messages,
        "tool_results": tool_results,
        "tool_calls": [],  # Clear pending calls
        "next_action": "agent",  # Go back to agent to process results
    }


async def request_approval_node(state: AgentState) -> dict:
    """
    Request user approval for a sensitive action.
    """
    pending = state.get("pending_approval", {})
    if not pending:
        return {"next_action": "agent"}

    tool_name = pending.get("tool", "action")
    args = pending.get("args", {})

    # Format approval message
    approval_msg = f"""**Approval Required**

I'd like to execute: **{tool_name}**

"""
    if args:
        approval_msg += "Details:\n"
        for key, value in args.items():
            if not key.startswith("_"):
                approval_msg += f"- {key}: {value}\n"

    approval_msg += "\nReply **'approve'** to proceed or **'cancel'** to abort."

    return {
        "approval_status": ApprovalStatus.PENDING.value,
        "next_action": "respond",
        "should_respond": True,
        "final_response": approval_msg,
    }


async def execute_approved_node(state: AgentState) -> dict:
    """
    Execute a previously approved action.
    """
    pending = state.get("pending_approval", {})
    if not pending:
        return {"next_action": "respond", "final_response": "Nothing to execute."}

    tool_name = pending.get("tool", "")
    args = pending.get("args", {})
    args["_user_id"] = state["user_id"]

    # Handle option selection
    approval_response = state.get("approval_response", "")
    if approval_response.startswith("option_"):
        option_num = int(approval_response.split("_")[1])
        # Would need to map option to specific selection
        args["selected_option"] = option_num

    # Execute the tool
    result = await execute_tool(
        tool_name=tool_name.split("_")[0] if "_" in tool_name else tool_name,
        action=tool_name,
        params=args,
        user_id=state["user_id"],
    )

    if result.get("success"):
        response = f"Done! {result.get('summary', 'Action completed successfully.')}"
    else:
        response = f"Sorry, that didn't work: {result.get('error', 'Unknown error')}"

    return {
        "tool_results": [{"tool": tool_name, "result": result}],
        "approval_status": ApprovalStatus.NONE.value,
        "pending_approval": None,
        "next_action": "respond",
        "should_respond": True,
        "final_response": response,
    }


async def respond_node(state: AgentState) -> dict:
    """
    Generate final response to user.
    """
    # If we already have a final response, use it
    if state.get("final_response"):
        return {
            "messages": [AIMessage(content=state["final_response"])],
            "completed_at": datetime.utcnow().isoformat(),
        }

    # Otherwise, generate a conversational response
    messages = [SystemMessage(content=FRANKLIN_SYSTEM)] + list(state["messages"])

    response = await llm.ainvoke(messages)

    return {
        "messages": [response],
        "final_response": response.content,
        "completed_at": datetime.utcnow().isoformat(),
    }


async def check_proactive_node(state: AgentState) -> dict:
    """
    Check for proactive notifications to include.
    """
    user_id_str = state["user_id"]

    try:
        from uuid import UUID
        user_id = UUID(user_id_str)

        # Build context
        context = UserContext(
            user_id=user_id,
            settings=state.get("user_profile", {}).get("settings", {}),
        )

        # Check triggers
        notifications = await proactive_engine.check_triggers(user_id, context)

        if notifications:
            proactive_list = []
            for n in notifications[:2]:  # Max 2 notifications
                proactive_list.append({
                    "message": n.message,
                    "type": n.action_type.value,
                    "priority": n.priority,
                })
            return {"proactive_notifications": proactive_list}

    except Exception:
        pass  # Don't fail for proactive errors

    return {"proactive_notifications": []}


# ============================================================
# ROUTING FUNCTIONS
# ============================================================

def route_after_intent(state: AgentState) -> Literal["agent", "respond", "execute_approved"]:
    """Route based on intent parsing result."""
    return state.get("next_action", "respond")


def route_after_agent(state: AgentState) -> Literal["execute_tools", "request_approval", "respond"]:
    """Route based on agent decision."""
    return state.get("next_action", "respond")


def route_after_tools(state: AgentState) -> Literal["agent", "respond"]:
    """Route after tool execution."""
    return state.get("next_action", "agent")


def should_continue(state: AgentState) -> Literal["continue", "end"]:
    """Determine if we should continue the graph or end."""
    if state.get("should_respond") or state.get("final_response"):
        return "end"
    return "continue"
