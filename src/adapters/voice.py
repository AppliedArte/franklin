"""Voice adapter using Vapi.ai for AI-powered voice calls."""

import httpx
from typing import Optional

from src.config import get_settings

settings = get_settings()


class VoiceAdapter:
    """Adapter for AI voice calls via Vapi.ai."""

    def __init__(self):
        self.api_key = settings.vapi_api_key
        self.base_url = "https://api.vapi.ai"

    async def initiate_call(
        self,
        phone_number: str,
        assistant_config: Optional[dict] = None,
    ) -> dict:
        """
        Initiate an outbound AI voice call.

        Args:
            phone_number: Number to call (with country code)
            assistant_config: Optional custom assistant configuration

        Returns:
            dict with call ID and status
        """
        from src.persona import PERSONA_VOICE_GREETING

        default_config = {
            "name": "Benjamin Franklin - Wealth Advisor",
            "firstMessage": PERSONA_VOICE_GREETING,
            "model": {
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514",
                "systemPrompt": self._get_voice_system_prompt(),
            },
            "voice": {
                "provider": "11labs",
                "voiceId": settings.elevenlabs_voice_id,
            },
        }

        config = assistant_config or default_config

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/call/phone",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "phoneNumberId": settings.vapi_phone_number_id or None,
                    "customer": {
                        "number": phone_number,
                    },
                    "assistant": config,
                },
            )

            if response.status_code == 201:
                data = response.json()
                return {
                    "success": True,
                    "call_id": data.get("id"),
                    "status": data.get("status"),
                }
            else:
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code,
                }

    async def get_call_status(self, call_id: str) -> dict:
        """Get the status of an ongoing or completed call."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/call/{call_id}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                },
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text}

    async def get_call_transcript(self, call_id: str) -> Optional[str]:
        """Get the transcript of a completed call."""
        call_data = await self.get_call_status(call_id)

        if "transcript" in call_data:
            return call_data["transcript"]

        return None

    def _get_voice_system_prompt(self) -> str:
        """Get the system prompt for voice conversations."""
        from src.persona import PERSONA_BACKGROUND

        return f"""{PERSONA_BACKGROUND}

## Voice-Specific Guidelines

You are speaking on a telephone call. Adjust your manner accordingly:

- Speak naturally and conversationally, as a gentleman would in parlour conversation
- Keep responses brief (2-3 sentences) - this is spoken word, not written correspondence
- Pause appropriately to allow them to respond
- Use clear language - your eloquence should illuminate, not obscure
- Ask one question at a time
- Be patient if they need time to consider
- Confirm your understanding of figures and amounts

## Your Goals for This Call
1. Understand their financial aspirations
2. Learn of their current circumstances
3. Provide helpful guidance
4. Know when to suggest a follow-up or refer to specialists

## Voice Manner
- Warm and avuncular, as if speaking to a friend
- Not robotic or as if reading from prepared remarks
- Natural pauses and acknowledgments ("I see", "Indeed", "Most interesting")
- Speak as Ben would - refined but accessible"""

    @staticmethod
    def parse_webhook_data(data: dict) -> dict:
        """Parse incoming webhook data from Vapi."""
        return {
            "call_id": data.get("call", {}).get("id"),
            "type": data.get("message", {}).get("type"),
            "transcript": data.get("message", {}).get("transcript"),
            "ended_reason": data.get("message", {}).get("endedReason"),
            "duration_seconds": data.get("message", {}).get("durationSeconds"),
            "customer_number": data.get("call", {}).get("customer", {}).get("number"),
        }
