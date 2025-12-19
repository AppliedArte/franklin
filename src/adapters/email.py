"""Email adapter using Resend."""

from typing import Optional, List

import resend

from src.config import get_settings

settings = get_settings()


class EmailAdapter:
    """Adapter for sending/receiving emails via Resend."""

    def __init__(self):
        resend.api_key = settings.resend_api_key
        self.from_email = settings.email_from

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> dict:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            reply_to: Optional reply-to address

        Returns:
            dict with email ID and status
        """
        try:
            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "text": body,
            }

            if html_body:
                params["html"] = html_body

            if reply_to:
                params["reply_to"] = reply_to

            # Resend SDK is synchronous
            response = resend.Emails.send(params)

            return {
                "success": True,
                "email_id": response.get("id"),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def send_conversation_email(
        self,
        to_email: str,
        user_name: Optional[str],
        ai_response: str,
        conversation_context: Optional[str] = None,
    ) -> dict:
        """
        Send a conversational email from the AI advisor.

        Formats the response appropriately for email context.
        """
        greeting = f"Hi {user_name}," if user_name else "Hi there,"

        plain_body = f"""{greeting}

{ai_response}

---
Your AI Wealth Advisor

*This is general educational information, not personalized investment advice.
Consider consulting a licensed financial advisor for recommendations specific to your situation.*

Reply to this email to continue our conversation.
"""

        html_body = f"""
<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <p>{greeting}</p>

    <div style="background: #f9f9f9; border-left: 4px solid #0066cc; padding: 15px; margin: 20px 0;">
        {ai_response.replace(chr(10), '<br>')}
    </div>

    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

    <p style="color: #666; font-size: 14px;">
        <strong>Your AI Wealth Advisor</strong>
    </p>

    <p style="color: #999; font-size: 12px; font-style: italic;">
        This is general educational information, not personalized investment advice.
        Consider consulting a licensed financial advisor for recommendations specific to your situation.
    </p>

    <p style="color: #666; font-size: 14px;">
        Reply to this email to continue our conversation.
    </p>
</body>
</html>
"""

        subject = "Your AI Wealth Advisor"
        if conversation_context:
            subject = f"Re: {conversation_context}"

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            body=plain_body,
            html_body=html_body,
        )

    async def send_introduction_email(
        self,
        to_email: str,
        user_name: Optional[str],
        referral_name: str,
        referral_context: str,
    ) -> dict:
        """
        Send a warm introduction email (Boardy-style matching).

        Used when connecting users with partners/advisors.
        """
        greeting = f"Hi {user_name}," if user_name else "Hi there,"

        plain_body = f"""{greeting}

I wanted to introduce you to {referral_name}.

{referral_context}

I thought this connection could be valuable for both of you. I've copied {referral_name} on this email so you can connect directly.

Best,
Your AI Wealth Advisor

---
*This introduction is based on your financial profile and goals.
Please do your own due diligence before engaging with any service providers.*
"""

        return await self.send_email(
            to_email=to_email,
            subject=f"Introduction: {referral_name}",
            body=plain_body,
        )

    @staticmethod
    def parse_inbound_email(data: dict) -> dict:
        """Parse inbound email webhook data."""
        return {
            "from_email": data.get("from"),
            "to_email": data.get("to"),
            "subject": data.get("subject", ""),
            "text_body": data.get("text", ""),
            "html_body": data.get("html", ""),
            "headers": data.get("headers", {}),
            "in_reply_to": data.get("headers", {}).get("In-Reply-To"),
        }
