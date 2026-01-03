"""Email Tool - Draft and send emails."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.config import get_settings
from src.tools.base import Tool, ToolAction, ToolResult, ToolCategory, ApprovalLevel

settings = get_settings()


@dataclass
class EmailDraft:
    """An email draft."""
    id: str = field(default_factory=lambda: str(uuid4()))
    to: list[str] = field(default_factory=list)
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)
    subject: str = ""
    body: str = ""
    html_body: Optional[str] = None
    attachments: list[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "draft"  # draft, sent, scheduled

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "to": self.to,
            "cc": self.cc,
            "subject": self.subject,
            "body": self.body[:200] + "..." if len(self.body) > 200 else self.body,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }

    def preview(self) -> str:
        recipients = ", ".join(self.to[:2])
        if len(self.to) > 2:
            recipients += f" +{len(self.to) - 2} more"
        return f"To: {recipients}\nSubject: {self.subject}\n\n{self.body[:100]}..."


class EmailTool(Tool):
    """Tool for drafting and sending emails."""

    name = "email"
    description = "Draft emails, send messages, and manage email communications"
    category = ToolCategory.EMAIL
    version = "1.0.0"

    requires_auth = True
    auth_type = "oauth2"  # Gmail or provider OAuth

    def _register_actions(self) -> None:
        """Register email actions."""
        self.register_action(ToolAction(
            name="draft",
            description="Create an email draft",
            parameters={
                "to": {"type": "array", "items": {"type": "string"}, "description": "Recipient email addresses", "required": True},
                "subject": {"type": "string", "description": "Email subject", "required": True},
                "body": {"type": "string", "description": "Email body (plain text)", "required": True},
                "cc": {"type": "array", "items": {"type": "string"}, "description": "CC recipients"},
                "bcc": {"type": "array", "items": {"type": "string"}, "description": "BCC recipients"},
            },
            approval_level=ApprovalLevel.NONE,  # Drafting is free
        ))

        self.register_action(ToolAction(
            name="send",
            description="Send an email or draft",
            parameters={
                "draft_id": {"type": "string", "description": "ID of draft to send"},
                "to": {"type": "array", "items": {"type": "string"}, "description": "Recipient email addresses"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body"},
            },
            approval_level=ApprovalLevel.CONFIRM,  # Sending needs approval
        ))

        self.register_action(ToolAction(
            name="search",
            description="Search emails in inbox",
            parameters={
                "query": {"type": "string", "description": "Search query", "required": True},
                "folder": {"type": "string", "description": "Folder to search (inbox, sent, all)", "default": "all"},
                "limit": {"type": "integer", "description": "Max results", "default": 10},
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="read",
            description="Read an email's full content",
            parameters={
                "email_id": {"type": "string", "description": "Email ID to read", "required": True},
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="reply",
            description="Reply to an email",
            parameters={
                "email_id": {"type": "string", "description": "Email ID to reply to", "required": True},
                "body": {"type": "string", "description": "Reply body", "required": True},
                "reply_all": {"type": "boolean", "description": "Reply to all recipients", "default": False},
            },
            approval_level=ApprovalLevel.CONFIRM,
        ))

    async def execute(self, action: str, params: dict, user_id: UUID) -> ToolResult:
        """Execute an email action."""
        if action == "draft":
            return await self._draft_email(params, user_id)
        elif action == "send":
            return await self._send_email(params, user_id)
        elif action == "search":
            return await self._search_emails(params, user_id)
        elif action == "read":
            return await self._read_email(params, user_id)
        elif action == "reply":
            return await self._reply_email(params, user_id)
        else:
            return ToolResult(success=False, error=f"Unknown action: {action}")

    async def _draft_email(self, params: dict, user_id: UUID) -> ToolResult:
        """Create an email draft."""
        draft = EmailDraft(
            to=params["to"],
            cc=params.get("cc", []),
            bcc=params.get("bcc", []),
            subject=params["subject"],
            body=params["body"],
        )

        # In production, save to database or email provider drafts
        return ToolResult(
            success=True,
            data=draft.to_dict(),
            summary=f"Draft created: '{draft.subject}' to {len(draft.to)} recipient(s)",
            metadata={
                "draft_id": draft.id,
                "preview": draft.preview(),
            },
        )

    async def _send_email(self, params: dict, user_id: UUID) -> ToolResult:
        """Send an email."""
        # In production, integrate with email provider (Resend, Gmail API, etc.)

        if params.get("draft_id"):
            # Send existing draft
            return ToolResult(
                success=True,
                summary=f"Email sent (draft {params['draft_id']})",
                metadata={"mock": True},
            )
        else:
            # Send new email
            to = params.get("to", [])
            subject = params.get("subject", "")
            return ToolResult(
                success=True,
                summary=f"Email sent: '{subject}' to {len(to)} recipient(s)",
                metadata={"mock": True},
            )

    async def _search_emails(self, params: dict, user_id: UUID) -> ToolResult:
        """Search emails."""
        # Mock search results
        mock_emails = [
            {
                "id": "email1",
                "from": "boss@company.com",
                "subject": "Q4 Planning",
                "snippet": "Let's discuss the Q4 priorities...",
                "date": "2024-01-02T10:30:00",
            },
            {
                "id": "email2",
                "from": "travel@airline.com",
                "subject": "Flight Confirmation - Tokyo",
                "snippet": "Your booking UA837 is confirmed...",
                "date": "2024-01-01T15:45:00",
            },
        ]

        return ToolResult(
            success=True,
            data=mock_emails,
            summary=f"Found {len(mock_emails)} emails matching '{params['query']}'",
            options=mock_emails,
            metadata={"mock": True},
        )

    async def _read_email(self, params: dict, user_id: UUID) -> ToolResult:
        """Read full email content."""
        # Mock email content
        return ToolResult(
            success=True,
            data={
                "id": params["email_id"],
                "from": "boss@company.com",
                "to": ["me@company.com"],
                "subject": "Q4 Planning",
                "body": "Hi,\n\nLet's discuss the Q4 priorities in our next meeting.\n\nBest,\nBoss",
                "date": "2024-01-02T10:30:00",
            },
            summary="Email retrieved",
            metadata={"mock": True},
        )

    async def _reply_email(self, params: dict, user_id: UUID) -> ToolResult:
        """Reply to an email."""
        return ToolResult(
            success=True,
            summary=f"Reply sent to email {params['email_id']}",
            metadata={"mock": True, "reply_all": params.get("reply_all", False)},
        )
