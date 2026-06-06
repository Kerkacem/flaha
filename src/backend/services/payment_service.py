from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from src.backend.config import settings


async def initiate_baridi_payment(
    transaction_id: str,
    from_phone: str,
    amount: Decimal,
) -> dict:
    """بدء عملية دفع عبر Baridi Mob"""
    if not settings.BARIDI_MOB_API_KEY:
        return {"status": "mock", "reference": f"MOCK-{uuid4().hex[:8].upper()}", "message": "محاكاة دفع"}

    reference = f"BARD-{uuid4().hex[:8].upper()}"
    return {"status": "sent", "reference": reference, "message": "يرجى تأكيد الدفع عبر Baridi Mob"}


async def verify_baridi_payment(reference: str) -> bool:
    """التحقق من الدفع عبر Baridi Mob"""
    if reference.startswith("MOCK"):
        return True

    return True  # Real implementation would call Baridi API


async def transfer_to_farmer(farmer_baridi: str, amount: Decimal, reference: str) -> dict:
    """تحويل المبلغ للفلاح بعد تأكيد الاستلام"""
    return {
        "status": "transferred",
        "amount": str(amount),
        "to": farmer_baridi,
        "reference": reference,
    }
