"""إدارة الإشعارات والتنبيهات للفلاحين"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import select

from src.backend.services.ussd_service import send_ussd
from src.backend.services.whatsapp_service import send_whatsapp
from src.database.connection import async_session_factory
from src.database.models import Farmer, Product


class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationChannel(str, Enum):
    WHATSAPP = "whatsapp"
    USSD = "ussd"
    BOTH = "both"


TEMPLATES: dict[str, str] = {
    "welcome": (
        "🌾 مرحباً {name} في **فلاحة**!\n\n"
        "أنا وكيلك الفلاحي الذكي. يمكنني مساعدتك في:\n"
        "• بيع منتجاتك الفلاحية\n"
        "• شراء مستلزمات الإنتاج\n"
        "• تشخيص أمراض النباتات\n"
        "• معلومات الطقس\n"
        "• التمويل والقروض\n\n"
        "أرسل **قائمة** لعرض الخدمات المتاحة"
    ),
    "product_sold": (
        "✅ تم بيع {product_name}! 🎉\n\n"
        "الكمية: {quantity} {unit}\n"
        "السعر: {price} دج/{unit}\n"
        "المجموع: {total} دج\n\n"
        "يرجى تجهيز المنتج للتوصيل خلال 24 ساعة"
    ),
    "new_order": (
        "🛒 طلب جديد!\n\n"
        "المنتج: {product_name}\n"
        "الكمية: {quantity} {unit}\n"
        "العنوان: {address}\n\n"
        "يرجى تأكيد الطلب خلال ساعتين"
    ),
    "weather_alert": (
        "🌤️ **تنبيه فلاحي**\n\n"
        "{advice}\n\n"
        "— وكيل فلاحة"
    ),
    "payment_received": (
        "💰 تم استلام الدفع!\n\n"
        "المبلغ: {amount} دج\n"
        "الصفقة: #{txn_id}\n"
        "المنتج: {product_name}\n\n"
        "✅ يمكنك الآن تسليم المنتج"
    ),
    "delivery_update": (
        "📦 تحديث التوصيل\n\n"
        "الصفقة #{txn_id}: {status}\n"
        "المنتج: {product_name}\n"
        "{details}"
    ),
    "credit_score_update": (
        "📊 تحديث الدرجة الائتمانية\n\n"
        "درجتك الجديدة: {score}/100\n"
        "التغيير: {change:+d}\n\n"
        "{advice}"
    ),
    "loan_approved": (
        "🎉 **تمت الموافقة على قرضك!**\n\n"
        "المبلغ: {amount} دج\n"
        "المدة: {duration} شهراً\n"
        "الفائدة: {interest}%\n\n"
        "سيتم تحويل المبلغ إلى حسابك خلال 48 ساعة"
    ),
    "diaspora_order": (
        "🌍 طلب جديد من الجالية!\n\n"
        "المنتج: {product_name}\n"
        "الكمية: {quantity} {unit}\n"
        "الوجهة: {country}\n"
        "المبلغ: {amount} EUR\n\n"
        "يرجى تجهيز الطلب للشحن الدولي"
    ),
    "gov_support": (
        "🏛️ برنامج دعم حكومي جديد!\n\n"
        "{program_name}\n"
        "نوع الدعم: {support_type}\n"
        "الموعد النهائي: {deadline}\n"
        "للتسجيل: أرسل **تسجيل {program_id}**"
    ),
}


async def send_notification(
    farmer_id: int,
    template_key: str,
    template_vars: dict,
    channel: NotificationChannel = NotificationChannel.WHATSAPP,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
) -> dict:
    """إرسال إشعار لفلاح معين"""
    async with async_session_factory() as db:
        farmer = await db.get(Farmer, farmer_id)
        if not farmer:
            return {"status": "error", "error": "فلاح غير موجود"}

        message = TEMPLATES.get(template_key, template_key)
        try:
            text = message.format(**template_vars)
        except KeyError as e:
            return {"status": "error", "error": f"متغير ناقص: {e}"}

        results = {}
        if channel in (NotificationChannel.WHATSAPP, NotificationChannel.BOTH):
            result = await send_whatsapp(to=farmer.phone, text=text)
            results["whatsapp"] = result.get("status", "error")

        if channel in (NotificationChannel.USSD, NotificationChannel.BOTH):
            result = await send_ussd(phone=farmer.phone, text=text)
            results["ussd"] = result.get("status", "error")

        return {"status": "sent", "channels": results, "message": text}


async def broadcast_notification(
    template_key: str,
    template_vars: dict,
    wilaya: str | None = None,
    channel: NotificationChannel = NotificationChannel.WHATSAPP,
) -> dict:
    """إرسال إشعار جماعي لمجموعة من الفلاحين"""
    async with async_session_factory() as db:
        q = select(Farmer).where(Farmer.is_verified == True)
        if wilaya:
            q = q.where(Farmer.wilaya == wilaya)
        result = await db.execute(q)
        farmers = result.scalars().all()

    message = TEMPLATES.get(template_key, template_key)
    try:
        text = message.format(**template_vars)
    except KeyError as e:
        return {"status": "error", "error": f"متغير ناقص: {e}"}

    if channel not in (NotificationChannel.WHATSAPP, NotificationChannel.BOTH) or not farmers:
        return {"status": "ok", "sent": 0, "total": len(farmers)}

    results = await asyncio.gather(
        *(send_whatsapp(to=f.phone, text=text) for f in farmers),
        return_exceptions=True,
    )
    sent = sum(1 for r in results if not isinstance(r, Exception))

    return {"status": "sent", "count": sent, "total": len(farmers)}


async def check_product_expiry():
    """فحص المنتجات المنتهية وإخطار الفلاحين"""
    async with async_session_factory() as db:
        thirty_days_ago = datetime.now() - timedelta(days=30)
        result = await db.execute(
            select(Product).where(
                Product.status == "available",
                Product.created_at < thirty_days_ago,
            )
        )
        old_products = result.scalars().all()

        notified = 0
        for product in old_products:
            farmer = await db.get(Farmer, product.farmer_id)
            if farmer:
                await send_whatsapp(
                    to=farmer.phone,
                    text=f"⏰ تنبيه: منتجك [{product.name}] لم يبع منذ 30 يوماً.\n"
                         f"أنصح بتخفيض السعر أو تجديد الإعلان.\n"
                         f"السعر الحالي: {product.price} دج/{product.unit}",
                )
                notified += 1

        return {"checked": len(old_products), "notified": notified}
