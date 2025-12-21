"""Embedding service for RAG - uses OpenAI text-embedding-3-small."""

import asyncio
from typing import Optional

import httpx

from src.config import get_settings

settings = get_settings()


class EmbeddingService:
    """Generate embeddings using OpenAI's API."""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.api_key = settings.openai_api_key
        self.base_url = "https://api.openai.com/v1/embeddings"
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        embeddings = await self.embed_texts([text])
        return embeddings[0]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts in a single API call."""
        if not texts:
            return []

        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        client = await self._get_client()

        response = await client.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "input": texts,
            },
        )

        response.raise_for_status()
        data = response.json()

        # Sort by index to ensure order matches input
        embeddings = sorted(data["data"], key=lambda x: x["index"])
        return [e["embedding"] for e in embeddings]

    async def embed_texts_batch(
        self, texts: list[str], batch_size: int = 100
    ) -> list[list[float]]:
        """Embed texts in batches to avoid API limits."""
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            embeddings = await self.embed_texts(batch)
            all_embeddings.extend(embeddings)

            # Small delay between batches to avoid rate limits
            if i + batch_size < len(texts):
                await asyncio.sleep(0.1)

        return all_embeddings

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
