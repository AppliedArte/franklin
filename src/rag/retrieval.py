"""Retrieval service for RAG queries."""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Document, DocumentChunk, UserFact, Message
from src.rag.embeddings import EmbeddingService


@dataclass
class RetrievedContext:
    """Container for retrieved RAG context."""

    document_chunks: list[dict]
    user_facts: list[dict]
    recent_messages: list[dict]

    def to_prompt_context(self) -> str:
        """Format retrieved context for injection into prompts."""
        parts = []

        if self.user_facts:
            facts_text = "\n".join([f"- {f['fact']}" for f in self.user_facts])
            parts.append(f"## What I Know About This Person\n{facts_text}")

        if self.document_chunks:
            docs_text = "\n\n".join([
                f"**From {c['document_title']}:**\n{c['content']}"
                for c in self.document_chunks
            ])
            parts.append(f"## Relevant Documents\n{docs_text}")

        if self.recent_messages:
            msgs_text = "\n".join([
                f"{'User' if m['role'] == 'user' else 'Franklin'}: {m['content'][:200]}..."
                if len(m['content']) > 200 else
                f"{'User' if m['role'] == 'user' else 'Franklin'}: {m['content']}"
                for m in self.recent_messages
            ])
            parts.append(f"## Recent Conversation\n{msgs_text}")

        return "\n\n".join(parts) if parts else ""


class RetrievalService:
    """Retrieve relevant context for RAG."""

    def __init__(self):
        self.embedder = EmbeddingService()

    async def retrieve_for_query(
        self,
        db: AsyncSession,
        user_id: str,
        query: str,
        top_k_chunks: int = 5,
        top_k_facts: int = 10,
        include_recent_messages: int = 5,
    ) -> RetrievedContext:
        """Retrieve all relevant context for a user query."""
        # Generate query embedding
        query_embedding = await self.embedder.embed_text(query)

        # Retrieve in parallel
        chunks = await self._retrieve_document_chunks(
            db, user_id, query_embedding, top_k_chunks
        )
        facts = await self._retrieve_user_facts(
            db, user_id, query_embedding, top_k_facts
        )
        messages = await self._get_recent_messages(
            db, user_id, include_recent_messages
        )

        return RetrievedContext(
            document_chunks=chunks,
            user_facts=facts,
            recent_messages=messages,
        )

    async def _retrieve_document_chunks(
        self,
        db: AsyncSession,
        user_id: str,
        query_embedding: list[float],
        top_k: int,
    ) -> list[dict]:
        """Retrieve most similar document chunks using pgvector."""
        # Use raw SQL for vector similarity search
        query = text("""
            SELECT
                dc.id,
                dc.content,
                dc.chunk_index,
                dc.page_number,
                dc.section_title,
                d.title as document_title,
                d.doc_type,
                d.filename,
                dc.embedding <-> :query_embedding as distance
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE d.user_id = :user_id
                AND dc.embedding IS NOT NULL
            ORDER BY dc.embedding <-> :query_embedding
            LIMIT :top_k
        """)

        result = await db.execute(
            query,
            {
                "user_id": user_id,
                "query_embedding": str(query_embedding),
                "top_k": top_k,
            },
        )

        rows = result.fetchall()
        return [
            {
                "id": row.id,
                "content": row.content,
                "chunk_index": row.chunk_index,
                "page_number": row.page_number,
                "section_title": row.section_title,
                "document_title": row.document_title,
                "doc_type": row.doc_type,
                "filename": row.filename,
                "distance": row.distance,
            }
            for row in rows
        ]

    async def _retrieve_user_facts(
        self,
        db: AsyncSession,
        user_id: str,
        query_embedding: list[float],
        top_k: int,
    ) -> list[dict]:
        """Retrieve most relevant user facts."""
        query = text("""
            SELECT
                id,
                category,
                fact,
                source,
                confidence,
                created_at,
                embedding <-> :query_embedding as distance
            FROM user_facts
            WHERE user_id = :user_id
                AND embedding IS NOT NULL
            ORDER BY embedding <-> :query_embedding
            LIMIT :top_k
        """)

        result = await db.execute(
            query,
            {
                "user_id": user_id,
                "query_embedding": str(query_embedding),
                "top_k": top_k,
            },
        )

        rows = result.fetchall()
        return [
            {
                "id": row.id,
                "category": row.category,
                "fact": row.fact,
                "source": row.source,
                "confidence": row.confidence,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "distance": row.distance,
            }
            for row in rows
        ]

    async def _get_recent_messages(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int,
    ) -> list[dict]:
        """Get recent messages from user's conversations."""
        query = text("""
            SELECT
                m.id,
                m.role,
                m.content,
                m.created_at,
                m.channel
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE c.user_id = :user_id
            ORDER BY m.created_at DESC
            LIMIT :limit
        """)

        result = await db.execute(
            query,
            {"user_id": user_id, "limit": limit},
        )

        rows = result.fetchall()
        # Reverse to get chronological order
        return [
            {
                "id": row.id,
                "role": row.role,
                "content": row.content,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "channel": row.channel,
            }
            for row in reversed(rows)
        ]

    async def get_all_user_facts(
        self,
        db: AsyncSession,
        user_id: str,
        category: Optional[str] = None,
    ) -> list[dict]:
        """Get all facts for a user, optionally filtered by category."""
        if category:
            query = select(UserFact).where(
                UserFact.user_id == user_id,
                UserFact.category == category,
            ).order_by(UserFact.created_at.desc())
        else:
            query = select(UserFact).where(
                UserFact.user_id == user_id,
            ).order_by(UserFact.created_at.desc())

        result = await db.execute(query)
        facts = result.scalars().all()

        return [
            {
                "id": f.id,
                "category": f.category,
                "fact": f.fact,
                "source": f.source,
                "confidence": f.confidence,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in facts
        ]

    async def get_user_documents(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> list[dict]:
        """Get all documents for a user."""
        query = select(Document).where(
            Document.user_id == user_id,
        ).order_by(Document.created_at.desc())

        result = await db.execute(query)
        docs = result.scalars().all()

        return [
            {
                "id": d.id,
                "filename": d.filename,
                "title": d.title,
                "doc_type": d.doc_type,
                "is_processed": d.is_processed,
                "chunk_count": d.chunk_count,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in docs
        ]

    async def close(self):
        """Cleanup resources."""
        await self.embedder.close()
