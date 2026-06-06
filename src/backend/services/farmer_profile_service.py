from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import (
    Farmer,
    LoanApplication,
    Product,
    Transaction,
    TransactionStatus,
)

# ─── Credit Scoring Model ───────────────────────────────────────
# وزن كل عامل في درجة الجدارة الائتمانية


async def calculate_credit_score(farmer_id: str, db: AsyncSession) -> dict:
    """حساب درجة الجدارة الائتمانية للفلاح (0-100)"""
    farmer = await db.get(Farmer, farmer_id)
    if not farmer:
        return {"score": 0, "level": "غير معروف", "factors": {}}

    score = Decimal("0")
    factors: dict[str, Decimal] = {}

    # 1. عدد الصفقات المنجزة (وزن: 30%)
    txn_result = await db.execute(
        select(func.count(Transaction.id)).where(
            (Transaction.seller_id == farmer_id) | (Transaction.buyer_id == farmer_id),
            Transaction.delivery_status == TransactionStatus.DELIVERED,
        )
    )
    txn_count = txn_result.scalar() or 0
    txn_score = min(Decimal(txn_count) * Decimal("5"), Decimal("30"))
    score += txn_score
    factors["عدد الصفقات"] = txn_score

    # 2. متوسط التقييم (وزن: 25%)
    rating_score = farmer.rating_avg * Decimal("5")
    score += rating_score
    factors["التقييم"] = rating_score

    # 3. تنوع المحاصيل (وزن: 15%)
    crop_result = await db.execute(
        select(func.count(func.distinct(Product.category))).where(Product.farmer_id == farmer_id)
    )
    crop_count = crop_result.scalar() or 0
    crop_score = min(Decimal(crop_count) * Decimal("5"), Decimal("15"))
    score += crop_score
    factors["تنوع المحاصيل"] = crop_score

    # 4. مدة النشاط (وزن: 10%)
    if farmer.created_at and farmer.total_transactions > 0:
        # Higher score = more established
        activity_score = Decimal("10")
    else:
        activity_score = Decimal("2")
    score += activity_score
    factors["مدة النشاط"] = activity_score

    # 5. مساحة الأرض (وزن: 10%)
    if farmer.land_hectares:
        land_score = min(farmer.land_hectares * Decimal("2"), Decimal("10"))
        score += land_score
        factors["مساحة الأرض"] = land_score

    # 6. التحقق من الهوية (وزن: 10%)
    if farmer.is_verified:
        score += Decimal("10")
        factors["التحقق"] = Decimal("10")

    # Ensure score is within 0-100
    score = max(Decimal("0"), min(score, Decimal("100")))

    # Level
    if score >= 80:
        level = "ممتاز 🌟"
    elif score >= 60:
        level = "جيد ✅"
    elif score >= 40:
        level = "متوسط ⚠️"
    else:
        level = "ضعيف ❌"

    return {
        "farmer_id": farmer_id,
        "farmer_name": farmer.name,
        "score": int(score),
        "level": level,
        "factors": factors,
    }


async def get_loan_recommendation(farmer_id: str, db: AsyncSession) -> dict:
    """التوصية بقرض بناءً على الجدارة الائتمانية"""
    credit = await calculate_credit_score(farmer_id, db)
    score = credit["score"]

    if score >= 80:
        return {
            "eligible": True,
            "max_amount": Decimal("5000000"),  # 5M DZD
            "interest_rate": "0% (RFIG)",
            "recommended_bank": "BADR",
            "credit_level": credit["level"],
        }
    elif score >= 60:
        return {
            "eligible": True,
            "max_amount": Decimal("2000000"),  # 2M DZD
            "interest_rate": "2-3%",
            "recommended_bank": "CPA",
            "credit_level": credit["level"],
        }
    elif score >= 40:
        return {
            "eligible": True,
            "max_amount": Decimal("500000"),  # 500K DZD
            "interest_rate": "4-5%",
            "recommended_bank": "CNMA",
            "credit_level": credit["level"],
        }
    else:
        return {
            "eligible": False,
            "max_amount": Decimal("0"),
            "reason": "الجدارة الائتمانية منخفضة. قم بزيادة عدد الصفقات لتحسين درجتك.",
            "credit_level": credit["level"],
        }


async def apply_for_loan(
    farmer_id: str,
    bank: str,
    amount: Decimal,
    purpose: str,
    db: AsyncSession,
) -> dict:
    """تقديم طلب قرض"""
    credit = await calculate_credit_score(farmer_id, db)

    loan = LoanApplication(
        farmer_id=farmer_id,
        bank=bank,
        amount=amount,
        purpose=purpose,
        flaha_score=Decimal(str(credit["score"])),
        status="pending",
    )
    db.add(loan)
    await db.flush()

    return {
        "loan_id": loan.id,
        "status": "pending",
        "amount": str(amount),
        "bank": bank,
        "flaha_score": credit["score"],
        "message": f"تم تقديم طلب القرض بنجاح ✅ رمز المتابعة: {loan.id}",
    }
