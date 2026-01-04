"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars not defined here
    )

    # Application
    app_name: str = "AIWealth"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/aiwealth"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # AI/LLM
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    default_llm_model: str = "claude-sonnet-4-20250514"

    # WhatsApp Provider Selection
    whatsapp_provider: str = "wasender"  # wasender, twilio, or 360dialog

    # WasenderAPI (Cheap validation - $6/mo)
    wasender_api_key: str = ""
    wasender_device_id: str = ""

    # Twilio (WhatsApp & Voice) - More reliable, higher cost
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""
    twilio_phone_number: str = ""

    # Resend (Email)
    resend_api_key: str = ""
    email_from: str = "advisor@example.com"

    # Vapi (Voice AI)
    vapi_api_key: str = ""
    vapi_phone_number_id: str = ""

    # ElevenLabs Voice
    elevenlabs_voice_id: str = "pNInz6obpgDQGcFmaJgB"  # Default: Adam

    # Twitter/X API (Free tier - public content only)
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_secret: str = ""
    twitter_bearer_token: str = ""

    # Telegram Bot
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""  # Optional secret for webhook verification

    # Amadeus (Travel API)
    amadeus_client_id: str = ""
    amadeus_client_secret: str = ""

    # Kiwi Tequila (Flight Search API) - Free for startups at tequila.kiwi.com
    kiwi_api_key: str = ""

    # Google OAuth (Calendar, etc.)
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    google_oauth_redirect_uri: str = "http://localhost:8000/oauth/google/callback"

    # Encryption key for OAuth tokens (Fernet key, generate with: Fernet.generate_key())
    oauth_encryption_key: str = ""

    # Plaid (Banking)
    plaid_client_id: str = ""
    plaid_secret: str = ""
    plaid_env: str = "sandbox"  # sandbox, development, production

    # Privacy.com (Virtual Cards)
    privacy_api_key: str = ""
    privacy_sandbox: bool = True  # Use sandbox for testing

    # Lithic (Alternative virtual card provider)
    lithic_api_key: str = ""
    lithic_sandbox: bool = True

    # User Settings
    default_approval_threshold: float = 100.0  # Auto-approve under this amount
    enable_proactive: bool = True

    # Autonomous Spending Defaults
    default_max_per_transaction: float = 500.0
    default_daily_limit: float = 2000.0
    default_monthly_limit: float = 10000.0

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
