from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.backend.services.logistics_service import (
    calculate_delivery_cost,
    create_yalidine_shipment,
    track_shipment,
)

router = APIRouter()


class DeliveryRequest(BaseModel):
    from_wilaya: str
    to_wilaya: str
    weight_kg: Decimal = Field(default=Decimal("1"), ge=Decimal("0.1"))
    is_refrigerated: bool = False


class ShipmentCreate(BaseModel):
    from_wilaya: str
    from_address: str
    to_wilaya: str
    to_address: str
    weight_kg: Decimal
    description: str
    value_dzd: Decimal
    cash_on_delivery: bool = True


@router.post("/calculate")
async def delivery_cost(body: DeliveryRequest):
    """حساب تكلفة التوصيل مع جميع الشركاء"""
    return await calculate_delivery_cost(
        from_wilaya=body.from_wilaya,
        to_wilaya=body.to_wilaya,
        weight_kg=body.weight_kg,
        is_refrigerated=body.is_refrigerated,
    )


@router.post("/ship")
async def create_shipment(body: ShipmentCreate):
    """إنشاء شحنة جديدة"""
    return await create_yalidine_shipment(
        from_wilaya=body.from_wilaya,
        from_address=body.from_address,
        to_wilaya=body.to_wilaya,
        to_address=body.to_address,
        weight_kg=body.weight_kg,
        description=body.description,
        value_dzd=body.value_dzd,
        cash_on_delivery=body.cash_on_delivery,
    )


@router.get("/track/{tracking_id}")
async def track(tracking_id: str):
    """تتبع شحنة"""
    return await track_shipment(tracking_id)
