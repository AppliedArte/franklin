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

    # Twitter/X API (Free tier - public content only)
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_secret: str = ""
    twitter_bearer_token: str = ""

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
