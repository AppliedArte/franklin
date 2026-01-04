"""Gmail API service for email operations."""

from __future__ import annotations

import base64
import email
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.api.oauth import get_google_credentials, has_gmail_scopes


# Gmail system label IDs
LABEL_INBOX = "INBOX"
LABEL_SPAM = "SPAM"
LABEL_TRASH = "TRASH"
LABEL_UNREAD = "UNREAD"
LABEL_STARRED = "STARRED"
LABEL_IMPORTANT = "IMPORTANT"
LABEL_SENT = "SENT"
LABEL_DRAFT = "DRAFT"


@dataclass
class GmailMessage:
    """A Gmail message."""
    id: str
    thread_id: str
    subject: str
    sender: str
    sender_email: str
    to: list[str]
    date: datetime
    snippet: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    labels: list[str] = field(default_factory=list)
    is_read: bool = True
    is_starred: bool = False
    is_important: bool = False
    has_attachments: bool = False

    # AI-computed fields (populated by analyzer)
    importance_score: Optional[float] = None
    spam_probability: Optional[float] = None
    category: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "subject": self.subject,
            "sender": self.sender,
            "sender_email": self.sender_email,
            "to": self.to,
            "date": self.date.isoformat(),
            "snippet": self.snippet,
            "body_text": self.body_text,
            "labels": self.labels,
            "is_read": self.is_read,
            "is_starred": self.is_starred,
            "is_important": self.is_important,
            "has_attachments": self.has_attachments,
            "importance_score": self.importance_score,
            "spam_probability": self.spam_probability,
            "category": self.category,
        }

    def summary_text(self) -> str:
        """Format for display."""
        date_str = self.date.strftime("%b %d, %I:%M %p")
        status = "📩" if not self.is_read else "📧"
        return f"{status} {self.sender}: {self.subject} ({date_str})"


class GmailService:
    """Service for interacting with Gmail API."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self._service = None

    async def _get_service(self):
        """Get authenticated Gmail service."""
        if self._service:
            return self._service

        credentials = await get_google_credentials(self.user_id)
        if not credentials:
            raise ValueError("User has not connected Gmail")

        # Check if Gmail scopes are available
        if not await has_gmail_scopes(self.user_id):
            raise ValueError("User has not granted Gmail access. Please connect Gmail.")

        self._service = build("gmail", "v1", credentials=credentials)
        return self._service

    async def is_connected(self) -> bool:
        """Check if user has connected Gmail with appropriate scopes."""
        return await has_gmail_scopes(self.user_id)

    async def list_messages(
        self,
        query: str = "",
        max_results: int = 50,
        label_ids: Optional[list[str]] = None,
        after: Optional[datetime] = None,
        before: Optional[datetime] = None,
        include_spam_trash: bool = False,
    ) -> list[GmailMessage]:
        """
        List messages matching criteria.

        Args:
            query: Gmail search query (e.g., "from:user@example.com")
            max_results: Maximum number of messages to return
            label_ids: Filter by label IDs (e.g., ["INBOX"])
            after: Only messages after this date
            before: Only messages before this date
            include_spam_trash: Include spam and trash in results

        Returns:
            List of GmailMessage objects with metadata (not full body)
        """
        service = await self._get_service()

        # Build query string with date filters
        query_parts = [query] if query else []
        if after:
            query_parts.append(f"after:{after.strftime('%Y/%m/%d')}")
        if before:
            query_parts.append(f"before:{before.strftime('%Y/%m/%d')}")

        full_query = " ".join(query_parts)

        try:
            # Get message IDs
            results = service.users().messages().list(
                userId="me",
                q=full_query if full_query else None,
                labelIds=label_ids,
                maxResults=max_results,
                includeSpamTrash=include_spam_trash,
            ).execute()

            messages = results.get("messages", [])
            if not messages:
                return []

            # Fetch metadata for each message
            gmail_messages = []
            for msg_ref in messages:
                try:
                    msg = service.users().messages().get(
                        userId="me",
                        id=msg_ref["id"],
                        format="metadata",
                        metadataHeaders=["From", "To", "Subject", "Date"],
                    ).execute()
                    gmail_messages.append(self._parse_message(msg))
                except HttpError:
                    continue  # Skip messages that can't be fetched

            return gmail_messages

        except HttpError as e:
            raise ValueError(f"Gmail API error: {e}")

    async def get_message(self, message_id: str, format: str = "full") -> GmailMessage:
        """
        Get a specific message with full content.

        Args:
            message_id: Gmail message ID
            format: "full" for complete message, "metadata" for headers only

        Returns:
            GmailMessage with body content
        """
        service = await self._get_service()

        try:
            msg = service.users().messages().get(
                userId="me",
                id=message_id,
                format=format,
            ).execute()
            return self._parse_message(msg, include_body=True)
        except HttpError as e:
            if e.resp.status == 404:
                raise ValueError("Message not found or already deleted")
            raise ValueError(f"Gmail API error: {e}")

    async def batch_get_messages(
        self,
        message_ids: list[str],
        include_body: bool = False,
    ) -> list[GmailMessage]:
        """
        Batch get multiple messages efficiently.

        Args:
            message_ids: List of message IDs
            include_body: Whether to include message body

        Returns:
            List of GmailMessage objects
        """
        service = await self._get_service()
        messages = []

        format_type = "full" if include_body else "metadata"
        metadata_headers = ["From", "To", "Subject", "Date"]

        # Gmail API supports batch requests, but for simplicity we'll do sequential
        # In production, use googleapiclient.http.BatchHttpRequest
        for msg_id in message_ids:
            try:
                msg = service.users().messages().get(
                    userId="me",
                    id=msg_id,
                    format=format_type,
                    metadataHeaders=metadata_headers if not include_body else None,
                ).execute()
                messages.append(self._parse_message(msg, include_body=include_body))
            except HttpError:
                continue  # Skip failed messages

        return messages

    async def modify_message(
        self,
        message_id: str,
        add_labels: Optional[list[str]] = None,
        remove_labels: Optional[list[str]] = None,
    ) -> GmailMessage:
        """
        Modify message labels.

        Args:
            message_id: Gmail message ID
            add_labels: Labels to add
            remove_labels: Labels to remove

        Returns:
            Updated GmailMessage
        """
        service = await self._get_service()

        body = {}
        if add_labels:
            body["addLabelIds"] = add_labels
        if remove_labels:
            body["removeLabelIds"] = remove_labels

        try:
            msg = service.users().messages().modify(
                userId="me",
                id=message_id,
                body=body,
            ).execute()
            return self._parse_message(msg)
        except HttpError as e:
            raise ValueError(f"Failed to modify message: {e}")

    async def batch_modify_messages(
        self,
        message_ids: list[str],
        add_labels: Optional[list[str]] = None,
        remove_labels: Optional[list[str]] = None,
    ) -> bool:
        """
        Batch modify multiple messages.

        Args:
            message_ids: List of message IDs
            add_labels: Labels to add to all
            remove_labels: Labels to remove from all

        Returns:
            True if successful
        """
        service = await self._get_service()

        body = {"ids": message_ids}
        if add_labels:
            body["addLabelIds"] = add_labels
        if remove_labels:
            body["removeLabelIds"] = remove_labels

        try:
            service.users().messages().batchModify(
                userId="me",
                body=body,
            ).execute()
            return True
        except HttpError as e:
            raise ValueError(f"Failed to batch modify messages: {e}")

    async def trash_message(self, message_id: str) -> bool:
        """Move message to trash."""
        service = await self._get_service()

        try:
            service.users().messages().trash(
                userId="me",
                id=message_id,
            ).execute()
            return True
        except HttpError as e:
            raise ValueError(f"Failed to trash message: {e}")

    async def archive_message(self, message_id: str) -> bool:
        """Archive message (remove INBOX label)."""
        await self.modify_message(message_id, remove_labels=[LABEL_INBOX])
        return True

    async def mark_as_read(self, message_id: str) -> bool:
        """Mark message as read."""
        await self.modify_message(message_id, remove_labels=[LABEL_UNREAD])
        return True

    async def mark_as_unread(self, message_id: str) -> bool:
        """Mark message as unread."""
        await self.modify_message(message_id, add_labels=[LABEL_UNREAD])
        return True

    async def move_to_spam(self, message_id: str) -> bool:
        """Move message to spam."""
        await self.modify_message(
            message_id,
            add_labels=[LABEL_SPAM],
            remove_labels=[LABEL_INBOX],
        )
        return True

    async def list_labels(self) -> list[dict]:
        """List available labels."""
        service = await self._get_service()

        try:
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            return [
                {
                    "id": label["id"],
                    "name": label["name"],
                    "type": label.get("type", "user"),
                }
                for label in labels
            ]
        except HttpError as e:
            raise ValueError(f"Failed to list labels: {e}")

    def _parse_message(self, msg: dict, include_body: bool = False) -> GmailMessage:
        """Parse Gmail API message response into GmailMessage."""
        headers = {}
        payload = msg.get("payload", {})

        for header in payload.get("headers", []):
            headers[header["name"].lower()] = header["value"]

        # Parse sender
        from_header = headers.get("from", "Unknown")
        sender_name = from_header
        sender_email = from_header
        if "<" in from_header and ">" in from_header:
            parts = from_header.split("<")
            sender_name = parts[0].strip().strip('"')
            sender_email = parts[1].rstrip(">")

        # Parse date
        date_str = headers.get("date", "")
        try:
            msg_date = parsedate_to_datetime(date_str)
        except Exception:
            msg_date = datetime.utcnow()

        # Parse to addresses
        to_header = headers.get("to", "")
        to_addresses = [addr.strip() for addr in to_header.split(",") if addr.strip()]

        # Get labels
        label_ids = msg.get("labelIds", [])

        # Extract body if requested
        body_text = None
        body_html = None
        has_attachments = False

        if include_body and payload:
            body_text, body_html, has_attachments = self._extract_body(payload)

        return GmailMessage(
            id=msg["id"],
            thread_id=msg.get("threadId", msg["id"]),
            subject=headers.get("subject", "(No Subject)"),
            sender=sender_name,
            sender_email=sender_email,
            to=to_addresses,
            date=msg_date,
            snippet=msg.get("snippet", ""),
            body_text=body_text,
            body_html=body_html,
            labels=label_ids,
            is_read=LABEL_UNREAD not in label_ids,
            is_starred=LABEL_STARRED in label_ids,
            is_important=LABEL_IMPORTANT in label_ids,
            has_attachments=has_attachments,
        )

    def _extract_body(self, payload: dict) -> tuple[Optional[str], Optional[str], bool]:
        """Extract text and HTML body from message payload."""
        body_text = None
        body_html = None
        has_attachments = False

        def decode_body(data: str) -> str:
            """Decode base64 encoded body."""
            try:
                return base64.urlsafe_b64decode(data).decode("utf-8")
            except Exception:
                return ""

        def process_part(part: dict):
            nonlocal body_text, body_html, has_attachments

            mime_type = part.get("mimeType", "")
            body = part.get("body", {})

            if body.get("attachmentId"):
                has_attachments = True

            if mime_type == "text/plain" and body.get("data"):
                body_text = decode_body(body["data"])
            elif mime_type == "text/html" and body.get("data"):
                body_html = decode_body(body["data"])

            # Process nested parts
            for sub_part in part.get("parts", []):
                process_part(sub_part)

        process_part(payload)
        return body_text, body_html, has_attachments
