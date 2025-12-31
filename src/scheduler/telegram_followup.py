"""Telegram Follow-up Scheduler for Fund Manager DD.

Sends follow-up messages to fund managers who:
1. Started DD but didn't complete it
2. Haven't responded in X days
3. Signed up but never messaged the bot

Run as a cron job or scheduled task.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import async_session_maker
from src.db.models import User, UserProfile, Conversation, Message
from src.adapters.telegram import TelegramAdapter
from src.config import get_settings

settings = get_settings()


# Follow-up message templates (Franklin's voice)
# Templates for FUND MANAGERS / INVESTORS
INVESTOR_TEMPLATES = {
    "incomplete_dd": """Good day, {name}!

Franklin here. We began our discourse on your fund's investment thesis some days past, but I believe we were interrupted before completion.

Might you have a moment to continue? I'm most eager to understand:
- Your typical cheque size
- The sectors you favour
- Your track record thus far

Simply reply here when convenient.

— Franklin""",

    "no_response_3_days": """Greetings, {name}!

Franklin at your service once more. I notice we haven't had the pleasure of continuing our conversation.

If you're still interested in discussing your fund's strategy and how I might be of assistance, do let me know. I remain at your disposal.

— Franklin""",

    "no_response_7_days": """Dear {name},

It has been a week since our last exchange. I trust all is well with your affairs.

Should circumstances have changed or if you require my counsel on a different matter entirely, I am here. The door, as they say, remains open.

Warm regards,
Franklin""",
}

# Templates for FOUNDERS
FOUNDER_TEMPLATES = {
    "incomplete_dd": """Good day, {name}!

Franklin here. We began discussing {company_name} some days past, but I believe we were interrupted.

Might you have a moment to continue? I'd love to understand:
- What stage your company is at
- What you're raising and at what valuation
- How I might help connect you with the right investors

Simply reply here when convenient.

— Franklin""",

    "no_response_3_days": """Greetings, {name}!

Franklin at your service once more. I notice we haven't had the pleasure of continuing our conversation about {company_name}.

If you're still seeking introductions to investors or strategic advice, do let me know. I have quite a network of fund managers who might be interested.

— Franklin""",

    "no_response_7_days": """Dear {name},

It has been a week since our last exchange regarding {company_name}. I trust the fundraising journey is progressing well.

Should you need introductions to investors, advice on pitch decks, or simply a sounding board - I remain at your disposal.

Warm regards,
Franklin""",
}

# Common templates
COMMON_TEMPLATES = {
    "new_signup_welcome_investor": """Welcome, {name}!

I am Franklin, your AI private banker. I understand you're an investor at {company_name}.

To serve you best, might you tell me:
- What is your fund's investment thesis?
- What cheque sizes do you typically deploy?
- Which sectors or stages interest you most?

I'm here to help you find the best opportunities.

— Franklin 🎩""",

    "new_signup_welcome_founder": """Welcome, {name}!

I am Franklin, your AI private banker. I understand you're building {company_name}.

To serve you best, might you tell me:
- What stage is your company at?
- Are you currently raising? If so, how much?
- What kind of investors are you looking for?

I have quite a network of fund managers who might be interested in what you're building.

— Franklin 🎩""",

    "new_signup_welcome_curious": """Welcome, {name}!

I am Franklin, your AI private banker. I understand you've expressed interest in our services.

To begin our acquaintance, might you tell me about yourself? Are you:
- A fund manager seeking deal flow?
- A founder looking for capital?
- Simply exploring what's possible?

I'm here to help, whatever your situation.

— Franklin 🎩""",
}


def get_missing_fields_text(profile: UserProfile) -> str:
    """Generate human-readable list of missing DD fields."""
    missing = []

    if not profile.investment_thesis:
        missing.append("• Your investment thesis")
    if not profile.cheque_size_min and not profile.cheque_size_max:
        missing.append("• Typical cheque size")
    if not profile.target_sectors:
        missing.append("• Target sectors")
    if not profile.fund_size_target:
        missing.append("• Fund size / AUM")
    if not profile.num_investments:
        missing.append("• Number of investments made")

    return "\n".join(missing[:3]) if missing else ""


async def get_users_needing_followup(db: AsyncSession) -> list[dict]:
    """Find users who need follow-up messages."""
    followups = []

    now = datetime.utcnow()
    three_days_ago = now - timedelta(days=3)
    seven_days_ago = now - timedelta(days=7)

    # Query users with telegram_id who might need follow-up
    result = await db.execute(
        select(User)
        .where(User.telegram_id.isnot(None))
        .where(User.is_active == True)
    )
    users = result.scalars().all()

    for user in users:
        profile = user.profile
        if not profile:
            continue

        # Get last conversation
        conv_result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user.id)
            .where(Conversation.channel == "telegram")
            .order_by(Conversation.updated_at.desc())
            .limit(1)
        )
        last_conversation = conv_result.scalar_one_or_none()

        # Get last message from user
        last_user_msg = None
        if last_conversation:
            msg_result = await db.execute(
                select(Message)
                .where(Message.conversation_id == last_conversation.id)
                .where(Message.role == "user")
                .order_by(Message.created_at.desc())
                .limit(1)
            )
            last_user_msg = msg_result.scalar_one_or_none()

        # Determine follow-up type
        followup_type = None
        last_activity = last_user_msg.created_at if last_user_msg else user.created_at

        # Check if DD is incomplete
        is_dd_incomplete = (
            profile.is_fund_manager and
            profile.profile_score < 50 and
            last_activity < three_days_ago
        )

        if is_dd_incomplete:
            if last_activity < seven_days_ago:
                followup_type = "no_response_7_days"
            elif last_activity < three_days_ago:
                if profile.profile_score > 10:
                    followup_type = "incomplete_dd"
                else:
                    followup_type = "no_response_3_days"

        # Check for new signups who never messaged
        if not last_conversation and user.created_at < three_days_ago:
            followup_type = "new_signup_welcome"

        if followup_type:
            followups.append({
                "user": user,
                "profile": profile,
                "followup_type": followup_type,
                "last_activity": last_activity,
                "telegram_id": user.telegram_id,
            })

    return followups


def get_template(followup_type: str, user_type: str) -> Optional[str]:
    """Get the appropriate template based on followup type and user type."""
    # Check for welcome templates first
    if followup_type.startswith("new_signup_welcome"):
        return COMMON_TEMPLATES.get(followup_type)

    # Get user-type specific template
    if user_type == "investor":
        return INVESTOR_TEMPLATES.get(followup_type)
    elif user_type == "founder":
        return FOUNDER_TEMPLATES.get(followup_type)
    else:
        # Default to investor templates for unknown types
        return INVESTOR_TEMPLATES.get(followup_type)


async def send_followup_message(
    adapter: TelegramAdapter,
    telegram_id: str,
    followup_type: str,
    user: User,
    profile: UserProfile,
    user_type: str = "investor",
) -> bool:
    """Send a follow-up message to a user."""
    template = get_template(followup_type, user_type)
    if not template:
        return False

    name = user.name or "friend"
    first_name = name.split()[0] if name else "friend"
    company_name = profile.fund_name or "your company"

    # Format the message
    message = template.format(
        name=first_name,
        fund_name=company_name,
        company_name=company_name,
        missing_fields=get_missing_fields_text(profile),
    )

    # Send via Telegram
    result = await adapter.send_message(telegram_id, message, parse_mode="")

    return result.get("success", False)


async def run_followup_scheduler():
    """Main scheduler function - run this as a cron job."""
    print(f"[{datetime.utcnow()}] Starting Telegram follow-up scheduler...")

    if not settings.telegram_bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN not configured")
        return

    adapter = TelegramAdapter()

    async with async_session_maker() as db:
        followups = await get_users_needing_followup(db)

        print(f"Found {len(followups)} users needing follow-up")

        for followup in followups:
            user = followup["user"]
            profile = followup["profile"]
            followup_type = followup["followup_type"]
            telegram_id = followup["telegram_id"]

            print(f"  - {user.name} (@{telegram_id}): {followup_type}")

            try:
                success = await send_followup_message(
                    adapter,
                    telegram_id,
                    followup_type,
                    user,
                    profile,
                )

                if success:
                    print(f"    ✓ Message sent")
                    # Update profile to track follow-up
                    if not profile.internal_notes:
                        profile.internal_notes = []
                    profile.internal_notes.append(
                        f"[{datetime.utcnow().isoformat()}] Sent {followup_type} follow-up via Telegram"
                    )
                else:
                    print(f"    ✗ Failed to send")
            except Exception as e:
                print(f"    ✗ Error: {e}")

        await db.commit()

    print(f"[{datetime.utcnow()}] Follow-up scheduler complete")


# ARQ worker task
async def telegram_followup_task(ctx):
    """ARQ task for scheduled follow-ups."""
    await run_followup_scheduler()


if __name__ == "__main__":
    asyncio.run(run_followup_scheduler())
