"""Web chat API endpoints."""

from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.db.database import get_db
from src.agents.orchestrator import ConversationOrchestrator

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message request."""

    user_id: str
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat message response."""

    response: str
    conversation_id: str
    profile_score: int


@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat: ChatMessage,
    db: AsyncSession = Depends(get_db),
):
    """Send a chat message and get AI response."""
    orchestrator = ConversationOrchestrator(db)

    response, conversation_id, profile_score = await orchestrator.handle_message(
        channel="web",
        channel_user_id=chat.user_id,
        message_content=chat.message,
        conversation_id=chat.conversation_id,
        return_metadata=True,
    )

    return ChatResponse(
        response=response,
        conversation_id=conversation_id,
        profile_score=profile_score,
    )


@router.websocket("/ws/{user_id}")
async def websocket_chat(
    websocket: WebSocket,
    user_id: str,
):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()

    # Get database session
    async with get_db() as db:
        orchestrator = ConversationOrchestrator(db)

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_json()
                message = data.get("message", "")

                if not message:
                    continue

                # Process message
                response = await orchestrator.handle_message(
                    channel="web",
                    channel_user_id=user_id,
                    message_content=message,
                )

                # Send response back
                await websocket.send_json({
                    "type": "message",
                    "content": response,
                })

        except WebSocketDisconnect:
            pass  # Client disconnected


@router.get("/history/{user_id}")
async def get_chat_history(
    user_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get chat history for a user."""
    from sqlalchemy import select
    from src.db.models import User, Conversation, Message

    # Find user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get recent conversations with messages
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(5)
    )
    conversations = result.scalars().all()

    history = []
    for conv in conversations:
        for msg in conv.messages[-limit:]:
            history.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "channel": msg.channel,
                "created_at": msg.created_at.isoformat(),
            })

    return {"user_id": user_id, "messages": history}
