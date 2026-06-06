from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.backend.services.diaspora_service import (
    SUBSCRIPTION_PLANS,
    calculate_shipping,
    create_subscription,
)

router = APIRouter()


class SubscriptionCreate(BaseModel):
    customer_name: str = Field(..., min_length=2)
    customer_email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    customer_phone: str = Field(..., pattern=r"^\+?\d{8,15}$")
    country: str = Field(..., min_length=2)
    plan_name: str
    address: str = Field(..., min_length=5)


class ShippingRequest(BaseModel):
    from_wilaya: str
    to_country: str
    weight_kg: Decimal


@router.get("/plans")
async def list_subscription_plans():
    """قائمة باقات الجالية"""
    return {"plans": SUBSCRIPTION_PLANS}


@router.post("/subscribe")
async def subscribe(body: SubscriptionCreate):
    """اشتراك جديد لصندوق الجالية"""
    if body.plan_name not in SUBSCRIPTION_PLANS:
        raise HTTPException(404, "الباقة غير موجودة")

    result = await create_subscription(
        customer_name=body.customer_name,
        customer_email=body.customer_email,
        customer_phone=body.customer_phone,
        country=body.country,
        plan_name=body.plan_name,
        address=body.address,
    )
    return result


@router.post("/shipping/calculate")
async def calculate_diaspora_shipping(body: ShippingRequest):
    """حساب تكلفة الشحن الدولي"""
    result = await calculate_shipping(
        from_wilaya=body.from_wilaya,
        to_country=body.to_country,
        weight_kg=body.weight_kg,
    )
    return result
