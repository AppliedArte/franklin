"""Gmail Tool - AI-powered email management."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from src.tools.base import Tool, ToolAction, ToolResult, ToolCategory, ApprovalLevel
from src.services.gmail import GmailService, GmailMessage
from src.services.gmail_analyzer import GmailAnalyzer


class GmailTool(Tool):
    """Tool for Gmail management with AI-powered analysis."""

    name = "gmail"
    description = "Read, analyze, and manage Gmail with AI-powered importance scoring and spam detection"
    category = ToolCategory.EMAIL
    version = "1.0.0"

    requires_auth = True
    auth_type = "oauth2"

    def _register_actions(self) -> None:
        """Register Gmail actions."""

        # Read-only actions (ApprovalLevel.NONE)
        self.register_action(ToolAction(
            name="analyze_inbox",
            description="Analyze recent emails for importance and spam. Highlights important emails and spam candidates.",
            parameters={
                "days": {
                    "type": "integer",
                    "description": "Number of days to analyze (default 30)",
                    "default": 30,
                },
                "max_emails": {
                    "type": "integer",
                    "description": "Maximum emails to analyze (default 100)",
                    "default": 100,
                },
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="list_emails",
            description="List emails with optional filters",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Gmail search query (e.g., 'from:user@example.com', 'subject:invoice')",
                },
                "label": {
                    "type": "string",
                    "description": "Filter by label (e.g., 'INBOX', 'STARRED')",
                },
                "unread_only": {
                    "type": "boolean",
                    "description": "Only show unread emails",
                    "default": False,
                },
                "days": {
                    "type": "integer",
                    "description": "Only emails from last N days",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results (default 20)",
                    "default": 20,
                },
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="read_email",
            description="Read the full content of a specific email",
            parameters={
                "email_id": {
                    "type": "string",
                    "description": "Gmail message ID",
                    "required": True,
                },
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="get_important",
            description="Get AI-identified important emails",
            parameters={
                "threshold": {
                    "type": "number",
                    "description": "Importance threshold 0-1 (default 0.7)",
                    "default": 0.7,
                },
                "days": {
                    "type": "integer",
                    "description": "Days to look back (default 7)",
                    "default": 7,
                },
                "max_emails": {
                    "type": "integer",
                    "description": "Maximum emails to analyze (default 50)",
                    "default": 50,
                },
            },
            approval_level=ApprovalLevel.NONE,
        ))

        self.register_action(ToolAction(
            name="get_spam_candidates",
            description="Get emails identified as potential spam that could be moved to junk",
            parameters={
                "threshold": {
                    "type": "number",
                    "description": "Spam probability threshold 0-1 (default 0.6)",
                    "default": 0.6,
                },
                "days": {
                    "type": "integer",
                    "description": "Days to analyze (default 30)",
                    "default": 30,
                },
                "max_emails": {
                    "type": "integer",
                    "description": "Maximum emails to analyze (default 100)",
                    "default": 100,
                },
            },
            approval_level=ApprovalLevel.NONE,
        ))

        # Write actions (ApprovalLevel.CONFIRM)
        self.register_action(ToolAction(
            name="archive",
            description="Archive email(s) - removes from inbox but keeps in All Mail",
            parameters={
                "email_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of email IDs to archive",
                    "required": True,
                },
            },
            approval_level=ApprovalLevel.CONFIRM,
        ))

        self.register_action(ToolAction(
            name="trash",
            description="Move email(s) to trash",
            parameters={
                "email_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of email IDs to trash",
                    "required": True,
                },
            },
            approval_level=ApprovalLevel.CONFIRM,
        ))

        self.register_action(ToolAction(
            name="move_to_spam",
            description="Mark email(s) as spam and move to junk folder",
            parameters={
                "email_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of email IDs to mark as spam",
                    "required": True,
                },
            },
            approval_level=ApprovalLevel.CONFIRM,
        ))

        self.register_action(ToolAction(
            name="label",
            description="Add or remove labels from email(s)",
            parameters={
                "email_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of email IDs",
                    "required": True,
                },
                "add_labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Labels to add",
                },
                "remove_labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Labels to remove",
                },
            },
            approval_level=ApprovalLevel.CONFIRM,
        ))

        # Low-approval actions (ApprovalLevel.NOTIFY)
        self.register_action(ToolAction(
            name="mark_read",
            description="Mark email(s) as read",
            parameters={
                "email_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of email IDs to mark as read",
                    "required": True,
                },
            },
            approval_level=ApprovalLevel.NOTIFY,
        ))

        self.register_action(ToolAction(
            name="mark_unread",
            description="Mark email(s) as unread",
            parameters={
                "email_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of email IDs to mark as unread",
                    "required": True,
                },
            },
            approval_level=ApprovalLevel.NOTIFY,
        ))

        # Bulk action (ApprovalLevel.STRICT)
        self.register_action(ToolAction(
            name="bulk_cleanup",
            description="Bulk cleanup based on AI spam detection",
            parameters={
                "action": {
                    "type": "string",
                    "enum": ["trash", "spam", "archive"],
                    "description": "Action to take on spam candidates",
                    "required": True,
                },
                "spam_threshold": {
                    "type": "number",
                    "description": "Spam probability threshold (default 0.8)",
                    "default": 0.8,
                },
                "days": {
                    "type": "integer",
                    "description": "Days to analyze (default 30)",
                    "default": 30,
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "Preview without taking action (default true)",
                    "default": True,
                },
            },
            approval_level=ApprovalLevel.STRICT,
        ))

    async def execute(self, action: str, params: dict, user_id: UUID) -> ToolResult:
        """Execute a Gmail action."""
        handlers = {
            "analyze_inbox": self._analyze_inbox,
            "list_emails": self._list_emails,
            "read_email": self._read_email,
            "get_important": self._get_important,
            "get_spam_candidates": self._get_spam_candidates,
            "archive": self._archive,
            "trash": self._trash,
            "move_to_spam": self._move_to_spam,
            "label": self._label,
            "mark_read": self._mark_read,
            "mark_unread": self._mark_unread,
            "bulk_cleanup": self._bulk_cleanup,
        }

        handler = handlers.get(action)
        if not handler:
            return ToolResult(
                success=False,
                error=f"Unknown action: {action}",
            )

        try:
            return await handler(params, str(user_id))
        except ValueError as e:
            error_msg = str(e)
            if "not connected" in error_msg.lower() or "not granted" in error_msg.lower():
                return ToolResult(
                    success=False,
                    error="Gmail not connected. Please connect Gmail first.",
                    metadata={"connect_url": "/oauth/google/gmail/authorize"},
                )
            return ToolResult(success=False, error=error_msg)
        except Exception as e:
            return ToolResult(success=False, error=f"Gmail error: {str(e)}")

    async def check_auth(self, user_id: UUID) -> bool:
        """Check if user has Gmail connected."""
        service = GmailService(str(user_id))
        return await service.is_connected()

    async def _analyze_inbox(self, params: dict, user_id: str) -> ToolResult:
        """Analyze inbox for importance and spam."""
        days = params.get("days", 30)
        max_emails = params.get("max_emails", 100)

        service = GmailService(user_id)
        analyzer = GmailAnalyzer()

        # Get recent emails
        after_date = datetime.utcnow() - timedelta(days=days)
        messages = await service.list_messages(
            max_results=max_emails,
            after=after_date,
            label_ids=["INBOX"],
        )

        if not messages:
            return ToolResult(
                success=True,
                data={"emails": [], "summary": None},
                summary="No emails found in the specified time range.",
            )

        # Analyze emails
        analyses = await analyzer.analyze_emails(messages)
        inbox_summary = await analyzer.summarize_inbox(messages, analyses)

        # Identify important and spam
        important = [a for a in analyses if a.importance_score >= 0.7]
        spam_candidates = [a for a in analyses if a.spam_probability >= 0.6]

        # Build response
        result_data = {
            "total_analyzed": len(messages),
            "important_count": len(important),
            "spam_candidates_count": len(spam_candidates),
            "unread_count": inbox_summary.unread_count,
            "summary": inbox_summary.overall_summary,
            "important_emails": [
                {
                    "id": a.message_id,
                    "subject": next((m.subject for m in messages if m.id == a.message_id), ""),
                    "sender": next((m.sender for m in messages if m.id == a.message_id), ""),
                    "importance_score": a.importance_score,
                    "reason": a.importance_reason,
                    "action_required": a.action_required,
                }
                for a in sorted(important, key=lambda x: -x.importance_score)[:10]
            ],
            "spam_candidates": [
                {
                    "id": a.message_id,
                    "subject": next((m.subject for m in messages if m.id == a.message_id), ""),
                    "sender": next((m.sender for m in messages if m.id == a.message_id), ""),
                    "spam_probability": a.spam_probability,
                    "signals": a.spam_signals,
                }
                for a in sorted(spam_candidates, key=lambda x: -x.spam_probability)[:10]
            ],
        }

        summary_text = f"Analyzed {len(messages)} emails from the last {days} days. "
        summary_text += f"Found {len(important)} important emails and {len(spam_candidates)} spam candidates. "
        summary_text += f"{inbox_summary.unread_count} unread."

        return ToolResult(
            success=True,
            data=result_data,
            summary=summary_text,
            options=[
                {"label": f"View {len(important)} important", "value": "get_important"},
                {"label": f"Review {len(spam_candidates)} spam", "value": "get_spam_candidates"},
            ] if important or spam_candidates else None,
        )

    async def _list_emails(self, params: dict, user_id: str) -> ToolResult:
        """List emails with filters."""
        query = params.get("query", "")
        label = params.get("label")
        unread_only = params.get("unread_only", False)
        days = params.get("days")
        limit = params.get("limit", 20)

        service = GmailService(user_id)

        # Build query
        if unread_only:
            query = f"is:unread {query}".strip()

        # Date filter
        after_date = None
        if days:
            after_date = datetime.utcnow() - timedelta(days=days)

        # Label filter
        label_ids = [label] if label else None

        messages = await service.list_messages(
            query=query,
            max_results=limit,
            label_ids=label_ids,
            after=after_date,
        )

        return ToolResult(
            success=True,
            data=[m.to_dict() for m in messages],
            summary=f"Found {len(messages)} emails",
            options=[
                {"label": m.summary_text(), "value": m.id}
                for m in messages[:10]
            ],
        )

    async def _read_email(self, params: dict, user_id: str) -> ToolResult:
        """Read full email content."""
        email_id = params.get("email_id")
        if not email_id:
            return ToolResult(success=False, error="email_id is required")

        service = GmailService(user_id)
        message = await service.get_message(email_id)

        return ToolResult(
            success=True,
            data=message.to_dict(),
            summary=f"Email from {message.sender}: {message.subject}",
        )

    async def _get_important(self, params: dict, user_id: str) -> ToolResult:
        """Get important emails."""
        threshold = params.get("threshold", 0.7)
        days = params.get("days", 7)
        max_emails = params.get("max_emails", 50)

        service = GmailService(user_id)
        analyzer = GmailAnalyzer()

        after_date = datetime.utcnow() - timedelta(days=days)
        messages = await service.list_messages(
            max_results=max_emails,
            after=after_date,
            label_ids=["INBOX"],
        )

        if not messages:
            return ToolResult(
                success=True,
                data=[],
                summary="No emails found in the specified time range.",
            )

        important = await analyzer.get_important_emails(messages, threshold)

        result_data = [
            {
                "id": msg.id,
                "subject": msg.subject,
                "sender": msg.sender,
                "date": msg.date.isoformat(),
                "importance_score": analysis.importance_score,
                "reason": analysis.importance_reason,
                "action_required": analysis.action_required,
                "suggested_action": analysis.suggested_action,
                "summary": analysis.summary,
            }
            for msg, analysis in important
        ]

        return ToolResult(
            success=True,
            data=result_data,
            summary=f"Found {len(important)} important emails (score >= {threshold})",
            options=[
                {"label": f"{msg.sender}: {msg.subject[:30]}...", "value": msg.id}
                for msg, _ in important[:5]
            ] if important else None,
        )

    async def _get_spam_candidates(self, params: dict, user_id: str) -> ToolResult:
        """Get spam candidates."""
        threshold = params.get("threshold", 0.6)
        days = params.get("days", 30)
        max_emails = params.get("max_emails", 100)

        service = GmailService(user_id)
        analyzer = GmailAnalyzer()

        after_date = datetime.utcnow() - timedelta(days=days)
        messages = await service.list_messages(
            max_results=max_emails,
            after=after_date,
            label_ids=["INBOX"],
        )

        if not messages:
            return ToolResult(
                success=True,
                data=[],
                summary="No emails found in the specified time range.",
            )

        spam_candidates = await analyzer.get_spam_candidates(messages, threshold)

        result_data = [
            {
                "id": msg.id,
                "subject": msg.subject,
                "sender": msg.sender,
                "sender_email": msg.sender_email,
                "date": msg.date.isoformat(),
                "spam_probability": analysis.spam_probability,
                "spam_signals": analysis.spam_signals,
            }
            for msg, analysis in spam_candidates
        ]

        return ToolResult(
            success=True,
            data=result_data,
            summary=f"Found {len(spam_candidates)} spam candidates (probability >= {threshold})",
            options=[
                {"label": f"Move all to spam", "value": "move_to_spam"},
                {"label": f"Move all to trash", "value": "trash"},
            ] if spam_candidates else None,
            metadata={
                "email_ids": [msg.id for msg, _ in spam_candidates],
            },
        )

    async def _archive(self, params: dict, user_id: str) -> ToolResult:
        """Archive emails."""
        email_ids = params.get("email_ids", [])
        if not email_ids:
            return ToolResult(success=False, error="email_ids is required")

        service = GmailService(user_id)

        for email_id in email_ids:
            await service.archive_message(email_id)

        return ToolResult(
            success=True,
            data={"archived": email_ids},
            summary=f"Archived {len(email_ids)} email(s)",
        )

    async def _trash(self, params: dict, user_id: str) -> ToolResult:
        """Move emails to trash."""
        email_ids = params.get("email_ids", [])
        if not email_ids:
            return ToolResult(success=False, error="email_ids is required")

        service = GmailService(user_id)

        for email_id in email_ids:
            await service.trash_message(email_id)

        return ToolResult(
            success=True,
            data={"trashed": email_ids},
            summary=f"Moved {len(email_ids)} email(s) to trash",
        )

    async def _move_to_spam(self, params: dict, user_id: str) -> ToolResult:
        """Move emails to spam."""
        email_ids = params.get("email_ids", [])
        if not email_ids:
            return ToolResult(success=False, error="email_ids is required")

        service = GmailService(user_id)

        for email_id in email_ids:
            await service.move_to_spam(email_id)

        return ToolResult(
            success=True,
            data={"spam": email_ids},
            summary=f"Moved {len(email_ids)} email(s) to spam",
        )

    async def _label(self, params: dict, user_id: str) -> ToolResult:
        """Add/remove labels."""
        email_ids = params.get("email_ids", [])
        add_labels = params.get("add_labels", [])
        remove_labels = params.get("remove_labels", [])

        if not email_ids:
            return ToolResult(success=False, error="email_ids is required")
        if not add_labels and not remove_labels:
            return ToolResult(success=False, error="add_labels or remove_labels required")

        service = GmailService(user_id)

        if len(email_ids) > 1:
            await service.batch_modify_messages(email_ids, add_labels, remove_labels)
        else:
            await service.modify_message(email_ids[0], add_labels, remove_labels)

        return ToolResult(
            success=True,
            data={"modified": email_ids},
            summary=f"Updated labels on {len(email_ids)} email(s)",
        )

    async def _mark_read(self, params: dict, user_id: str) -> ToolResult:
        """Mark emails as read."""
        email_ids = params.get("email_ids", [])
        if not email_ids:
            return ToolResult(success=False, error="email_ids is required")

        service = GmailService(user_id)

        for email_id in email_ids:
            await service.mark_as_read(email_id)

        return ToolResult(
            success=True,
            data={"marked_read": email_ids},
            summary=f"Marked {len(email_ids)} email(s) as read",
        )

    async def _mark_unread(self, params: dict, user_id: str) -> ToolResult:
        """Mark emails as unread."""
        email_ids = params.get("email_ids", [])
        if not email_ids:
            return ToolResult(success=False, error="email_ids is required")

        service = GmailService(user_id)

        for email_id in email_ids:
            await service.mark_as_unread(email_id)

        return ToolResult(
            success=True,
            data={"marked_unread": email_ids},
            summary=f"Marked {len(email_ids)} email(s) as unread",
        )

    async def _bulk_cleanup(self, params: dict, user_id: str) -> ToolResult:
        """Bulk cleanup spam emails."""
        action = params.get("action")
        spam_threshold = params.get("spam_threshold", 0.8)
        days = params.get("days", 30)
        dry_run = params.get("dry_run", True)

        if action not in ["trash", "spam", "archive"]:
            return ToolResult(success=False, error="action must be 'trash', 'spam', or 'archive'")

        service = GmailService(user_id)
        analyzer = GmailAnalyzer()

        after_date = datetime.utcnow() - timedelta(days=days)
        messages = await service.list_messages(
            max_results=200,
            after=after_date,
            label_ids=["INBOX"],
        )

        spam_candidates = await analyzer.get_spam_candidates(messages, spam_threshold)

        if not spam_candidates:
            return ToolResult(
                success=True,
                data={"affected": 0},
                summary=f"No spam candidates found above {spam_threshold} threshold.",
            )

        email_ids = [msg.id for msg, _ in spam_candidates]

        if dry_run:
            return ToolResult(
                success=True,
                data={
                    "would_affect": len(email_ids),
                    "action": action,
                    "emails": [
                        {"id": msg.id, "subject": msg.subject, "sender": msg.sender}
                        for msg, _ in spam_candidates[:10]
                    ],
                },
                summary=f"DRY RUN: Would {action} {len(email_ids)} email(s). Set dry_run=false to execute.",
                options=[
                    {"label": f"Execute {action} on {len(email_ids)} emails", "value": "execute"},
                ],
            )

        # Execute the action
        if action == "trash":
            for email_id in email_ids:
                await service.trash_message(email_id)
        elif action == "spam":
            for email_id in email_ids:
                await service.move_to_spam(email_id)
        elif action == "archive":
            for email_id in email_ids:
                await service.archive_message(email_id)

        return ToolResult(
            success=True,
            data={"affected": len(email_ids), "action": action},
            summary=f"Bulk {action}: processed {len(email_ids)} email(s)",
        )
