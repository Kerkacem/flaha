"""
خدمة الاستشارات الفلاحية — تستخدم Gemini (مجاني) أو قواعد محلية
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.services.ai_service import diagnose_image_from_bytes, get_advisory
from src.database.models import AdvisoryQuery, Farmer


async def process_advisory_query(
    farmer_phone: str,
    query: str,
    db: AsyncSession,
    image_url: str | None = None,
    image_bytes: bytes | None = None,
) -> dict:
    """معالجة استفسار فلاحي وإرجاع رد ذكي"""
    result = await db.execute(select(Farmer).where(Farmer.phone == farmer_phone))
    farmer = result.scalar_one_or_none()

    if not farmer:
        farmer = Farmer(phone=farmer_phone, name=f"فلاح {farmer_phone[-4:]}")
        db.add(farmer)
        await db.flush()

    query_type = "disease" if any(kw in query for kw in ["مرض", "علاج", "مبيد", "دود", "حشرة"]) else "general"
    if image_bytes:
        query_type = "disease"

    advisory = AdvisoryQuery(
        farmer_id=farmer.id,
        query_type=query_type,
        query_text=query,
        image_url=image_url,
    )
    db.add(advisory)
    await db.flush()

    disease_detected = None
    recommended_products = None

    if image_bytes:
        advisory.disease_detected = True
        response_text = await diagnose_image_from_bytes(image_bytes=image_bytes, crop="")
        disease_detected = "مرض محتمل" if "مرض" in response_text or "عفن" in response_text or "فطر" in response_text else "غير محدد"
    else:
        response_text = await get_advisory(query=query, wilaya=farmer.wilaya or "")
        if any(kw in query for kw in ["مرض", "علاج", "مبيد"]):
            disease_detected = query
            recommended_products = [{"name": "مبيد فلاحي", "type": "مبيد"}]

    advisory.ai_response = response_text
    advisory.responded_at = datetime.now()
    await db.flush()

    return {
        "query_id": advisory.id,
        "response": response_text,
        "confidence": Decimal("0.85"),
        "disease": disease_detected,
        "products": recommended_products,
    }
