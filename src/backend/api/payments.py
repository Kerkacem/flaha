from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.schemas import PaymentInitiate, PaymentVerify
from src.backend.services.payment_service import initiate_baridi_payment, verify_baridi_payment
from src.database.connection import get_db
from src.database.models import PaymentStatus, Transaction

router = APIRouter()


@router.post("/pay")
async def initiate_payment(body: PaymentInitiate, db: AsyncSession = Depends(get_db)):
    txn = await db.get(Transaction, body.transaction_id)
    if not txn:
        raise HTTPException(404, "صفقة غير موجودة")

    result = await initiate_baridi_payment(
        transaction_id=body.transaction_id,
        from_phone=body.from_phone,
        amount=body.amount,
    )
    return {"status": "pending", "reference": result.get("reference"), "message": "طلب الدفع مرسل"}


@router.post("/verify")
async def verify_payment(body: PaymentVerify, db: AsyncSession = Depends(get_db)):
    txn = await db.get(Transaction, body.transaction_id)
    if not txn:
        raise HTTPException(404, "صفقة غير موجودة")

    verified = await verify_baridi_payment(body.reference)
    if verified:
        txn.payment_status = PaymentStatus.HELD
        await db.flush()

    return {"status": "confirmed" if verified else "pending", "transaction_id": txn.id}
