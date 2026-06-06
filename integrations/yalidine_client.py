"""عميل API خارجي — Yalidine لتوصيل الطرود في الجزائر"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

import httpx

from src.backend.config import settings


WILAYA_CODES: dict[str, int] = {
    "أدرار": 1, "الشلف": 2, "الأغواط": 3, "أم البواقي": 4,
    "باتنة": 5, "بجاية": 6, "بسكرة": 7, "بشار": 8,
    "البليدة": 9, "البويرة": 10, "تمنراست": 11, "تبسة": 12,
    "تلمسان": 13, "تيارت": 14, "تيزي وزو": 15, "الجزائر": 16,
    "الجلفة": 17, "جيجل": 18, "سطيف": 19, "سعيدة": 20,
    "سكيكدة": 21, "سيدي بلعباس": 22, "عنابة": 23, "قالمة": 24,
    "قسنطينة": 25, "المدية": 26, "مستغانم": 27, "المسيلة": 28,
    "معسكر": 29, "ورقلة": 30, "وهران": 31, "البيض": 32,
    "إليزي": 33, "برج بوعريريج": 34, "بومرداس": 35, "الطارف": 36,
    "تندوف": 37, "تيسمسيلت": 38, "الوادي": 39, "خنشلة": 40,
    "سوق أهراس": 41, "تيبازة": 42, "ميلة": 43, "عين الدفلى": 44,
    "النعامة": 45, "عين تموشنت": 46, "غرداية": 47, "غليزان": 48,
    "تميمون": 49, "برج باجي مختار": 50, "أولاد جلال": 51,
    "بني عباس": 52, "عين صالح": 53, "عين قزام": 54, "تقرت": 55,
    "جانت": 56, "المغير": 57, "المنيعة": 58,
}


DELIVERY_PRICES: dict[str, dict] = {
    "standard": {"base": 300, "per_kg": 50, "per_100km": 25},
    "express": {"base": 600, "per_kg": 75, "per_100km": 40},
    "international": {"base": 5000, "per_kg": 500, "per_100km": 200},
}


async def calculate_shipping_cost(
    from_wilaya: str,
    to_wilaya: str,
    weight_kg: Decimal,
    type_: str = "standard",
) -> dict:
    """حساب تكلفة التوصيل عبر Yalidine"""
    from_code = WILAYA_CODES.get(from_wilaya, 16)
    to_code = WILAYA_CODES.get(to_wilaya, 16)
    km_factor = abs(from_code - to_code) * 50
    km_factor = max(km_factor, 50)

    rates = DELIVERY_PRICES.get(type_, DELIVERY_PRICES["standard"])
    cost = rates["base"] + (float(weight_kg) * rates["per_kg"]) + ((km_factor / 100) * rates["per_100km"])
    cost = max(cost, rates["base"])

    if settings.YALIDINE_API_KEY:
        cost_with_partner = cost * 0.85
    else:
        cost_with_partner = cost

    return {
        "partner": "Yalidine",
        "from": from_wilaya,
        "to": to_wilaya,
        "weight_kg": float(weight_kg),
        "type": type_,
        "cost_dzd": round(cost_with_partner, 0),
        "estimated_days": _estimate_days(from_wilaya, to_wilaya, type_),
    }


def _estimate_days(from_wilaya: str, to_wilaya: str, type_: str) -> int:
    """تقدير أيام التوصيل حسب المسافة"""
    from_code = WILAYA_CODES.get(from_wilaya, 16)
    to_code = WILAYA_CODES.get(to_wilaya, 16)
    distance = abs(from_code - to_code)

    if type_ == "express":
        return max(1, distance // 15)
    elif type_ == "international":
        return 7 + (distance // 10)
    return max(2, distance // 8)


async def create_yalidine_shipment(
    from_address: str,
    from_wilaya: str,
    from_phone: str,
    to_address: str,
    to_wilaya: str,
    to_phone: str,
    items: list[dict],
    type_: str = "standard",
) -> dict:
    """إنشاء شحنة عبر Yalidine API"""
    if not settings.YALIDINE_API_KEY:
        return {
            "status": "simulated",
            "tracking_id": f"YL-{__import__('uuid').uuid4().hex[:8].upper()}",
            "note": "وضع المحاكاة — API غير مهيأ",
        }

    url = "https://api.yalidine.app/v1/shipments"
    headers = {
        "Authorization": f"Bearer {settings.YALIDINE_API_KEY}",
        "X-API-Secret": settings.YALIDINE_SECRET,
        "Content-Type": "application/json",
    }

    payload = {
        "from_address": from_address,
        "from_wilaya_id": WILAYA_CODES.get(from_wilaya, 16),
        "from_phone": from_phone,
        "to_address": to_address,
        "to_wilaya_id": WILAYA_CODES.get(to_wilaya, 16),
        "to_phone": to_phone,
        "type": type_,
        "items": [
            {
                "name": item.get("name", "منتج فلاحي"),
                "quantity": item.get("quantity", 1),
                "price": float(item.get("price", 0)),
            }
            for item in items
        ],
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code in (200, 201):
            data = resp.json()
            return {
                "status": "created",
                "tracking_id": data.get("tracking_id"),
                "label_url": data.get("label_url"),
            }

        return {
            "status": "error",
            "error": resp.text,
        }


async def track_yalidine(tracking_id: str) -> dict:
    """تتبع شحنة Yalidine"""
    if not settings.YALIDINE_API_KEY:
        return {
            "status": "simulated",
            "tracking_id": tracking_id,
            "current_status": "قيد التوصيل",
            "events": [
                {"date": "2026-06-05", "status": "تم استلام الشحنة"},
                {"date": "2026-06-04", "status": "قيد المعالجة في مركز التوزيع"},
            ],
        }

    url = f"https://api.yalidine.app/v1/shipments/{tracking_id}/tracking"
    headers = {"Authorization": f"Bearer {settings.YALIDINE_API_KEY}"}

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        return {"status": "error", "error": resp.text}
