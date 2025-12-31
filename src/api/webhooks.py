"""Webhook endpoints for communication channels."""

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.agents.orchestrator import ConversationOrchestrator

router = APIRouter()


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle incoming WhatsApp messages.

    Supports multiple providers:
    - WasenderAPI (JSON body)
    - Twilio (form data with TwiML response)
    """
    from src.adapters.whatsapp import WhatsAppAdapter
    from src.config import get_settings
    from fastapi.responses import Response

    settings = get_settings()
    adapter = WhatsAppAdapter()

    # Parse based on content type (Twilio uses form, WasenderAPI uses JSON)
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        # WasenderAPI webhook (JSON)
        data = await request.json()
        parsed = adapter.parse_webhook(data)
    else:
        # Twilio webhook (form data)
        form_data = await request.form()
        parsed = adapter.parse_webhook(dict(form_data))

    from_number = parsed.get("from_number", "")
    body = parsed.get("message_body", "")
    message_id = parsed.get("message_id", "")

    if not from_number or not body:
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Process through orchestrator
    orchestrator = ConversationOrchestrator(db)
    response = await orchestrator.handle_message(
        channel="whatsapp",
        channel_user_id=from_number,
        message_content=body,
        metadata={"message_id": message_id, "provider": settings.whatsapp_provider},
    )

    # Send response back via WhatsApp
    await adapter.send_message(from_number, response)

    # Return appropriate response based on provider
    if settings.whatsapp_provider == "twilio":
        # Return TwiML for Twilio
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response}</Message>
</Response>"""
        return Response(content=twiml, media_type="application/xml")
    else:
        # Return JSON for other providers
        return {"status": "ok", "response_sent": True}


@router.post("/email")
async def email_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle incoming email messages."""
    data = await request.json()

    from_email = data.get("from")
    subject = data.get("subject", "")
    body = data.get("text", "") or data.get("html", "")

    if not from_email or not body:
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Process through orchestrator
    orchestrator = ConversationOrchestrator(db)
    response = await orchestrator.handle_message(
        channel="email",
        channel_user_id=from_email,
        message_content=body,
        metadata={"subject": subject},
    )

    return {"status": "processed", "response_queued": True}


@router.get("/whatsapp")
async def whatsapp_verify(request: Request):
    """Verify WhatsApp webhook (for Twilio/Meta verification)."""
    # For Meta Business API verification
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    # TODO: Verify against configured token
    if mode == "subscribe" and challenge:
        return int(challenge)

    return {"status": "ok"}


@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle incoming Telegram messages.

    Telegram sends updates as JSON with message/callback_query.
    """
    from src.adapters.telegram import TelegramAdapter

    data = await request.json()
    adapter = TelegramAdapter()
    parsed = adapter.parse_webhook(data)

    # Get chat_id and user info
    chat_id = parsed.get("chat_id")
    user_id = str(parsed.get("user_id", ""))
    body = parsed.get("message_body", "")
    is_callback = parsed.get("is_callback", False)
    first_name = parsed.get("first_name", "")

    if not chat_id or not body:
        return {"ok": True}  # Telegram expects 200 OK even for ignored updates

    # Answer callback query if applicable
    if is_callback and parsed.get("callback_query_id"):
        await adapter.answer_callback_query(parsed["callback_query_id"])

    # Process through orchestrator
    orchestrator = ConversationOrchestrator(db)
    response = await orchestrator.handle_message(
        channel="telegram",
        channel_user_id=user_id,
        message_content=body,
        metadata={
            "chat_id": chat_id,
            "first_name": first_name,
            "username": parsed.get("username", ""),
            "message_type": parsed.get("message_type", "text"),
        },
    )

    # Send response back via Telegram
    await adapter.send_message(chat_id, response)

    return {"ok": True}


@router.post("/vapi")
async def vapi_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Vapi Custom LLM webhook.

    Vapi sends transcribed user speech, we return AI response.
    """
    data = await request.json()
    message_type = data.get("message", {}).get("type")

    # Handle different Vapi webhook events
    if message_type == "transcript":
        # User said something - generate response
        transcript = data.get("message", {}).get("transcript", "")
        call_id = data.get("call", {}).get("id", "")
        customer_number = data.get("call", {}).get("customer", {}).get("number", "")

        if not transcript:
            return {"response": ""}

        # Process through orchestrator
        orchestrator = ConversationOrchestrator(db)
        response = await orchestrator.handle_message(
            channel="voice",
            channel_user_id=customer_number,
            message_content=transcript,
            metadata={"call_id": call_id, "source": "vapi"},
        )

        return {"response": response}

    elif message_type == "end-of-call-report":
        # Call ended - log summary
        call_id = data.get("call", {}).get("id")
        duration = data.get("message", {}).get("durationSeconds")
        summary = data.get("message", {}).get("summary")
        # TODO: Store call summary for future context
        return {"status": "received"}

    elif message_type == "hang":
        # User hung up
        return {"status": "received"}

    return {"status": "ok"}
