"""Background worker tasks using ARQ (async Redis queue)."""

from arq import create_pool
from arq.connections import RedisSettings

from src.config import get_settings

settings = get_settings()


async def send_whatsapp_message(ctx, to_number: str, message: str):
    """Background task to send WhatsApp message."""
    from src.adapters.whatsapp import WhatsAppAdapter

    adapter = WhatsAppAdapter()
    result = await adapter.send_message(to_number, message)
    return result


async def send_email(ctx, to_email: str, subject: str, body: str, html_body: str = None):
    """Background task to send email."""
    from src.adapters.email import EmailAdapter

    adapter = EmailAdapter()
    result = await adapter.send_email(to_email, subject, body, html_body)
    return result


async def initiate_voice_call(ctx, phone_number: str, assistant_config: dict = None):
    """Background task to initiate voice call."""
    from src.adapters.voice import VoiceAdapter

    adapter = VoiceAdapter()
    result = await adapter.initiate_call(phone_number, assistant_config)
    return result


async def send_telegram_message(ctx, chat_id: str | int, message: str, parse_mode: str = "HTML"):
    """Background task to send Telegram message."""
    from src.adapters.telegram import TelegramAdapter

    adapter = TelegramAdapter()
    result = await adapter.send_message(chat_id, message, parse_mode)
    return result


async def telegram_followup_scheduler(ctx):
    """
    Scheduled task: Send follow-up messages to fund managers via Telegram.

    Checks for:
    - Incomplete DD profiles (>3 days inactive)
    - Users who haven't responded (>7 days)
    - New signups who never messaged

    Schedule: Daily at 10am
    """
    from src.scheduler.telegram_followup import run_followup_scheduler

    await run_followup_scheduler()


async def update_profile_embeddings(ctx, user_id: str):
    """Background task to update user profile embeddings for vector search."""
    # TODO: Implement embedding generation for profile data
    pass


async def process_referral_followup(ctx, referral_id: str):
    """Background task to follow up on referrals."""
    # TODO: Implement referral follow-up logic
    pass


async def generate_conversation_summary(ctx, conversation_id: str):
    """Background task to generate conversation summary."""
    # TODO: Implement conversation summarization
    pass


# =============================================================================
# Twitter Content Jobs (Scheduled)
# =============================================================================


async def post_wisdom_tweet(ctx):
    """
    Scheduled task: Post a wisdom tweet.

    Schedule: 2-3 times per week
    """
    from src.adapters.twitter import TwitterAdapter
    from src.agents.content_agent import ContentAgent

    twitter = TwitterAdapter()
    if not twitter.is_configured:
        return {"success": False, "error": "Twitter not configured"}

    content_agent = ContentAgent()
    tweet = await content_agent.generate_wisdom_tweet()

    result = await twitter.post_tweet(tweet)
    return result


async def post_market_commentary(ctx, market_context: str = None):
    """
    Scheduled task: Post market commentary.

    Schedule: Daily at market close
    """
    from src.adapters.twitter import TwitterAdapter
    from src.agents.content_agent import ContentAgent

    twitter = TwitterAdapter()
    if not twitter.is_configured:
        return {"success": False, "error": "Twitter not configured"}

    content_agent = ContentAgent()
    tweet = await content_agent.generate_market_commentary(market_context)

    result = await twitter.post_tweet(tweet)
    return result


async def post_educational_thread(ctx, topic: str):
    """
    Scheduled task: Post an educational thread.

    Schedule: Weekly (e.g., Sunday evening)
    """
    from src.adapters.twitter import TwitterAdapter
    from src.agents.content_agent import ContentAgent

    twitter = TwitterAdapter()
    if not twitter.is_configured:
        return {"success": False, "error": "Twitter not configured"}

    content_agent = ContentAgent()
    tweets = await content_agent.generate_educational_thread(topic)

    result = await twitter.post_thread(tweets)
    return result


async def post_fixed_income_insight(ctx):
    """Scheduled task: Post fixed income insight."""
    from src.adapters.twitter import TwitterAdapter
    from src.agents.content_agent import ContentAgent

    twitter = TwitterAdapter()
    if not twitter.is_configured:
        return {"success": False, "error": "Twitter not configured"}

    content_agent = ContentAgent()
    tweet = await content_agent.generate_fixed_income_insight()

    result = await twitter.post_tweet(tweet)
    return result


async def post_alternatives_insight(ctx):
    """Scheduled task: Post alternatives/funds insight."""
    from src.adapters.twitter import TwitterAdapter
    from src.agents.content_agent import ContentAgent

    twitter = TwitterAdapter()
    if not twitter.is_configured:
        return {"success": False, "error": "Twitter not configured"}

    content_agent = ContentAgent()
    tweet = await content_agent.generate_alternatives_insight()

    result = await twitter.post_tweet(tweet)
    return result


async def startup(ctx):
    """Worker startup - initialize connections."""
    pass


async def shutdown(ctx):
    """Worker shutdown - cleanup."""
    pass


class WorkerSettings:
    """ARQ worker settings."""

    functions = [
        # Communication
        send_whatsapp_message,
        send_email,
        initiate_voice_call,
        send_telegram_message,
        # Profile & Conversation
        update_profile_embeddings,
        process_referral_followup,
        generate_conversation_summary,
        # Telegram Follow-up (scheduled)
        telegram_followup_scheduler,
        # Twitter Content (scheduled)
        post_wisdom_tweet,
        post_market_commentary,
        post_educational_thread,
        post_fixed_income_insight,
        post_alternatives_insight,
    ]

    on_startup = startup
    on_shutdown = shutdown

    redis_settings = RedisSettings.from_dsn(settings.redis_url)

    # Cron jobs for scheduled tasks
    # Note: Actual scheduling requires ARQ cron jobs setup
    # Example cron jobs (configure in production):
    # cron_jobs = [
    #     # Telegram follow-up - daily at 10am
    #     cron(telegram_followup_scheduler, hour=10, minute=0),
    #
    #     # Twitter posting
    #     cron(post_wisdom_tweet, hour=14, minute=0, weekday={1, 3, 5}),  # Mon/Wed/Fri 2pm
    #     cron(post_market_commentary, hour=16, minute=30, weekday={0, 1, 2, 3, 4}),  # Weekdays 4:30pm
    #     cron(post_educational_thread, hour=18, minute=0, weekday={6}),  # Sunday 6pm
    # ]
