"""AI-powered Gmail analysis using Claude."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

from anthropic import AsyncAnthropic

from src.config import get_settings
from src.services.gmail import GmailMessage

settings = get_settings()


@dataclass
class EmailAnalysis:
    """Analysis result for an email."""
    message_id: str
    importance_score: float  # 0-1, higher = more important
    importance_reason: str
    spam_probability: float  # 0-1
    spam_signals: list[str] = field(default_factory=list)
    category: str = "primary"  # primary, social, promotions, updates, forums
    action_required: bool = False
    suggested_action: Optional[str] = None  # "respond", "archive", "schedule", None
    summary: str = ""  # 1-2 sentence summary

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "importance_score": self.importance_score,
            "importance_reason": self.importance_reason,
            "spam_probability": self.spam_probability,
            "spam_signals": self.spam_signals,
            "category": self.category,
            "action_required": self.action_required,
            "suggested_action": self.suggested_action,
            "summary": self.summary,
        }


@dataclass
class InboxSummary:
    """Summary of inbox state."""
    total_emails: int
    unread_count: int
    important_count: int
    spam_candidates_count: int
    categories: dict[str, int]  # category -> count
    top_senders: list[dict]  # [{sender, count}]
    action_items: list[str]  # Emails that need attention
    overall_summary: str

    def to_dict(self) -> dict:
        return {
            "total_emails": self.total_emails,
            "unread_count": self.unread_count,
            "important_count": self.important_count,
            "spam_candidates_count": self.spam_candidates_count,
            "categories": self.categories,
            "top_senders": self.top_senders,
            "action_items": self.action_items,
            "overall_summary": self.overall_summary,
        }


IMPORTANCE_ANALYSIS_PROMPT = """Analyze these emails and score their importance for a wealth management professional.

For each email, provide:
1. importance_score: 0.0-1.0 (1.0 = urgent/critical)
2. importance_reason: Brief explanation (10 words max)
3. spam_probability: 0.0-1.0
4. spam_signals: List of red flags if spam_probability > 0.3
5. category: "primary", "social", "promotions", "updates", or "forums"
6. action_required: true if needs response or action
7. suggested_action: "respond", "archive", "schedule", or null
8. summary: 1 sentence summary of the email

Importance factors (high score):
- Direct messages from real people (not automated)
- Financial/investment discussions
- Time-sensitive requests or deadlines
- Client communications
- Meeting requests or calendar items
- Legal or compliance matters

Lower importance:
- Marketing/promotional emails
- Newsletters
- Automated notifications
- Social media updates
- Mass emails

Spam indicators:
- Unsolicited promotional content
- Deceptive subject lines
- Unknown sender with commercial intent
- Urgency tactics ("Act now!", "Limited time")
- Generic greetings ("Dear Customer")
- Suspicious links or requests for personal info

Emails to analyze:
{emails_json}

Return ONLY a valid JSON array with one object per email, in the same order. Example:
[
  {{"message_id": "abc123", "importance_score": 0.8, "importance_reason": "Client meeting request", "spam_probability": 0.0, "spam_signals": [], "category": "primary", "action_required": true, "suggested_action": "respond", "summary": "Client wants to schedule Q1 portfolio review."}}
]"""


SPAM_DETECTION_PROMPT = """Analyze these emails specifically for spam and unwanted mail patterns.

For each email, assess:
1. spam_probability: 0.0-1.0 (0 = definitely legitimate, 1 = definitely spam)
2. spam_signals: List of specific red flags detected
3. recommendation: "keep", "spam", or "unsubscribe"

Strong spam indicators (high probability):
- Unsolicited commercial email
- Phishing attempts
- Fake urgency ("Your account will be suspended!")
- Misspelled sender domains
- Generic/impersonal content
- Suspicious attachments or links
- No unsubscribe option for commercial mail

Legitimate indicators (low probability):
- From known contacts or companies user interacts with
- Personalized content
- Expected notifications (banks, services, employers)
- Has proper unsubscribe mechanisms
- Replies to user's emails

Emails to analyze:
{emails_json}

Return ONLY a valid JSON array. Example:
[
  {{"message_id": "abc123", "spam_probability": 0.9, "spam_signals": ["unknown sender", "urgency tactics", "misspelled domain"], "recommendation": "spam"}}
]"""


INBOX_SUMMARY_PROMPT = """Summarize this email inbox for a busy professional.

Inbox data:
- Total emails: {total_emails}
- Unread: {unread_count}
- Email details:
{emails_summary}

Provide a concise executive summary that includes:
1. Overall inbox status (is it manageable or overwhelming?)
2. Most important items that need attention (max 3)
3. Any patterns noticed (e.g., many marketing emails, recurring senders)
4. Recommended next actions

Keep the summary under 100 words. Be direct and actionable."""


class GmailAnalyzer:
    """Analyze emails using Claude for importance scoring and spam detection."""

    def __init__(self, model: str = None):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = model or "claude-3-5-haiku-20241022"  # Fast model for analysis

    async def analyze_emails(
        self,
        messages: list[GmailMessage],
        batch_size: int = 20,
    ) -> list[EmailAnalysis]:
        """
        Analyze a batch of emails for importance and spam.

        Args:
            messages: List of GmailMessage objects
            batch_size: Process in batches of this size

        Returns:
            List of EmailAnalysis results
        """
        if not messages:
            return []

        all_results = []

        # Process in batches
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            batch_results = await self._analyze_batch(batch)
            all_results.extend(batch_results)

        return all_results

    async def _analyze_batch(self, messages: list[GmailMessage]) -> list[EmailAnalysis]:
        """Analyze a single batch of messages."""
        # Prepare emails for analysis (minimal data to reduce tokens)
        emails_data = [
            {
                "message_id": msg.id,
                "subject": msg.subject,
                "sender": msg.sender,
                "sender_email": msg.sender_email,
                "snippet": msg.snippet[:200],  # Limit snippet length
                "date": msg.date.isoformat(),
                "is_read": msg.is_read,
            }
            for msg in messages
        ]

        prompt = IMPORTANCE_ANALYSIS_PROMPT.format(
            emails_json=json.dumps(emails_data, indent=2)
        )

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse JSON response
            response_text = response.content[0].text.strip()
            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()

            results_json = json.loads(response_text)

            # Convert to EmailAnalysis objects
            analyses = []
            for result in results_json:
                analyses.append(EmailAnalysis(
                    message_id=result.get("message_id", ""),
                    importance_score=float(result.get("importance_score", 0.5)),
                    importance_reason=result.get("importance_reason", ""),
                    spam_probability=float(result.get("spam_probability", 0.0)),
                    spam_signals=result.get("spam_signals", []),
                    category=result.get("category", "primary"),
                    action_required=result.get("action_required", False),
                    suggested_action=result.get("suggested_action"),
                    summary=result.get("summary", ""),
                ))

            return analyses

        except json.JSONDecodeError:
            # Fallback: return basic analysis
            return [
                EmailAnalysis(
                    message_id=msg.id,
                    importance_score=0.5,
                    importance_reason="Unable to analyze",
                    spam_probability=0.0,
                    category="primary",
                    summary=msg.snippet[:100],
                )
                for msg in messages
            ]
        except Exception as e:
            raise ValueError(f"Failed to analyze emails: {e}")

    async def detect_spam(
        self,
        messages: list[GmailMessage],
    ) -> list[dict]:
        """
        Detect spam patterns across messages.

        Returns list of {message_id, spam_probability, spam_signals, recommendation}
        """
        if not messages:
            return []

        emails_data = [
            {
                "message_id": msg.id,
                "subject": msg.subject,
                "sender": msg.sender,
                "sender_email": msg.sender_email,
                "snippet": msg.snippet[:200],
            }
            for msg in messages
        ]

        prompt = SPAM_DETECTION_PROMPT.format(
            emails_json=json.dumps(emails_data, indent=2)
        )

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()

            return json.loads(response_text)

        except Exception:
            # Return empty spam detection on failure
            return []

    async def summarize_inbox(
        self,
        messages: list[GmailMessage],
        analyses: Optional[list[EmailAnalysis]] = None,
    ) -> InboxSummary:
        """
        Generate executive summary of inbox state.

        Args:
            messages: List of messages to summarize
            analyses: Optional pre-computed analyses

        Returns:
            InboxSummary with stats and recommendations
        """
        if not messages:
            return InboxSummary(
                total_emails=0,
                unread_count=0,
                important_count=0,
                spam_candidates_count=0,
                categories={},
                top_senders=[],
                action_items=[],
                overall_summary="Your inbox is empty.",
            )

        # Calculate stats
        unread_count = sum(1 for m in messages if not m.is_read)

        # Count senders
        sender_counts: dict[str, int] = {}
        for msg in messages:
            sender_counts[msg.sender] = sender_counts.get(msg.sender, 0) + 1

        top_senders = [
            {"sender": sender, "count": count}
            for sender, count in sorted(sender_counts.items(), key=lambda x: -x[1])[:5]
        ]

        # Use analyses if provided
        important_count = 0
        spam_candidates_count = 0
        categories: dict[str, int] = {}
        action_items = []

        if analyses:
            for analysis in analyses:
                if analysis.importance_score >= 0.7:
                    important_count += 1
                if analysis.spam_probability >= 0.6:
                    spam_candidates_count += 1
                categories[analysis.category] = categories.get(analysis.category, 0) + 1
                if analysis.action_required:
                    # Find corresponding message
                    msg = next((m for m in messages if m.id == analysis.message_id), None)
                    if msg:
                        action_items.append(f"{msg.sender}: {msg.subject}")

        # Generate AI summary
        emails_summary = "\n".join([
            f"- {msg.sender}: {msg.subject}"
            for msg in messages[:30]  # Limit for prompt size
        ])

        prompt = INBOX_SUMMARY_PROMPT.format(
            total_emails=len(messages),
            unread_count=unread_count,
            emails_summary=emails_summary,
        )

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            overall_summary = response.content[0].text.strip()
        except Exception:
            overall_summary = f"You have {len(messages)} emails, {unread_count} unread."

        return InboxSummary(
            total_emails=len(messages),
            unread_count=unread_count,
            important_count=important_count,
            spam_candidates_count=spam_candidates_count,
            categories=categories,
            top_senders=top_senders,
            action_items=action_items[:5],  # Limit to top 5
            overall_summary=overall_summary,
        )

    async def get_important_emails(
        self,
        messages: list[GmailMessage],
        threshold: float = 0.7,
    ) -> list[tuple[GmailMessage, EmailAnalysis]]:
        """
        Get emails with importance score above threshold.

        Returns list of (message, analysis) tuples sorted by importance.
        """
        analyses = await self.analyze_emails(messages)

        # Create message lookup
        msg_lookup = {m.id: m for m in messages}

        # Filter and sort by importance
        important = [
            (msg_lookup[a.message_id], a)
            for a in analyses
            if a.importance_score >= threshold and a.message_id in msg_lookup
        ]

        return sorted(important, key=lambda x: -x[1].importance_score)

    async def get_spam_candidates(
        self,
        messages: list[GmailMessage],
        threshold: float = 0.6,
    ) -> list[tuple[GmailMessage, EmailAnalysis]]:
        """
        Get emails with spam probability above threshold.

        Returns list of (message, analysis) tuples sorted by spam probability.
        """
        analyses = await self.analyze_emails(messages)

        msg_lookup = {m.id: m for m in messages}

        spam = [
            (msg_lookup[a.message_id], a)
            for a in analyses
            if a.spam_probability >= threshold and a.message_id in msg_lookup
        ]

        return sorted(spam, key=lambda x: -x[1].spam_probability)
