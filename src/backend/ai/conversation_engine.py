"""
محرك المحادثة — يدير تدفق المحادثة مع الفلاح
يستخدم Gemini لتحليل النوايا والمقاصد
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.ai.nlp_engine import FlahaNLPEngine
from src.backend.services.marketplace_service import handle_sell_intent
from src.backend.services.whatsapp_service import whatsapp_sessions
from src.database.models import Farmer, Product

logger = logging.getLogger("flaha.conversation")


async def process_message(
    from_number: str,
    text: str | None,
    media_url: str | None,
    db: AsyncSession,
) -> dict:
    """معالجة رسالة واردة — تستخدم Gemini إن وجد"""
    session = whatsapp_sessions.get(from_number, {"state": "idle", "data": {"phone": from_number}})

    if text:
        text = text.strip()

    # صورة ← تشخيص
    if media_url:
        return {
            "intent": "advisory",
            "response": "📷 تم استلام الصورة.\n"
                        "أرسل **نوع الزرع** (مثال: طماطم) للتشخيص الدقيق",
        }

    if not text:
        return {"intent": "unknown", "response": "أرسل **مرحبا** للبدء 🌾"}

    # إذا في منتصف محادثة
    if session["state"] != "idle":
        return await _handle_conversation_step(from_number, text, session, db)

    # تحليل النية
    nlp = FlahaNLPEngine()
    nlp_result = await nlp.analyze_async(text)
    intent = nlp_result["intent"]

    return await _start_new_conversation(from_number, text, intent, nlp_result, db)


async def _start_new_conversation(
    phone: str,
    text: str,
    intent: str,
    nlp_result: dict,
    db: AsyncSession,
) -> dict:
    """بدء محادثة جديدة حسب النية"""
    responses = {
        "sell": {
            "state": "awaiting_product_name",
            "response": "حسناً 👨‍🌾\nأرسل **اسم المنتج** الي تحب تبيع؟\n(مثال: طماطم)",
        },
        "buy": {
            "state": "awaiting_search_product",
            "response": "🛒 أرسل **اسم المنتج** الي تحب تشتري؟",
        },
        "advisory": {
            "state": "awaiting_crop_type",
            "response": "🌱 أرسل **نوع الزرع** (مثال: طماطم) أو صورة للنبات",
        },
        "weather": {
            "state": "awaiting_weather_wilaya",
            "response": "🌤️ **حالة الطقس**\nأرسل اسم **الولاية**",
        },
        "price": {
            "state": "awaiting_price_product",
            "response": "📊 **أسعار السوق**\nأرسل اسم المنتج لمعرفة سعره",
        },
        "loan": {
            "state": "awaiting_loan_type",
            "response": (
                "💳 **التمويل والقروض**\n\n"
                "1️⃣ قرض BADR (بدون فوائد)\n"
                "2️⃣ قرض CPA فلاح\n"
                "3️⃣ الدرجة الائتمانية\n"
                "أرسل الرقم"
            ),
        },
        "gov_support": {
            "state": "awaiting_gov_option",
            "response": (
                "🏛️ **الدعم الحكومي**\n\n"
                "1️⃣ FNDIA — دعم صغار الفلاحين\n"
                "2️⃣ FGVA — ضمان القروض\n"
                "3️⃣ PNDA — دعم المدخلات\n"
                "4️⃣ التأمين الفلاحي\n"
                "أرسل الرقم"
            ),
        },
        "diaspora": {
            "state": "idle",
            "response": (
                "🌍 **باقات الجالية**\n\n"
                "1️⃣ 5 كغ/شهر — $49 🇫🇷\n"
                "2️⃣ 15 كغ/شهر — $99 🇫🇷🇪🇺\n"
                "3️⃣ 30 كغ/شهر — $149 🌍\n"
                "4️⃣ 50 كغ/شهر — $199 🌍\n\n"
                "للاشتراك: **اشتراك [رقم]**"
            ),
        },
    }

    entry = responses.get(intent, {
        "state": "idle",
        "response": (
            "🌾 **مرحباً بك في فلاحة!**\n\n"
            "أنا وكيلك الفلاحي الذكي 🤖\n\n"
            "📌 **ما يمكنني فعله:**\n"
            "• **عندي** ← بيع منتج\n"
            "• **نشتري** ← شراء منتج\n"
            "• **مرض** ← تشخيص الأمراض\n"
            "• **الطقس** ← حالة الطقس\n"
            "• **السعر** ← أسعار السوق\n"
            "• **دعم** ← الدعم الحكومي\n"
            "• **قرض** ← تمويل وقروض\n"
            "• **جالية** ← باقات الجالية"
        ),
    })

    whatsapp_sessions[phone] = {
        "state": entry["state"],
        "data": {"phone": phone, "original_text": text},
    }

    return {"intent": intent, "response": entry["response"]}


async def _handle_conversation_step(
    phone: str,
    text: str,
    session: dict,
    db: AsyncSession,
) -> dict:
    """معالجة خطوة في المحادثة"""
    state = session["state"]
    data = session["data"]

    handlers = {
        "awaiting_product_name": _handle_product_name,
        "awaiting_product_qty": _handle_product_qty,
        "awaiting_product_unit": _handle_product_unit,
        "awaiting_product_price": _handle_product_price,
        "awaiting_product_wilaya": _handle_product_wilaya,
        "awaiting_search_product": _handle_search_product,
        "awaiting_product_selection": _handle_product_selection,
        "awaiting_buy_qty": _handle_buy_qty,
        "awaiting_price_product": _handle_price_query,
        "awaiting_weather_wilaya": _handle_weather_query,
        "awaiting_crop_type": _handle_advisory_crop,
        "awaiting_gov_option": _handle_gov_option,
        "awaiting_loan_type": _handle_loan_type,
    }

    handler = handlers.get(state, _handle_unknown)
    return await handler(phone, text, session, data, db)


async def _handle_product_name(phone, text, session, data, db):
    data["product_name"] = text
    whatsapp_sessions[phone] = {"state": "awaiting_product_qty", "data": data}
    return {"intent": "sell", "response": f"المنتج: {text}\nأرسل **الكمية** (قنطار/كغ):"}


async def _handle_product_qty(phone, text, session, data, db):
    data["quantity"] = text
    whatsapp_sessions[phone] = {"state": "awaiting_product_unit", "data": data}
    return {"intent": "sell", "response": "أرسل **الوحدة** (قنطار/كغ/لتر/صندوق):"}


async def _handle_product_unit(phone, text, session, data, db):
    data["unit"] = text
    whatsapp_sessions[phone] = {"state": "awaiting_product_price", "data": data}
    return {"intent": "sell", "response": "أرسل **السعر** بالدينار:"}


async def _handle_product_price(phone, text, session, data, db):
    data["price"] = text
    whatsapp_sessions[phone] = {"state": "awaiting_product_wilaya", "data": data}
    return {"intent": "sell", "response": "أرسل **الولاية**:"}


async def _handle_product_wilaya(phone, text, session, data, db):
    data["wilaya"] = text
    full_text = f"عندي {data.get('product_name','')} {data.get('quantity','')} {data.get('unit','')} من {data.get('wilaya','')} ب {data.get('price','')} دج"
    result = await handle_sell_intent(phone, full_text, db)
    whatsapp_sessions[phone] = {"state": "idle", "data": {}}
    return {"intent": "sell", "response": result.get("message", "✅ تم تسجيل المنتج!")}


async def _handle_search_product(phone, text, session, data, db):
    result = await db.execute(
        select(Product, Farmer)
        .join(Farmer)
        .where(Product.name.ilike(f"%{text}%"), Product.status == "available")
        .limit(5)
    )
    products = result.all()

    if not products:
        whatsapp_sessions[phone] = {"state": "idle", "data": {}}
        return {"intent": "buy", "response": f"❌ لا توجد منتجات باسم '{text}' حالياً"}

    lines = ["🛒 **المنتجات المتوفرة:**\n"]
    for i, (p, f) in enumerate(products, 1):
        lines.append(f"{i}. {p.name} | {f.wilaya} | {p.price} دج/{p.unit}")
    lines.append("\nأرسل **رقم المنتج** لشرائه")

    whatsapp_sessions[phone] = {
        "state": "awaiting_product_selection",
        "data": {"products": [{"id": p.id, "name": p.name} for p, _ in products]},
    }
    return {"intent": "buy", "response": "\n".join(lines)}


async def _handle_product_selection(phone, text, session, data, db):
    try:
        idx = int(text) - 1
        products = data.get("products", [])
        if 0 <= idx < len(products):
            product = products[idx]
            whatsapp_sessions[phone] = {
                "state": "awaiting_buy_qty",
                "data": {"product_id": product["id"], "product_name": product["name"]},
            }
            return {"intent": "buy", "response": f"اخترت {product['name']} ✅\nأرسل الكمية:"}
    except ValueError:
        pass
    whatsapp_sessions[phone] = {"state": "idle", "data": {}}
    return {"intent": "buy", "response": "❌ رقم غير صحيح. أرسل **نشتري** للبدء"}


async def _handle_buy_qty(phone, text, session, data, db):
    whatsapp_sessions[phone] = {"state": "idle", "data": {}}
    return {"intent": "buy", "response": f"✅ تم تسجيل طلب شراء {data.get('product_name', '')}.\nسيتم التواصل معك قريباً"}


async def _handle_price_query(phone, text, session, data, db):
    result = await db.execute(
        select(Product.name, Product.wilaya, Product.price)
        .where(Product.name.ilike(f"%{text}%"), Product.status == "available")
    )
    prices = result.all()
    whatsapp_sessions[phone] = {"state": "idle", "data": {}}

    if not prices:
        return {"intent": "price", "response": f"❌ لا توجد معلومات لـ {text}"}

    vals = [float(p.price) for p in prices]
    return {
        "intent": "price",
        "response": (
            f"📊 **أسعار {text}**\n\n"
            f"• المتوسط: **{sum(vals)/len(vals):.0f} دج**\n"
            f"• الأدنى: **{min(vals):.0f} دج**\n"
            f"• الأعلى: **{max(vals):.0f} دج**\n"
            f"• عدد العروض: {len(prices)}"
        ),
    }


async def _handle_weather_query(phone, text, session, data, db):
    from src.backend.services.weather_service import get_agricultural_advice
    advice = await get_agricultural_advice(text, "طماطم", db)
    whatsapp_sessions[phone] = {"state": "idle", "data": {}}
    return {"intent": "weather", "response": f"🌤️ **الطقس في {text}**\n\n{advice}"}


async def _handle_advisory_crop(phone, text, session, data, db):
    from src.backend.ai.advisory_service import process_advisory_query
    result = await process_advisory_query(farmer_phone=phone, query=text, db=db)
    whatsapp_sessions[phone] = {"state": "idle", "data": {}}
    return {"intent": "advisory", "response": result.get("response", "تم التحليل")}


async def _handle_gov_option(phone, text, session, data, db):
    programs = {
        "1": "📋 **FNDIA**\n💰 حتى 500,000 دج\n✅ شروط: أقل من 10 هكتار + بطاقة فلاح",
        "2": "📋 **FGVA**\n🛡️ ضمان 70% من القرض\n💰 حتى 10,000,000 دج\n📆 حتى 7 سنوات",
        "3": "📋 **PNDA**\n🌱 دعم البذور حتى 50%\n🧪 دعم الأسمدة حتى 40%",
        "4": "📋 **التأمين الفلاحي (CNA)**\n🌾 تعويض حتى 80% من المحصول",
    }
    whatsapp_sessions[phone] = {"state": "idle", "data": {}}
    return {"intent": "gov_support", "response": programs.get(text, "❌ خيار غير صحيح")}


async def _handle_loan_type(phone, text, session, data, db):
    loans = {
        "1": "💳 **BADR RFIG** — قرض بدون فوائد حتى 1,000,000 دج",
        "2": "💳 **CPA فلاح** — قرض حتى 5,000,000 دج",
        "3": "📊 **الدرجة الائتمانية** — احسب درجتك الآن",
    }
    whatsapp_sessions[phone] = {"state": "idle", "data": {}}
    return {"intent": "loan", "response": loans.get(text, "❌ خيار غير صحيح")}


async def _handle_unknown(phone, text, session, data, db):
    whatsapp_sessions[phone] = {"state": "idle", "data": {}}
    return {
        "intent": "unknown",
        "response": "أرسل **مرحبا** لعرض كل الخدمات 🌾",
    }
