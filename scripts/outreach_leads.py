#!/usr/bin/env python3
"""
Outreach to recent leads who haven't been contacted.

Usage:
    python scripts/outreach_leads.py --list          # List recent leads
    python scripts/outreach_leads.py --call          # Call leads without telegram
    python scripts/outreach_leads.py --telegram      # Message leads with telegram
    python scripts/outreach_leads.py --all           # Both
"""

import asyncio
import os
import sys
import argparse
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client

# Load env
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def get_leads():
    """Fetch recent leads from Supabase."""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Get leads from last 30 days
    result = supabase.table("leads").select("*").order("created_at", desc=True).limit(50).execute()

    return result.data


async def call_lead(lead: dict):
    """Initiate a Vapi call to a lead."""
    import httpx

    phone = lead.get("phone")
    name = lead.get("name", "friend")
    first_name = name.split()[0] if name else "friend"
    fund_name = lead.get("fund_name", "your company")
    user_type = lead.get("user_type", "investor")

    user_type_label = "an investor" if user_type == "investor" else "a founder"

    system_prompt = f"""You are Franklin, an AI private banker with a warm, avuncular personality.

You're calling {first_name} (full name: {name}), who is {user_type_label} at {fund_name}.

YOUR GOAL: Get to know this person and understand their background, current situation, and what they're looking for.

QUESTIONS TO ASK (one at a time, conversationally):
1. What prompted you to sign up? What are you hoping to get help with?
2. Tell me about yourself - what's your role at {fund_name}? How long have you been there?
3. What does {fund_name} do? What's your focus area?
4. Are you currently working with any financial advisors or wealth managers?
5. What are your main financial goals right now?

PERSONALITY:
- Warm, genuinely curious about their story
- Like catching up with an old friend
- Knowledgeable about finance but not showing off
- Never pushy - make them feel heard

RULES:
- Keep responses to 1-2 sentences MAX
- Ask ONE question at a time
- Use their name ({first_name}) occasionally
- Wrap up: "Great getting to know you {first_name}. I'll follow up with some ideas that might help."
"""

    payload = {
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "customer": {
            "number": phone,
            "name": first_name,
        },
        "assistant": {
            "name": "Franklin",
            "firstMessage": f"Hello {first_name}, this is Franklin from Ask Franklin. Thanks for signing up! I wanted to personally reach out and learn more about what you're looking for. Is now a good time?",
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "systemPrompt": system_prompt,
            },
            "voice": {
                "provider": "vapi",
                "voiceId": "Harry",
            },
            "silenceTimeoutSeconds": 30,
            "responseDelaySeconds": 0.4,
            "maxDurationSeconds": 600,
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.vapi.ai/call/phone",
            headers={
                "Authorization": f"Bearer {VAPI_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30.0,
        )

        if response.status_code == 201:
            print(f"  ✓ Call initiated to {first_name} ({phone})")
            return True
        else:
            print(f"  ✗ Failed to call {first_name}: {response.status_code} - {response.text}")
            return False


async def message_telegram(lead: dict):
    """Send Telegram message to a lead."""
    import httpx

    telegram = lead.get("telegram")
    if not telegram:
        return False

    # Clean username
    username = telegram.replace("@", "").strip()

    name = lead.get("name", "friend")
    first_name = name.split()[0] if name else "friend"
    fund_name = lead.get("fund_name", "your company")
    user_type = lead.get("user_type", "investor")

    if user_type == "investor":
        message = f"""Good day, {first_name}!

I am Franklin, your AI private banker. Thank you for signing up at askfranklin.xyz.

As an investor at {fund_name}, I'd be delighted to learn about your investment thesis and help you find the best opportunities.

To begin, might you tell me:
• What is your fund's primary investment thesis?
• What cheque sizes do you typically deploy?
• Which sectors interest you most?

Simply message me here when convenient.

— Franklin 🎩"""
    else:
        message = f"""Good day, {first_name}!

I am Franklin, your AI private banker. Thank you for signing up at askfranklin.xyz.

As a founder at {fund_name}, I'd love to understand your vision and help connect you with the right investors.

To begin, might you tell me:
• What stage is your company at?
• Are you currently raising? If so, how much?
• What kind of investors are you looking for?

I have quite a network of fund managers who might be interested.

— Franklin 🎩"""

    print(f"  → Telegram message for @{username}:")
    print(f"    (Note: User must message @askfranklin_bot first)")
    print(f"    Message preview: {message[:100]}...")

    return True


async def main():
    parser = argparse.ArgumentParser(description="Outreach to recent leads")
    parser.add_argument("--list", action="store_true", help="List recent leads")
    parser.add_argument("--call", action="store_true", help="Call leads without telegram")
    parser.add_argument("--telegram", action="store_true", help="Show telegram messages")
    parser.add_argument("--all", action="store_true", help="Do all outreach")

    args = parser.parse_args()

    if not any([args.list, args.call, args.telegram, args.all]):
        args.list = True  # Default to listing

    print("=" * 60)
    print("FRANKLIN LEAD OUTREACH")
    print("=" * 60)

    leads = get_leads()
    print(f"\nFound {len(leads)} leads\n")

    if args.list or args.all:
        print("RECENT LEADS:")
        print("-" * 60)
        for i, lead in enumerate(leads, 1):
            name = lead.get("name", "Unknown")
            email = lead.get("email", "")
            phone = lead.get("phone", "")
            telegram = lead.get("telegram", "")
            fund = lead.get("fund_name", "")
            user_type = lead.get("user_type", "")
            created = lead.get("created_at", "")[:10]

            tg_status = f"@{telegram.replace('@', '')}" if telegram else "—"

            print(f"{i:2}. {name}")
            print(f"    📧 {email}")
            print(f"    📱 {phone}")
            print(f"    💬 Telegram: {tg_status}")
            print(f"    🏢 {fund} ({user_type})")
            print(f"    📅 {created}")
            print()

    if args.call or args.all:
        print("\nINITIATING CALLS (leads without Telegram):")
        print("-" * 60)

        if not VAPI_API_KEY or not VAPI_PHONE_NUMBER_ID:
            print("  ✗ Vapi not configured")
        else:
            for lead in leads:
                if not lead.get("telegram"):  # Only call if no telegram
                    await call_lead(lead)
                    await asyncio.sleep(2)  # Rate limit

    if args.telegram or args.all:
        print("\nTELEGRAM MESSAGES:")
        print("-" * 60)

        for lead in leads:
            if lead.get("telegram"):
                await message_telegram(lead)
                print()


if __name__ == "__main__":
    asyncio.run(main())
