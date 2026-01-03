"""Planner - Creates execution plans from intents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from anthropic import AsyncAnthropic

from src.config import get_settings
from src.planner.intent import Intent, IntentCategory
from src.tools.base import ApprovalLevel

settings = get_settings()


class StepStatus(str, Enum):
    """Status of a plan step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Step:
    """A single step in an execution plan."""
    id: UUID = field(default_factory=uuid4)
    order: int = 0
    tool: str = ""
    action: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    depends_on: list[UUID] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    approval_level: ApprovalLevel = ApprovalLevel.NONE
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "order": self.order,
            "tool": self.tool,
            "action": self.action,
            "parameters": self.parameters,
            "description": self.description,
            "status": self.status.value,
            "approval_level": self.approval_level.value,
        }


@dataclass
class Plan:
    """An execution plan composed of steps."""
    id: UUID = field(default_factory=uuid4)
    intent: Optional[Intent] = None
    steps: list[Step] = field(default_factory=list)
    description: str = ""
    status: StepStatus = StepStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    user_message: str = ""

    @property
    def current_step(self) -> Optional[Step]:
        """Get the current step to execute."""
        for step in self.steps:
            if step.status in (StepStatus.PENDING, StepStatus.IN_PROGRESS, StepStatus.AWAITING_APPROVAL):
                return step
        return None

    @property
    def is_complete(self) -> bool:
        """Check if plan is complete."""
        return all(s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED) for s in self.steps)

    @property
    def has_failed(self) -> bool:
        """Check if plan has failed."""
        return any(s.status == StepStatus.FAILED for s in self.steps)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "description": self.description,
            "status": self.status.value,
            "steps": [s.to_dict() for s in self.steps],
            "is_complete": self.is_complete,
        }


# Planning prompt
PLANNING_SYSTEM_PROMPT = """You are a task planner for Franklin, a personal AI assistant.

Given a user intent and available tools, create an execution plan.

Available tools and their actions:
- travel: search_flights, book_flight, get_itinerary, cancel_booking
- calendar: list_events, find_free_time, create_event, update_event, delete_event
- email: draft, send, search, read, reply
- finance: list_accounts, get_transactions, spending_summary, tax_summary, estimate_taxes, prepare_tax_documents, submit_tax_return, schedule_payment
- research: web_search, price_lookup, weather, stock_quote, currency_convert

Create a plan with steps that:
1. Gather any needed information first (read-only operations)
2. Present options to user when appropriate
3. Execute actions that modify data last
4. Respect approval requirements (booking, payments, sending emails need approval)

Respond with valid JSON:
{
    "description": "Brief plan description",
    "steps": [
        {
            "order": 1,
            "tool": "tool_name",
            "action": "action_name",
            "parameters": {"key": "value"},
            "description": "What this step does",
            "depends_on": [],
            "needs_approval": false
        }
    ]
}

Keep plans focused and minimal. Don't over-engineer."""


class Planner:
    """Creates execution plans from intents."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.default_llm_model

    async def create_plan(self, intent: Intent, user_context: Optional[dict] = None) -> Plan:
        """Create an execution plan from an intent."""
        import json

        # For simple conversation intents, return empty plan
        if intent.category == IntentCategory.CONVERSATION:
            return Plan(
                intent=intent,
                description="Conversational response",
                steps=[],
                user_message=intent.raw_message,
            )

        # Build the planning prompt
        user_prompt = f"""
Intent: {intent.category.value} - {intent.action}
Parameters: {json.dumps(intent.parameters)}
Original message: {intent.raw_message}
"""
        if user_context:
            user_prompt += f"\nUser context: {json.dumps(user_context)}"

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.2,
                system=PLANNING_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )

            response_text = response.content[0].text.strip()

            # Handle markdown code blocks
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            parsed = json.loads(response_text)

            # Convert to Plan with Steps
            steps = []
            for step_data in parsed.get("steps", []):
                step = Step(
                    order=step_data.get("order", len(steps) + 1),
                    tool=step_data.get("tool", ""),
                    action=step_data.get("action", ""),
                    parameters=step_data.get("parameters", {}),
                    description=step_data.get("description", ""),
                    approval_level=ApprovalLevel.CONFIRM if step_data.get("needs_approval") else ApprovalLevel.NONE,
                )
                steps.append(step)

            # Set up dependencies (each step depends on previous)
            for i, step in enumerate(steps):
                if i > 0 and not step.depends_on:
                    step.depends_on = [steps[i - 1].id]

            return Plan(
                intent=intent,
                steps=steps,
                description=parsed.get("description", ""),
                user_message=intent.raw_message,
            )

        except json.JSONDecodeError:
            # Return a simple single-step plan
            return self._create_fallback_plan(intent)
        except Exception as e:
            return Plan(
                intent=intent,
                description=f"Planning failed: {str(e)}",
                steps=[],
                status=StepStatus.FAILED,
                user_message=intent.raw_message,
            )

    def _create_fallback_plan(self, intent: Intent) -> Plan:
        """Create a simple fallback plan from intent."""
        # Map categories to tools
        category_to_tool = {
            IntentCategory.TRAVEL: "travel",
            IntentCategory.FINANCE: "finance",
            IntentCategory.CALENDAR: "calendar",
            IntentCategory.EMAIL: "email",
            IntentCategory.RESEARCH: "research",
        }

        tool = category_to_tool.get(intent.category, "research")

        step = Step(
            order=1,
            tool=tool,
            action=intent.action,
            parameters=intent.parameters,
            description=f"Execute {intent.action}",
        )

        return Plan(
            intent=intent,
            steps=[step],
            description=f"Execute {intent.category.value} action",
            user_message=intent.raw_message,
        )

    async def replan(self, plan: Plan, feedback: str) -> Plan:
        """Replan based on execution feedback."""
        import json

        # Find remaining steps
        remaining_steps = [s for s in plan.steps if s.status == StepStatus.PENDING]

        if not remaining_steps:
            return plan

        user_prompt = f"""
Original plan: {plan.description}
Completed steps: {[s.description for s in plan.steps if s.status == StepStatus.COMPLETED]}
Feedback: {feedback}
Original message: {plan.user_message}

Adjust the remaining plan based on this feedback.
"""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.2,
                system=PLANNING_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )

            response_text = response.content[0].text.strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            parsed = json.loads(response_text)

            # Update remaining steps
            new_steps = []
            for step_data in parsed.get("steps", []):
                step = Step(
                    order=step_data.get("order", len(new_steps) + 1),
                    tool=step_data.get("tool", ""),
                    action=step_data.get("action", ""),
                    parameters=step_data.get("parameters", {}),
                    description=step_data.get("description", ""),
                    approval_level=ApprovalLevel.CONFIRM if step_data.get("needs_approval") else ApprovalLevel.NONE,
                )
                new_steps.append(step)

            # Keep completed steps, replace remaining with new
            completed = [s for s in plan.steps if s.status == StepStatus.COMPLETED]
            plan.steps = completed + new_steps
            plan.description = parsed.get("description", plan.description)

            return plan

        except Exception:
            return plan  # Keep original plan on error
