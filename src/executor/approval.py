"""Approval management for actions requiring user confirmation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4


class ApprovalStatus(str, Enum):
    """Status of an approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class PendingApproval:
    """A pending approval request."""
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = None
    tool: str = ""
    action: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    estimated_cost: Optional[Decimal] = None
    options: Optional[list[dict]] = None  # If user needs to choose
    selected_option: Optional[int] = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    resolved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    # For audit
    plan_id: Optional[UUID] = None
    step_id: Optional[UUID] = None
    channel: str = ""  # whatsapp, telegram, web, etc.

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at and self.status == ApprovalStatus.PENDING

    def to_message(self) -> str:
        """Format as a user-facing message."""
        msg = f"**Action Approval Required**\n\n"
        msg += f"{self.description}\n\n"

        if self.estimated_cost:
            msg += f"💰 Estimated cost: ${self.estimated_cost:.2f}\n\n"

        if self.options:
            msg += "**Options:**\n"
            for i, opt in enumerate(self.options, 1):
                label = opt.get("label", str(opt))
                msg += f"{i}. {label}\n"
            msg += "\nReply with option number, 'approve', or 'cancel'\n"
        else:
            msg += "Reply 'approve' to proceed or 'cancel' to abort.\n"

        msg += f"\n_Expires in {self._time_until_expiry()}_"
        return msg

    def _time_until_expiry(self) -> str:
        delta = self.expires_at - datetime.utcnow()
        hours = int(delta.total_seconds() / 3600)
        if hours > 24:
            return f"{hours // 24} days"
        elif hours > 0:
            return f"{hours} hours"
        else:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes} minutes"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "tool": self.tool,
            "action": self.action,
            "description": self.description,
            "estimated_cost": float(self.estimated_cost) if self.estimated_cost else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }


class ApprovalManager:
    """Manages pending approvals and their resolution."""

    def __init__(self):
        # In production, use database
        self._pending: dict[UUID, PendingApproval] = {}
        self._user_pending: dict[UUID, list[UUID]] = {}  # user_id -> approval_ids

    async def create_approval(
        self,
        user_id: UUID,
        tool: str,
        action: str,
        description: str,
        parameters: dict,
        estimated_cost: Optional[Decimal] = None,
        options: Optional[list[dict]] = None,
        plan_id: Optional[UUID] = None,
        step_id: Optional[UUID] = None,
        channel: str = "",
        expires_in_hours: int = 24,
    ) -> PendingApproval:
        """Create a new pending approval."""
        approval = PendingApproval(
            user_id=user_id,
            tool=tool,
            action=action,
            parameters=parameters,
            description=description,
            estimated_cost=estimated_cost,
            options=options,
            plan_id=plan_id,
            step_id=step_id,
            channel=channel,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours),
        )

        self._pending[approval.id] = approval
        if user_id not in self._user_pending:
            self._user_pending[user_id] = []
        self._user_pending[user_id].append(approval.id)

        return approval

    async def get_pending(self, approval_id: UUID) -> Optional[PendingApproval]:
        """Get a pending approval by ID."""
        approval = self._pending.get(approval_id)
        if approval and approval.is_expired:
            approval.status = ApprovalStatus.EXPIRED
        return approval

    async def get_user_pending(self, user_id: UUID) -> list[PendingApproval]:
        """Get all pending approvals for a user."""
        approval_ids = self._user_pending.get(user_id, [])
        approvals = []
        for aid in approval_ids:
            approval = await self.get_pending(aid)
            if approval and approval.status == ApprovalStatus.PENDING:
                approvals.append(approval)
        return approvals

    async def approve(
        self,
        approval_id: UUID,
        selected_option: Optional[int] = None,
    ) -> Optional[PendingApproval]:
        """Approve a pending request."""
        approval = await self.get_pending(approval_id)
        if not approval:
            return None

        if approval.status != ApprovalStatus.PENDING:
            return approval  # Already resolved

        approval.status = ApprovalStatus.APPROVED
        approval.selected_option = selected_option
        approval.resolved_at = datetime.utcnow()

        return approval

    async def reject(
        self,
        approval_id: UUID,
        reason: Optional[str] = None,
    ) -> Optional[PendingApproval]:
        """Reject a pending request."""
        approval = await self.get_pending(approval_id)
        if not approval:
            return None

        if approval.status != ApprovalStatus.PENDING:
            return approval

        approval.status = ApprovalStatus.REJECTED
        approval.rejection_reason = reason
        approval.resolved_at = datetime.utcnow()

        return approval

    async def resolve_from_message(
        self,
        user_id: UUID,
        message: str,
    ) -> tuple[Optional[PendingApproval], str]:
        """Try to resolve a pending approval from user message."""
        message = message.strip().lower()

        # Get user's pending approvals
        pending = await self.get_user_pending(user_id)
        if not pending:
            return None, "No pending approvals"

        # Take the most recent one
        approval = pending[-1]

        # Parse the response
        if message in ("approve", "yes", "ok", "confirm", "y", "proceed"):
            resolved = await self.approve(approval.id)
            return resolved, "Approved"

        elif message in ("cancel", "no", "reject", "n", "stop", "abort"):
            resolved = await self.reject(approval.id, "User cancelled")
            return resolved, "Cancelled"

        elif message.isdigit() and approval.options:
            # User selected an option by number
            option_num = int(message)
            if 1 <= option_num <= len(approval.options):
                resolved = await self.approve(approval.id, option_num - 1)
                return resolved, f"Selected option {option_num}"
            else:
                return None, f"Invalid option. Please choose 1-{len(approval.options)}"

        else:
            return None, "Reply 'approve' or 'cancel'"

    def cleanup_expired(self) -> int:
        """Clean up expired approvals. Returns count removed."""
        expired = []
        for aid, approval in self._pending.items():
            if approval.is_expired:
                approval.status = ApprovalStatus.EXPIRED
                expired.append(aid)

        for aid in expired:
            del self._pending[aid]

        return len(expired)
