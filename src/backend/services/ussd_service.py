from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import settings
from src.database.models import Farmer, Product, ProductCategory, ProductUnit

# Store USSD sessions
ussd_sessions: dict[str, dict] = {}


async def send_ussd(phone: str, text: str) -> dict:
    """إرسال رسالة USSD — في وضع المحاكاة يعيد النص"""
    if not settings.USSD_API_KEY:
        return {"status": "simulated", "message": text, "phone": phone}

    return {"status": "sent", "message": text, "phone": phone}


async def handle_ussd(session_id: str, phone: str, text: str, db: AsyncSession) -> str:
    """معالجة طلبات USSD"""
    if not text:
        # Main menu
        ussd_sessions[session_id] = {"phone": phone}
        return (
            "CON 🌾 مرحبا بك في فلاحة\n"
            "1️⃣ بيع منتج\n"
            "2️⃣ شراء منتج\n"
            "3️⃣ أسعار السوق\n"
            "4️⃣ استشارة\n"
            "5️⃣ دعم حكومي\n"
            "# للرجوع"
        )

    session = ussd_sessions.get(session_id, {})
    steps = text.split("*")
    main_choice = steps[0] if steps else ""

    if main_choice == "1":
        # Sell product flow
        return await _handle_sell_ussd(session_id, phone, steps, session, db)

    elif main_choice == "2":
        # Buy product flow
        return await _handle_buy_ussd(session_id, steps, session, db)

    elif main_choice == "3":
        # Market prices
        return await _handle_prices_ussd(session, steps, db)

    return "END ❌ اختيار غير صحيح. الرجاء المحاولة مرة أخرى"


async def _handle_sell_ussd(session_id, phone, steps, session, db):
    step = len(steps)
    if step == 1:
        return "CON أدخل اسم المنتج:\nمثال: طماطم"
    elif step == 2:
        session["product"] = steps[1]
        return "CON أدخل الكمية:\nمثال: 5 (قناطير)"
    elif step == 3:
        session["quantity"] = steps[2]
        return "CON أدخل السعر للقنطار (دج):\nمثال: 2000"
    elif step == 4:
        session["price"] = steps[3]
        return "CON أدخل ولايتك:\nمثال: البويرة"
    elif step == 5:
        session["wilaya"] = steps[4]
        # Save product
        result = await db.execute(select(Farmer).where(Farmer.phone == phone))
        farmer = result.scalar_one_or_none()
        if not farmer:
            farmer = Farmer(name=f"فلاح {phone[-4:]}", phone=phone, wilaya=session["wilaya"])
            db.add(farmer)
            await db.flush()

        product = Product(
            farmer_id=farmer.id,
            name=session["product"],
            category=ProductCategory.OTHER,
            quantity=Decimal(session["quantity"]),
            unit=ProductUnit.QUINTAL,
            price=Decimal(session["price"]),
            wilaya=session["wilaya"],
        )
        db.add(product)
        await db.flush()

        ussd_sessions.pop(session_id, None)
        return (
            f"END ✅ تم تسجيل منتجك بنجاح!\n"
            f"المنتج: {session['product']}\n"
            f"الكمية: {session['quantity']} قنطار\n"
            f"السعر: {session['price']} دج/قنطار\n"
            f"الولاية: {session['wilaya']}\n"
            f"رمز: {product.id}"
        )
    return "END ❌ خطأ في الإدخال"


async def _handle_buy_ussd(session_id, steps, session, db):
    step = len(steps)
    if step == 1:
        return "CON أدخل اسم المنتج المطلوب:\nمثال: طماطم"
    elif step == 2:
        session["search_product"] = steps[1]
        return "CON أدخل الكمية المطلوبة:\nمثال: 2"
    elif step == 3:
        session["search_qty"] = steps[2]
        result = await db.execute(
            select(Product, Farmer)
            .join(Farmer)
            .where(Product.name.ilike(f"%{session['search_product']}%"))
            .where(Product.status == "available")
            .limit(5)
        )
        products = result.all()

        if not products:
            ussd_sessions.pop(session_id, None)
            return "END ❌ لا توجد منتجات مطابقة حالياً"

        response = "CON 🔍 المنتجات المتوفرة:\n"
        for i, (p, f) in enumerate(products, 1):
            response += f"{i}. {p.name} | {f.wilaya} | {p.price} دج\n"
        response += "0 للرجوع"
        return response

    return "END ❌ خطأ"


async def _handle_prices_ussd(session, steps, db):
    if len(steps) == 1:
        return "CON أدخل اسم المنتج لمعرفة السعر:\nمثال: طماطم"

    product_name = steps[1]
    result = await db.execute(
        select(Product)
        .where(Product.name.ilike(f"%{product_name}%"))
        .where(Product.status == "available")
        .order_by(Product.created_at.desc())
        .limit(5)
    )
    products = result.scalars().all()

    if not products:
        return "END ❌ لا توجد معلومات سعرية متاحة"

    prices = [p.price for p in products]
    avg_price = sum(prices, Decimal(0)) / len(prices)
    min_price = min(prices)
    max_price = max(prices)

    return (
        f"END 📊 أسعار {product_name}:\n"
        f"المتوسط: {avg_price:.0f} دج\n"
        f"الأدنى: {min_price:.0f} دج\n"
        f"الأعلى: {max_price:.0f} دج\n"
        f"عدد العروض: {len(products)}"
    )
