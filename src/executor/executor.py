"""Executor - Runs plans with approval gates and audit trails."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID, uuid4

from src.config import get_settings
from src.executor.approval import ApprovalManager, PendingApproval, ApprovalStatus
from src.planner.planner import Plan, Step, StepStatus
from src.tools.base import Tool, ToolResult, ApprovalLevel, ToolRegistry

settings = get_settings()


@dataclass
class ExecutionResult:
    """Result of executing a plan or step."""
    id: UUID = field(default_factory=uuid4)
    success: bool = False
    data: Any = None
    error: Optional[str] = None
    summary: str = ""
    requires_approval: bool = False
    approval: Optional[PendingApproval] = None
    step_results: list[ToolResult] = field(default_factory=list)
    executed_at: datetime = field(default_factory=datetime.utcnow)

    # For conversation response
    response_message: str = ""
    options_for_user: Optional[list[dict]] = None

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "success": self.success,
            "summary": self.summary,
            "requires_approval": self.requires_approval,
            "response": self.response_message,
        }


@dataclass
class AuditEntry:
    """Audit log entry for executed actions."""
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = None
    tool: str = ""
    action: str = ""
    parameters: dict = field(default_factory=dict)
    result: str = ""  # success/failure
    error: Optional[str] = None
    approval_id: Optional[UUID] = None
    plan_id: Optional[UUID] = None
    step_id: Optional[UUID] = None
    executed_at: datetime = field(default_factory=datetime.utcnow)
    execution_time_ms: int = 0


class Executor:
    """Executes plans with approval management."""

    def __init__(self, tool_registry: ToolRegistry):
        self.tools = tool_registry
        self.approval_manager = ApprovalManager()
        self._audit_log: list[AuditEntry] = []  # In production, use database

    async def execute_plan(
        self,
        plan: Plan,
        user_id: UUID,
        channel: str = "",
    ) -> ExecutionResult:
        """Execute a plan step by step."""
        if not plan.steps:
            return ExecutionResult(
                success=True,
                summary="No actions to execute",
                response_message="",
            )

        step_results = []
        plan.status = StepStatus.IN_PROGRESS

        for step in plan.steps:
            if step.status != StepStatus.PENDING:
                continue  # Skip already processed steps

            result = await self.execute_step(step, user_id, plan.id, channel)
            step_results.append(result)

            if result.requires_approval:
                # Stop execution, wait for approval
                step.status = StepStatus.AWAITING_APPROVAL
                return ExecutionResult(
                    success=True,
                    summary=f"Awaiting approval for: {step.description}",
                    requires_approval=True,
                    approval=result.approval,
                    step_results=step_results,
                    response_message=result.approval.to_message() if result.approval else "",
                )

            if not result.success:
                step.status = StepStatus.FAILED
                step.error = result.error
                plan.status = StepStatus.FAILED
                return ExecutionResult(
                    success=False,
                    error=result.error,
                    summary=f"Failed at step: {step.description}",
                    step_results=step_results,
                    response_message=f"Sorry, I encountered an error: {result.error}",
                )

            step.status = StepStatus.COMPLETED
            step.result = result.data
            step.completed_at = datetime.utcnow()

        plan.status = StepStatus.COMPLETED

        # Compile final result
        final_summary = self._compile_summary(step_results)
        return ExecutionResult(
            success=True,
            data=[r.data for r in step_results],
            summary=final_summary,
            step_results=step_results,
            response_message=final_summary,
            options_for_user=step_results[-1].options if step_results else None,
        )

    async def execute_step(
        self,
        step: Step,
        user_id: UUID,
        plan_id: Optional[UUID] = None,
        channel: str = "",
    ) -> ExecutionResult:
        """Execute a single step."""
        step.status = StepStatus.IN_PROGRESS
        step.started_at = datetime.utcnow()

        # Get the tool
        tool = self.tools.get(step.tool)
        if not tool:
            return ExecutionResult(
                success=False,
                error=f"Tool not found: {step.tool}",
            )

        # Check approval level
        approval_level = tool.get_approval_level(step.action)

        # Also check step-level override
        if step.approval_level.value > approval_level.value:
            approval_level = step.approval_level

        if approval_level in (ApprovalLevel.CONFIRM, ApprovalLevel.STRICT):
            # Need approval
            approval = await self.approval_manager.create_approval(
                user_id=user_id,
                tool=step.tool,
                action=step.action,
                description=step.description,
                parameters=step.parameters,
                plan_id=plan_id,
                step_id=step.id,
                channel=channel,
            )

            return ExecutionResult(
                success=True,
                requires_approval=True,
                approval=approval,
                summary=f"Approval required: {step.description}",
            )

        # Execute the action
        start_time = datetime.utcnow()
        try:
            result = await tool.execute(step.action, step.parameters, user_id)

            # Audit log
            self._audit(
                user_id=user_id,
                tool=step.tool,
                action=step.action,
                parameters=step.parameters,
                result="success" if result.success else "failure",
                error=result.error,
                plan_id=plan_id,
                step_id=step.id,
                execution_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
            )

            if approval_level == ApprovalLevel.NOTIFY:
                # Execute but notify
                result.metadata["notification_sent"] = True

            return ExecutionResult(
                success=result.success,
                data=result.data,
                error=result.error,
                summary=result.summary or "",
                response_message=result.summary or "",
                options_for_user=result.options,
            )

        except Exception as e:
            self._audit(
                user_id=user_id,
                tool=step.tool,
                action=step.action,
                parameters=step.parameters,
                result="error",
                error=str(e),
                plan_id=plan_id,
                step_id=step.id,
                execution_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
            )

            return ExecutionResult(
                success=False,
                error=str(e),
                summary=f"Error executing {step.action}: {str(e)}",
            )

    async def resume_after_approval(
        self,
        approval: PendingApproval,
        plan: Plan,
        user_id: UUID,
        channel: str = "",
    ) -> ExecutionResult:
        """Resume plan execution after approval."""
        if approval.status != ApprovalStatus.APPROVED:
            return ExecutionResult(
                success=False,
                error="Action was not approved",
                response_message="Action cancelled.",
            )

        # Find the step that was waiting
        step = None
        for s in plan.steps:
            if s.id == approval.step_id:
                step = s
                break

        if not step:
            return ExecutionResult(
                success=False,
                error="Could not find pending step",
            )

        # Get the tool and execute
        tool = self.tools.get(step.tool)
        if not tool:
            return ExecutionResult(
                success=False,
                error=f"Tool not found: {step.tool}",
            )

        # If there were options, use selected one
        if approval.selected_option is not None and approval.options:
            selected = approval.options[approval.selected_option]
            # Merge selected option into parameters
            if isinstance(selected, dict):
                step.parameters.update(selected.get("params", {}))

        # Execute
        try:
            result = await tool.execute(step.action, step.parameters, user_id)

            step.status = StepStatus.COMPLETED
            step.result = result.data
            step.completed_at = datetime.utcnow()

            self._audit(
                user_id=user_id,
                tool=step.tool,
                action=step.action,
                parameters=step.parameters,
                result="success" if result.success else "failure",
                error=result.error,
                approval_id=approval.id,
                plan_id=plan.id,
                step_id=step.id,
            )

            if result.success:
                # Continue with remaining steps
                return await self.execute_plan(plan, user_id, channel)
            else:
                return ExecutionResult(
                    success=False,
                    error=result.error,
                    response_message=f"Action failed: {result.error}",
                )

        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e),
                response_message=f"Error: {str(e)}",
            )

    def _audit(
        self,
        user_id: UUID,
        tool: str,
        action: str,
        parameters: dict,
        result: str,
        error: Optional[str] = None,
        approval_id: Optional[UUID] = None,
        plan_id: Optional[UUID] = None,
        step_id: Optional[UUID] = None,
        execution_time_ms: int = 0,
    ) -> None:
        """Add an audit log entry."""
        entry = AuditEntry(
            user_id=user_id,
            tool=tool,
            action=action,
            parameters=parameters,
            result=result,
            error=error,
            approval_id=approval_id,
            plan_id=plan_id,
            step_id=step_id,
            execution_time_ms=execution_time_ms,
        )
        self._audit_log.append(entry)
        # In production, save to database

    def _compile_summary(self, results: list) -> str:
        """Compile a summary from multiple results."""
        summaries = []
        for r in results:
            if hasattr(r, 'summary') and r.summary:
                summaries.append(r.summary)
        return " → ".join(summaries) if summaries else "Actions completed"

    def get_audit_log(self, user_id: UUID, limit: int = 50) -> list[AuditEntry]:
        """Get audit log for a user."""
        user_entries = [e for e in self._audit_log if e.user_id == user_id]
        return sorted(user_entries, key=lambda e: e.executed_at, reverse=True)[:limit]
