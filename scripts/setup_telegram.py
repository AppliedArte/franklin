#!/usr/bin/env python3
"""Setup script for Telegram bot webhook."""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.telegram import TelegramAdapter
from src.config import get_settings


async def main():
    settings = get_settings()

    if not settings.telegram_bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in environment")
        print("\nTo set up Telegram:")
        print("1. Message @BotFather on Telegram")
        print("2. Send /newbot and follow the prompts")
        print("3. Copy the token and add to .env:")
        print("   TELEGRAM_BOT_TOKEN=your_token_here")
        sys.exit(1)

    adapter = TelegramAdapter()

    # Test connection
    print("Testing bot connection...")
    bot_info = await adapter.get_me()

    if "error" in bot_info:
        print(f"ERROR: Failed to connect to bot: {bot_info['error']}")
        sys.exit(1)

    print(f"Connected to bot: @{bot_info.get('username', 'unknown')}")
    print(f"Bot name: {bot_info.get('first_name', 'unknown')}")

    # Check for webhook URL argument
    if len(sys.argv) > 1:
        webhook_url = sys.argv[1]

        if webhook_url == "--delete":
            print("\nDeleting webhook...")
            result = await adapter.delete_webhook()
            if result["success"]:
                print("Webhook deleted. Bot will use polling mode.")
            else:
                print(f"Failed to delete webhook: {result}")
        else:
            # Ensure URL ends with /webhooks/telegram
            if not webhook_url.endswith("/webhooks/telegram"):
                webhook_url = webhook_url.rstrip("/") + "/webhooks/telegram"

            print(f"\nSetting webhook to: {webhook_url}")
            result = await adapter.set_webhook(webhook_url)

            if result["success"]:
                print("Webhook set successfully!")
                print(f"Response: {result['response']}")
            else:
                print(f"Failed to set webhook: {result}")
    else:
        print("\nUsage:")
        print("  Set webhook:    python scripts/setup_telegram.py https://your-domain.com")
        print("  Delete webhook: python scripts/setup_telegram.py --delete")
        print("\nCurrent bot is ready. Set a webhook URL to receive messages.")


if __name__ == "__main__":
    asyncio.run(main())
