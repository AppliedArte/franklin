"""Base Tool class and core abstractions for Franklin's action system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4


class ToolCategory(str, Enum):
    """Categories of tools for organization and permissions."""
    TRAVEL = "travel"
    FINANCE = "finance"
    CALENDAR = "calendar"
    EMAIL = "email"
    DOCUMENTS = "documents"
    RESEARCH = "research"
    COMMUNICATION = "communication"


class ApprovalLevel(str, Enum):
    """Levels of approval required for actions."""
    NONE = "none"  # Auto-approve (read-only operations)
    NOTIFY = "notify"  # Execute but notify user
    CONFIRM = "confirm"  # Require explicit approval
    STRICT = "strict"  # Require approval + verification code


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    # For UI presentation
    summary: Optional[str] = None  # Human-readable summary
    options: Optional[list[dict]] = None  # Choices for user to pick from

    # For audit
    execution_id: UUID = field(default_factory=uuid4)
    executed_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.summary is None and self.success:
            self.summary = "Action completed successfully"
        elif self.summary is None and not self.success:
            self.summary = self.error or "Action failed"


@dataclass
class ApprovalRequired:
    """Raised when an action requires user approval."""
    action: str
    tool_name: str
    description: str
    estimated_cost: Optional[Decimal] = None
    options: Optional[list[dict]] = None
    expires_at: Optional[datetime] = None
    approval_id: UUID = field(default_factory=uuid4)

    def to_message(self) -> str:
        """Format as a message for the user."""
        msg = f"**Approval Required**\n\n"
        msg += f"Action: {self.description}\n"
        if self.estimated_cost:
            msg += f"Estimated cost: ${self.estimated_cost:.2f}\n"
        if self.options:
            msg += "\nOptions:\n"
            for i, opt in enumerate(self.options, 1):
                msg += f"{i}. {opt.get('label', opt)}\n"
        msg += f"\nReply 'approve' to proceed or 'cancel' to abort."
        return msg


@dataclass
class ToolAction:
    """Definition of a single action a tool can perform."""
    name: str
    description: str
    parameters: dict[str, dict]  # JSON Schema style
    approval_level: ApprovalLevel = ApprovalLevel.NONE
    cost_estimate: Optional[Decimal] = None  # If action has a cost

    def to_schema(self) -> dict:
        """Convert to Claude tool schema format."""
        return {
            "name": f"{self.name}",
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.parameters,
                "required": [k for k, v in self.parameters.items() if v.get("required", False)]
            }
        }


class Tool(ABC):
    """Base class for all Franklin tools."""

    name: str = "base_tool"
    description: str = "Base tool"
    category: ToolCategory = ToolCategory.RESEARCH
    version: str = "1.0.0"

    # Default approval settings
    default_approval_level: ApprovalLevel = ApprovalLevel.NONE
    cost_threshold_auto: Decimal = Decimal("0")  # Auto-approve under this
    cost_threshold_notify: Decimal = Decimal("50")  # Notify under this, confirm above

    # Authentication
    requires_auth: bool = False
    auth_type: Optional[str] = None  # "oauth2", "api_key", "credentials"

    def __init__(self):
        self._actions: dict[str, ToolAction] = {}
        self._register_actions()

    @abstractmethod
    def _register_actions(self) -> None:
        """Register all actions this tool supports."""
        pass

    @abstractmethod
    async def execute(self, action: str, params: dict, user_id: UUID) -> ToolResult:
        """Execute an action with given parameters."""
        pass

    async def check_auth(self, user_id: UUID) -> bool:
        """Check if user has authenticated with this tool."""
        if not self.requires_auth:
            return True
        # Override in subclass to check user's credentials
        return False

    def get_actions(self) -> list[ToolAction]:
        """Get all registered actions."""
        return list(self._actions.values())

    def get_action(self, name: str) -> Optional[ToolAction]:
        """Get a specific action by name."""
        return self._actions.get(name)

    def register_action(self, action: ToolAction) -> None:
        """Register an action."""
        self._actions[action.name] = action

    def get_approval_level(self, action: str, estimated_cost: Optional[Decimal] = None) -> ApprovalLevel:
        """Determine approval level for an action."""
        tool_action = self.get_action(action)
        if tool_action:
            base_level = tool_action.approval_level
        else:
            base_level = self.default_approval_level

        # Escalate based on cost if applicable
        if estimated_cost:
            if estimated_cost > self.cost_threshold_notify:
                return ApprovalLevel.CONFIRM
            elif estimated_cost > self.cost_threshold_auto:
                return max(base_level, ApprovalLevel.NOTIFY, key=lambda x: list(ApprovalLevel).index(x))

        return base_level

    def to_claude_tools(self) -> list[dict]:
        """Convert all actions to Claude tool format."""
        tools = []
        for action in self.get_actions():
            schema = action.to_schema()
            schema["name"] = f"{self.name}__{action.name}"  # Namespace it
            tools.append(schema)
        return tools

    def __repr__(self) -> str:
        return f"<Tool {self.name} v{self.version}>"


class ToolRegistry:
    """Registry for discovering and accessing tools."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    def list_by_category(self, category: ToolCategory) -> list[Tool]:
        """List tools in a category."""
        return [t for t in self._tools.values() if t.category == category]

    def get_all_claude_tools(self) -> list[dict]:
        """Get all tools in Claude format."""
        tools = []
        for tool in self._tools.values():
            tools.extend(tool.to_claude_tools())
        return tools

    def parse_tool_call(self, tool_name: str) -> tuple[Optional[str], Optional[str]]:
        """Parse a namespaced tool call into (tool_name, action_name)."""
        if "__" in tool_name:
            parts = tool_name.split("__", 1)
            return parts[0], parts[1]
        return tool_name, None
