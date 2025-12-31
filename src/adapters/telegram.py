"""Telegram adapter for Franklin AI.

Uses python-telegram-bot library for Telegram Bot API integration.
Supports both webhook and polling modes.
"""

from typing import Optional
import httpx

from src.config import get_settings

settings = get_settings()


class TelegramAdapter:
    """
    Telegram Bot adapter for Franklin AI.

    Usage:
        adapter = TelegramAdapter()
        await adapter.send_message(chat_id, "Hello!")
    """

    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(
        self,
        chat_id: str | int,
        message: str,
        parse_mode: str = "HTML",
        reply_markup: Optional[dict] = None,
    ) -> dict:
        """
        Send a text message via Telegram Bot API.

        Args:
            chat_id: Telegram chat ID
            message: Message text
            parse_mode: HTML or Markdown
            reply_markup: Optional inline keyboard or reply keyboard

        Returns:
            API response dict
        """
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode,
        }

        if reply_markup:
            payload["reply_markup"] = reply_markup

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=30.0,
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message_id": data.get("result", {}).get("message_id"),
                    "chat_id": chat_id,
                }
            else:
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code,
                }

    async def send_photo(
        self,
        chat_id: str | int,
        photo_url: str,
        caption: Optional[str] = None,
    ) -> dict:
        """Send a photo via Telegram."""
        payload = {
            "chat_id": chat_id,
            "photo": photo_url,
        }

        if caption:
            payload["caption"] = caption
            payload["parse_mode"] = "HTML"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/sendPhoto",
                json=payload,
                timeout=30.0,
            )

            return {
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text,
            }

    async def send_document(
        self,
        chat_id: str | int,
        document_url: str,
        caption: Optional[str] = None,
    ) -> dict:
        """Send a document via Telegram."""
        payload = {
            "chat_id": chat_id,
            "document": document_url,
        }

        if caption:
            payload["caption"] = caption

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/sendDocument",
                json=payload,
                timeout=30.0,
            )

            return {
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text,
            }

    def parse_webhook(self, data: dict) -> dict:
        """
        Parse incoming Telegram webhook update.

        Telegram sends updates in this format:
        {
            "update_id": 123,
            "message": {
                "message_id": 456,
                "from": {"id": 789, "first_name": "John", "username": "johndoe"},
                "chat": {"id": 789, "type": "private"},
                "date": 1234567890,
                "text": "Hello!"
            }
        }

        Returns:
            Normalized message dict
        """
        message = data.get("message", {})
        callback_query = data.get("callback_query", {})

        # Handle regular messages
        if message:
            from_user = message.get("from", {})
            chat = message.get("chat", {})

            return {
                "update_id": data.get("update_id"),
                "message_id": message.get("message_id"),
                "chat_id": chat.get("id"),
                "user_id": from_user.get("id"),
                "username": from_user.get("username", ""),
                "first_name": from_user.get("first_name", ""),
                "last_name": from_user.get("last_name", ""),
                "message_body": message.get("text", ""),
                "message_type": self._get_message_type(message),
                "timestamp": message.get("date"),
                "is_callback": False,
            }

        # Handle callback queries (inline keyboard button presses)
        elif callback_query:
            from_user = callback_query.get("from", {})
            message = callback_query.get("message", {})
            chat = message.get("chat", {})

            return {
                "update_id": data.get("update_id"),
                "callback_query_id": callback_query.get("id"),
                "chat_id": chat.get("id"),
                "user_id": from_user.get("id"),
                "username": from_user.get("username", ""),
                "first_name": from_user.get("first_name", ""),
                "message_body": callback_query.get("data", ""),
                "message_type": "callback",
                "is_callback": True,
            }

        return {}

    def _get_message_type(self, message: dict) -> str:
        """Determine the type of message received."""
        if message.get("text"):
            return "text"
        elif message.get("photo"):
            return "photo"
        elif message.get("document"):
            return "document"
        elif message.get("voice"):
            return "voice"
        elif message.get("video"):
            return "video"
        elif message.get("sticker"):
            return "sticker"
        elif message.get("contact"):
            return "contact"
        elif message.get("location"):
            return "location"
        else:
            return "unknown"

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False,
    ) -> dict:
        """Answer a callback query (acknowledge button press)."""
        payload = {
            "callback_query_id": callback_query_id,
        }

        if text:
            payload["text"] = text
            payload["show_alert"] = show_alert

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/answerCallbackQuery",
                json=payload,
                timeout=30.0,
            )

            return {"success": response.status_code == 200}

    async def set_webhook(self, webhook_url: str) -> dict:
        """Set the webhook URL for receiving updates."""
        payload = {
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"],
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/setWebhook",
                json=payload,
                timeout=30.0,
            )

            return {
                "success": response.status_code == 200,
                "response": response.json(),
            }

    async def delete_webhook(self) -> dict:
        """Remove the webhook (switch to polling mode)."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/deleteWebhook",
                timeout=30.0,
            )

            return {
                "success": response.status_code == 200,
                "response": response.json(),
            }

    async def get_me(self) -> dict:
        """Get bot info (useful for testing connection)."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/getMe",
                timeout=30.0,
            )

            if response.status_code == 200:
                return response.json().get("result", {})
            return {"error": response.text}

    def build_inline_keyboard(self, buttons: list[list[dict]]) -> dict:
        """
        Build an inline keyboard markup.

        Args:
            buttons: 2D list of button dicts, each with 'text' and 'callback_data'

        Example:
            adapter.build_inline_keyboard([
                [{"text": "Option 1", "callback_data": "opt1"}],
                [{"text": "Option 2", "callback_data": "opt2"}],
            ])
        """
        return {
            "inline_keyboard": buttons,
        }

    def build_reply_keyboard(
        self,
        buttons: list[list[str]],
        one_time: bool = True,
        resize: bool = True,
    ) -> dict:
        """
        Build a reply keyboard markup.

        Args:
            buttons: 2D list of button text strings
            one_time: Hide keyboard after button press
            resize: Fit keyboard to button sizes
        """
        keyboard = [[{"text": btn} for btn in row] for row in buttons]

        return {
            "keyboard": keyboard,
            "one_time_keyboard": one_time,
            "resize_keyboard": resize,
        }
