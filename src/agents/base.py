"""Base agent class for all AI agents."""

from abc import ABC, abstractmethod
from typing import Optional

from anthropic import AsyncAnthropic

from src.config import get_settings

settings = get_settings()


class BaseAgent(ABC):
    """Base class for all AI agents."""

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = model or settings.default_llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    async def generate(
        self,
        messages: list[dict],
        system_override: Optional[str] = None,
    ) -> str:
        """Generate a response from the LLM."""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_override or self.system_prompt,
            messages=messages,
        )

        return response.content[0].text

    async def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        system_override: Optional[str] = None,
    ) -> dict:
        """Generate a response with tool use capability."""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_override or self.system_prompt,
            messages=messages,
            tools=tools,
        )

        return {
            "content": response.content,
            "stop_reason": response.stop_reason,
        }
