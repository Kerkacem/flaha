from __future__ import annotations

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import settings

# ─── Send WhatsApp Message ──────────────────────────────────────


async def send_whatsapp(to: str, text: str, media_url: str | None = None) -> dict:
    """إرسال رسالة عبر WhatsApp Business API"""
    if not settings.WHATSAPP_API_TOKEN:
        return {"status": "error", "message": "WhatsApp API غير مهيأ"}

    url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text" if not media_url else "image",
        "text": {"body": text} if not media_url else None,
        "image": {"link": media_url} if media_url else None,
    }
    data = {k: v for k, v in data.items() if v is not None}

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=data, headers=headers)
        return resp.json()


async def send_template_message(to: str, template_name: str, parameters: list[str]) -> dict:
    """إرسال قالب واتساب معتمد"""
    if not settings.WHATSAPP_API_TOKEN:
        return {"status": "error", "message": "WhatsApp API غير مهيأ"}

    url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "ar"},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": p} for p in parameters],
                }
            ],
        },
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=data, headers=headers)
        return resp.json()


# ─── Session Store ───────────────────────────────────────────────

whatsapp_sessions: dict[str, dict] = {}

# ─── Process Incoming Message ───────────────────────────────────


async def process_incoming_message(from_number: str, body: str | None, media_url: str | None, db: AsyncSession):
    """تحليل الرسالة الواردة وتحديد النية"""
    from src.backend.services.marketplace_service import handle_sell_intent

    if not body:
        return {"intent": "unknown", "message": "لم أفهم الرسالة"}

    body = body.strip()

    # Intent detection based on keywords
    if any(kw in body for kw in ["عندي", "نبيع", "بيع", "نبي نبيع"]):
        return await handle_sell_intent(from_number, body, db)

    elif any(kw in body for kw in ["نشتري", "نبي نشتري", "شراء"]):
        return {"intent": "buy", "message": "نعم، نبي نشتري"}

    elif any(kw in body for kw in ["دعم", "مساعدة", "اعانة"]):
        return {"intent": "gov_support", "message": "نعم، نحتاج دعم"}

    elif any(kw in body for kw in ["مرض", "علاج", "مبيد", "نبات", "زرع"]):
        return {"intent": "advisory", "message": "نعم، استشارة فلاحية"}

    return {"intent": "unknown", "message": "مرحباً بك في فلاحة 🌾\n\nأرسل:\n• 'عندي' لبيع منتج\n• 'نشتري' لشراء منتج\n• 'دعم' للاستفسار عن الدعم\n• 'مرض' لتشخيص مرض النبات"}
