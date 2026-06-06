from __future__ import annotations

from decimal import Decimal, DecimalException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Farmer, Product, ProductCategory, ProductUnit


async def handle_sell_intent(from_number: str, body: str, db: AsyncSession) -> dict:
    """معالجة نية البيع من رسالة واتساب"""

    # Parse product info from message: "عندي طماطم 5 قناطير بليدة ب 2000"
    parts = body.replace("عندي", "").strip().split()

    if len(parts) < 4:
        return {
            "intent": "sell",
            "message": (
                "لبيع منتج، أرسل:\n"
                "عندي [اسم المنتج] [الكمية] [الوحدة] [الولاية] ب [السعر]\n\n"
                "مثال: عندي طماطم 5 قناطير بليدة ب 2000"
            ),
        }

    # Basic parsing
    idx = 0
    product_name = parts[idx]
    idx += 1

    quantity_str = parts[idx]
    idx += 1

    unit_str = parts[idx]
    idx += 1

    # Everything until "ب" is wilaya
    wilaya_parts = []
    while idx < len(parts) and parts[idx] != "ب":
        wilaya_parts.append(parts[idx])
        idx += 1

    wilaya = " ".join(wilaya_parts) if wilaya_parts else "غير معروفة"

    # Skip "ب"
    if idx < len(parts) and parts[idx] == "ب":
        idx += 1

    price_str = "".join(parts[idx:]) if idx < len(parts) else "0"

    try:
        quantity = Decimal(quantity_str)
        price = Decimal(price_str)

        # Find or create farmer
        result = await db.execute(select(Farmer).where(Farmer.phone == from_number))
        farmer = result.scalar_one_or_none()
        if not farmer:
            farmer = Farmer(name=f"فلاح {from_number[-4:]}", phone=from_number, wilaya=wilaya)
            db.add(farmer)
            await db.flush()

        # Create product
        unit_map = {"قنطار": ProductUnit.QUINTAL, "كغ": ProductUnit.KG, "لتر": ProductUnit.LITER, "وحدة": ProductUnit.PIECE, "صندوق": ProductUnit.BOX}
        unit = unit_map.get(unit_str, ProductUnit.KG)

        product = Product(
            farmer_id=farmer.id,
            name=product_name,
            category=ProductCategory.OTHER,
            quantity=quantity,
            unit=unit,
            price=price,
            wilaya=wilaya,
        )
        db.add(product)
        await db.flush()

        return {
            "intent": "sell",
            "message": (
                f"✅ تم تسجيل منتجك!\n"
                f"📦 {product_name}\n"
                f"📊 {quantity} {unit_str}\n"
                f"💰 {price} دج\n"
                f"📍 {wilaya}\n"
                f"🔑 رمز: {product.id}\n\n"
                f"سيتم نشر إعلانك تلقائياً للمشترين"
            ),
            "product_id": product.id,
        }

    except (ValueError, DecimalException):
        return {"intent": "sell", "message": "❌ خطأ في قراءة الكمية أو السعر. حاول مرة أخرى\nمثال: عندي طماطم 5 قناطير بليدة ب 2000"}
