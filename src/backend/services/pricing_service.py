from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import PriceHistory


async def suggest_price(
    product_name: str, wilaya: str, farmer_price: Decimal, db: AsyncSession
) -> Decimal:
    """خوارزمية التسعير الذكي — تجلب متوسط السوق من قاعدة البيانات"""
    market_avg = await _get_market_avg(product_name, wilaya, db)
    if market_avg == 0:
        return farmer_price

    quality_factor = farmer_price * Decimal("0.1")
    suggested = (market_avg * Decimal("0.6")) + (farmer_price * Decimal("0.3")) + quality_factor
    return suggested.quantize(Decimal("1"))


async def _get_market_avg(product_name: str, wilaya: str, db: AsyncSession) -> Decimal:
    """متوسط سعر السوق من PriceHistory أو Products"""
    from sqlalchemy import func

    result = await db.execute(
        select(func.avg(PriceHistory.price_avg))
        .where(PriceHistory.product_name.ilike(f"%{product_name}%"))
        .where(PriceHistory.wilaya == wilaya)
    )
    avg = result.scalar()
    if avg:
        return Decimal(str(avg))

    result = await db.execute(
        select(func.avg(PriceHistory.price_avg))
        .where(PriceHistory.product_name.ilike(f"%{product_name}%"))
    )
    avg = result.scalar()
    if avg:
        return Decimal(str(avg))

    return Decimal("100")
