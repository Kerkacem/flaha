"""API واتساب"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import settings
from src.backend.middleware.auth import verify_whatsapp_signature
from src.backend.schemas import WhatsAppResponse
from src.backend.services.whatsapp_service import process_incoming_message, send_whatsapp
from src.database.connection import get_db
from src.database.models import WhatsAppMessage

logger = logging.getLogger("flaha.whatsapp.api")
router = APIRouter()


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str | None = None,
    hub_verify_token: str | None = None,
    hub_challenge: str | None = None,
):
    """التحقق من webhook واتساب"""
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        logger.info("✅ WhatsApp webhook verified!")
        return hub_challenge if hub_challenge else "200"
    raise HTTPException(403, "فشل التحقق من webhook")


@router.post("/webhook")
async def receive_message(request: Request, db: AsyncSession = Depends(get_db)):
    """استقبال رسائل واتساب ومعالجتها"""
    raw_body = await request.body()
    if not verify_whatsapp_signature(request, raw_body):
        logger.warning("Invalid WhatsApp webhook signature")
        if not settings.DEBUG:
            raise HTTPException(403, "❌ توقيع غير صالح")

    try:
        body = json.loads(raw_body)
    except Exception:
        raise HTTPException(400, "طلب غير صحيح")

    entry = body.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})
    messages = value.get("messages", [])

    if not messages:
        return {"status": "ok"}

    for msg in messages:
        from_number = msg.get("from", "")
        msg_type = msg.get("type", "text")

        text = None
        media_url = None

        if msg_type == "text":
            text = msg.get("text", {}).get("body", "")
        elif msg_type in ("image", "document"):
            media_url = msg.get(msg_type, {}).get("link", "")
            text = msg.get(msg_type, {}).get("caption", "")

        wa_msg = WhatsAppMessage(
            from_number=from_number,
            to_number="system",
            message_type=msg_type,
            body=text,
            media_url=media_url,
            wa_message_id=msg.get("id", ""),
            direction="incoming",
        )
        db.add(wa_msg)
        await db.flush()

        try:
            result = await process_incoming_message(from_number, text, media_url, db)
            response_text = result.get("response") or result.get("message", "")

            if response_text:
                await send_whatsapp(to=from_number, text=response_text)

            wa_msg.processed = True
            wa_msg.intent = result.get("intent", "")

        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            await send_whatsapp(
                to=from_number,
                text="😅 حدث خطأ. الرجاء المحاولة مرة أخرى لاحقاً.",
            )

        await db.flush()

    return {"status": "ok"}


class SendMessageRequest(BaseModel):
    to: str
    text: str


class SendTemplateRequest(BaseModel):
    to: str
    template_name: str
    parameters: list[str] = []


@router.post("/send", response_model=WhatsAppResponse)
async def send_message_api(body: SendMessageRequest):
    """إرسال رسالة عبر واتساب"""
    if not settings.WHATSAPP_API_TOKEN:
        return WhatsAppResponse(
            status="simulated",
            message="⚠️ وضع المحاكاة: تمت محاكاة الإرسال",
            data={"to": body.to, "text_preview": body.text[:50] + "..."},
        )

    result = await send_whatsapp(to=body.to, text=body.text)
    return WhatsAppResponse(
        status="sent" if result.get("status") == "sent" else "error",
        message="تم إرسال الرسالة" if result.get("status") == "sent" else "فشل الإرسال",
        data=result,
    )


@router.post("/send-template", response_model=WhatsAppResponse)
async def send_template_api(body: SendTemplateRequest):
    """إرسال قالب واتساب معتمد"""
    if not settings.WHATSAPP_API_TOKEN:
        return WhatsAppResponse(status="simulated", message="WhatsApp API غير مهيأ")

    from src.backend.services.whatsapp_service import send_template_message
    result = await send_template_message(body.to, body.template_name, body.parameters)
    return WhatsAppResponse(
        status="sent" if result.get("status") == "sent" else "error",
        message=result.get("status", "unknown"),
    )
