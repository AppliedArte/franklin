"""WhatsApp adapter with multiple provider support.

Supports:
- WasenderAPI ($6/mo) - Cheapest for validation
- Twilio - More reliable, higher cost
- 360dialog - Best for scale
"""

from typing import Optional
from abc import ABC, abstractmethod

import httpx

from src.config import get_settings

settings = get_settings()


class WhatsAppProvider(ABC):
    """Abstract base class for WhatsApp providers."""

    @abstractmethod
    async def send_message(self, to_number: str, message: str) -> dict:
        pass

    @abstractmethod
    def parse_webhook(self, data: dict) -> dict:
        pass


class WasenderAPIProvider(WhatsAppProvider):
    """
    WasenderAPI - Cheapest WhatsApp API ($6/mo).

    Docs: https://wasenderapi.com/docs
    """

    def __init__(self):
        self.api_key = settings.wasender_api_key
        self.device_id = settings.wasender_device_id
        self.base_url = "https://api.wasenderapi.com/v1"

    async def send_message(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None,
    ) -> dict:
        """Send a WhatsApp message via WasenderAPI."""
        # Normalize phone number (remove + and spaces)
        to_number = to_number.replace("+", "").replace(" ", "").replace("-", "")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "device_id": self.device_id,
            "to": to_number,
            "message": message,
        }

        if media_url:
            payload["media_url"] = media_url

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/send-message",
                headers=headers,
                json=payload,
                timeout=30.0,
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message_id": data.get("message_id"),
                    "status": data.get("status"),
                }
            else:
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code,
                }

    def parse_webhook(self, data: dict) -> dict:
        """Parse incoming webhook from WasenderAPI."""
        return {
            "from_number": data.get("from", ""),
            "to_number": data.get("to", ""),
            "message_body": data.get("message", {}).get("text", ""),
            "message_id": data.get("message_id", ""),
            "timestamp": data.get("timestamp"),
            "message_type": data.get("message", {}).get("type", "text"),
        }


class TwilioProvider(WhatsAppProvider):
    """
    Twilio WhatsApp provider.

    More reliable but $0.005/msg markup.
    """

    def __init__(self):
        from twilio.rest import Client

        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token,
        )
        self.from_number = settings.twilio_whatsapp_number

    async def send_message(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None,
    ) -> dict:
        """Send a WhatsApp message via Twilio."""
        try:
            # Ensure proper WhatsApp format
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"

            kwargs = {
                "body": message,
                "from_": self.from_number,
                "to": to_number,
            }

            if media_url:
                kwargs["media_url"] = [media_url]

            msg = self.client.messages.create(**kwargs)

            return {
                "success": True,
                "message_id": msg.sid,
                "status": msg.status,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def parse_webhook(self, data: dict) -> dict:
        """Parse incoming webhook from Twilio."""
        return {
            "from_number": data.get("From", "").replace("whatsapp:", ""),
            "to_number": data.get("To", "").replace("whatsapp:", ""),
            "message_body": data.get("Body", ""),
            "message_id": data.get("MessageSid", ""),
            "num_media": int(data.get("NumMedia", 0)),
            "profile_name": data.get("ProfileName", ""),
        }


class WhatsAppAdapter:
    """
    Unified WhatsApp adapter that supports multiple providers.

    Usage:
        adapter = WhatsAppAdapter()  # Uses default provider from config
        adapter = WhatsAppAdapter(provider="twilio")  # Force specific provider
    """

    def __init__(self, provider: Optional[str] = None):
        provider = provider or settings.whatsapp_provider

        if provider == "wasender":
            self._provider = WasenderAPIProvider()
        elif provider == "twilio":
            self._provider = TwilioProvider()
        else:
            # Default to WasenderAPI for cheap validation
            self._provider = WasenderAPIProvider()

        self.provider_name = provider or "wasender"

    async def send_message(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None,
    ) -> dict:
        """Send a WhatsApp message."""
        return await self._provider.send_message(to_number, message, media_url)

    def parse_webhook(self, data: dict) -> dict:
        """Parse incoming webhook data."""
        return self._provider.parse_webhook(data)

    async def send_template_message(
        self,
        to_number: str,
        template_name: str,
        template_params: dict,
    ) -> dict:
        """
        Send a template message (for initiating conversations).

        Note: WasenderAPI doesn't support official templates.
        This only works with Twilio/360dialog.
        """
        if self.provider_name == "wasender":
            # WasenderAPI doesn't have official templates
            # Send as regular message (only works if user messaged first)
            message = template_params.get("body", "Hello!")
            return await self.send_message(to_number, message)

        # For Twilio, use content templates
        # TODO: Implement Twilio template support
        return {"success": False, "error": "Templates not supported for this provider"}
