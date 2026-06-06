from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.services.farmer_profile_service import (
    apply_for_loan,
    calculate_credit_score,
    get_loan_recommendation,
)
from src.backend.services.gov_service import (
    get_program_info,
    get_wilaya_delegate,
)
from src.database.connection import get_db
from src.database.models import Farmer

router = APIRouter()


class LoanApplyRequest(BaseModel):
    farmer_phone: str
    bank: str = Field(..., pattern=r"^(BADR|CPA|BNA|CNMA)$")
    amount: float
    purpose: str


@router.get("/farmers/{farmer_id}/credit-score")
async def farmer_credit_score(farmer_id: str, db: AsyncSession = Depends(get_db)):
    """درجة الجدارة الائتمانية للفلاح"""
    result = await calculate_credit_score(farmer_id, db)
    return result


@router.get("/farmers/{farmer_id}/loan-recommendation")
async def farmer_loan_recommendation(farmer_id: str, db: AsyncSession = Depends(get_db)):
    """التوصية بقرض للفلاح"""
    result = await get_loan_recommendation(farmer_id, db)
    return result


@router.post("/loans/apply")
async def apply_loan(body: LoanApplyRequest, db: AsyncSession = Depends(get_db)):
    """تقديم طلب قرض"""
    result = await db.execute(
        select(Farmer).where(Farmer.phone == body.farmer_phone)
    )
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(404, "فلاح غير موجود")

    loan = await apply_for_loan(
        farmer_id=farmer.id,
        bank=body.bank,
        amount=Decimal(str(body.amount)),
        purpose=body.purpose,
        db=db,
    )
    return loan


@router.get("/programs/{program_code}")
async def program_info(program_code: str):
    """معلومات برنامج دعم حكومي"""
    result = await get_program_info(program_code)
    return result


@router.get("/programs/check-deadlines")
async def check_deadlines():
    """المواعيد النهائية القادمة"""
    from src.backend.services.gov_service import check_upcoming_deadlines
    reminders = await check_upcoming_deadlines()
    return {"deadlines": reminders}


@router.get("/wilaya-delegate/{wilaya}")
async def wilaya_delegate(wilaya: str):
    """معلومات المندوب الفلاحي للولاية"""
    result = await get_wilaya_delegate(wilaya)
    return result
