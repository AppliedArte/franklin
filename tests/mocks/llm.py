"""Mock LLM clients for testing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from unittest.mock import MagicMock, AsyncMock


@dataclass
class MockMessage:
    """Mock LLM message response."""
    content: str
    tool_calls: list[dict] = field(default_factory=list)
    role: str = "assistant"


@dataclass
class MockToolCall:
    """Mock tool call from LLM."""
    id: str
    name: str
    args: dict


class MockLLM:
    """Mock LLM for testing agent behavior."""

    def __init__(self, responses: Optional[list[str | dict]] = None):
        self._responses = responses or ["I understand. How can I help you?"]
        self._call_index = 0
        self._calls = []

    async def ainvoke(self, messages: list) -> MockMessage:
        """Mock async invoke."""
        self._calls.append(messages)
        response = self._get_next_response()
        return response

    def invoke(self, messages: list) -> MockMessage:
        """Mock sync invoke."""
        self._calls.append(messages)
        return self._get_next_response()

    def _get_next_response(self) -> MockMessage:
        """Get the next configured response."""
        if self._call_index >= len(self._responses):
            response = self._responses[-1]  # Repeat last response
        else:
            response = self._responses[self._call_index]
            self._call_index += 1

        if isinstance(response, str):
            return MockMessage(content=response)
        elif isinstance(response, dict):
            return MockMessage(
                content=response.get("content", ""),
                tool_calls=response.get("tool_calls", []),
            )
        return response

    def bind_tools(self, tools: list) -> "MockLLM":
        """Mock bind_tools - returns self for chaining."""
        return self

    @property
    def calls(self) -> list:
        """Get all recorded calls."""
        return self._calls

    def reset(self):
        """Reset call tracking."""
        self._call_index = 0
        self._calls.clear()


class MockAnthropicClient:
    """Mock Anthropic client for testing."""

    def __init__(self, responses: Optional[list[str | dict]] = None):
        self.messages = MockAnthropicMessages(responses)


class MockAnthropicMessages:
    """Mock Anthropic messages API."""

    def __init__(self, responses: Optional[list[str | dict]] = None):
        self._responses = responses or [{"role": "assistant", "content": "Hello!"}]
        self._call_index = 0
        self._calls = []

    def create(self, **kwargs) -> dict:
        """Mock create message."""
        self._calls.append(kwargs)
        return self._get_next_response()

    async def acreate(self, **kwargs) -> dict:
        """Mock async create message."""
        self._calls.append(kwargs)
        return self._get_next_response()

    def _get_next_response(self) -> dict:
        """Get the next configured response."""
        if self._call_index >= len(self._responses):
            response = self._responses[-1]
        else:
            response = self._responses[self._call_index]
            self._call_index += 1

        if isinstance(response, str):
            return {
                "id": "msg_mock",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": response}],
                "model": "claude-sonnet-4-20250514",
                "stop_reason": "end_turn",
            }
        return response

    @property
    def calls(self) -> list:
        """Get all recorded calls."""
        return self._calls


def create_intent_response(
    needs_action: bool = True,
    category: str = "calendar",
    action: str = "list events",
    confidence: float = 0.95,
) -> str:
    """Create a mock intent classification response."""
    import json
    return json.dumps({
        "needs_action": needs_action,
        "category": category,
        "action": action,
        "confidence": confidence,
    })


def create_tool_call_response(
    tool_name: str,
    tool_args: dict,
    tool_id: str = "call_mock",
) -> dict:
    """Create a mock response with tool calls."""
    return {
        "content": "",
        "tool_calls": [{
            "id": tool_id,
            "name": tool_name,
            "args": tool_args,
        }],
    }
