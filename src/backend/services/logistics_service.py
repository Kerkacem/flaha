from __future__ import annotations

from decimal import Decimal

import httpx

from src.backend.config import settings

# ─── Local Partners Pricing ─────────────────────────────────────


DELIVERY_PARTNERS: dict[str, dict] = {
    "Yalidine": {
        "coverage": "58 ولاية",
        "base_price_dzd": Decimal("300"),
        "price_per_kg_dzd": Decimal("50"),
        "api_endpoint": "https://api.yalidine.net/v1/parcels",
    },
    "ZR Express": {
        "coverage": "48 ولاية",
        "base_price_dzd": Decimal("250"),
        "price_per_kg_dzd": Decimal("40"),
        "api_endpoint": "https://api.zrexpress.dz/v1/shipments",
    },
    "Imedia": {
        "coverage": "40 ولاية",
        "base_price_dzd": Decimal("200"),
        "price_per_kg_dzd": Decimal("35"),
        "api_endpoint": "https://api.imedia.dz/v1/deliveries",
    },
}


async def calculate_delivery_cost(
    from_wilaya: str,
    to_wilaya: str,
    weight_kg: Decimal,
    is_refrigerated: bool = False,
) -> dict:
    """حساب تكلفة التوصيل المحلي مع جميع الشركاء"""
    options = []

    for partner_name, partner in DELIVERY_PARTNERS.items():
        cost = partner["base_price_dzd"] + (weight_kg * partner["price_per_kg_dzd"])

        if is_refrigerated:
            cost += Decimal("500")

        options.append(
            {
                "partner": partner_name,
                "cost_dzd": int(cost),
                "cost_usd": float(cost / Decimal("135")),  # 1 USD ≈ 135 DZD
                "coverage": partner["coverage"],
                "estimated_days": 1 if from_wilaya == to_wilaya else 2,
            }
        )

    options.sort(key=lambda x: x["cost_dzd"])

    return {
        "from": from_wilaya,
        "to": to_wilaya,
        "weight_kg": float(weight_kg),
        "refrigerated": is_refrigerated,
        "options": options,
    }


async def create_yalidine_shipment(
    from_wilaya: str,
    from_address: str,
    to_wilaya: str,
    to_address: str,
    weight_kg: Decimal,
    description: str,
    value_dzd: Decimal,
    cash_on_delivery: bool = True,
) -> dict:
    """إنشاء شحنة عبر Yalidine"""
    if not settings.YALIDINE_API_KEY:
        return {
            "status": "mock",
            "tracking_id": f"YL-MOCK-{__import__('uuid').uuid4().hex[:8].upper()}",
            "message": "محاكاة شحنة Yalidine (API غير مهيأ)",
        }

    payload = {
        "from": {"wilaya": from_wilaya, "address": from_address},
        "to": {"wilaya": to_wilaya, "address": to_address},
        "parcel": {
            "weight_kg": float(weight_kg),
            "description": description,
            "value": int(value_dzd),
        },
        "payment": "cash_on_delivery" if cash_on_delivery else "prepaid",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            DELIVERY_PARTNERS["Yalidine"]["api_endpoint"],
            json=payload,
            headers={"Authorization": f"Bearer {settings.YALIDINE_API_KEY}"},
        )
        return resp.json()


async def track_shipment(tracking_id: str) -> dict:
    """تتبع شحنة"""
    if "MOCK" in tracking_id:
        return {
            "tracking_id": tracking_id,
            "status": "in_transit",
            "location": "مركز التوزيع",
            "estimated_delivery": "غداً",
            "updates": [
                {"date": "2026-06-06", "status": "تم استلام الشحنة"},
                {"date": "2026-06-07", "status": "في مركز التوزيع"},
            ],
        }

    return {"tracking_id": tracking_id, "status": "unknown"}
