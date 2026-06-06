from __future__ import annotations

from decimal import Decimal

# ─── Subscription Plans ─────────────────────────────────────────


SUBSCRIPTION_PLANS: dict[str, dict] = {
    "بلادي Basic": {
        "price_usd": Decimal("49"),
        "price_eur": Decimal("45"),
        "products": ["زيت زيتون (لتر)", "تمر دقلة نور (كغ)"],
        "frequency": "شهري",
        "shipping_included": "بريد الجزائر",
    },
    "بلادي Premium": {
        "price_usd": Decimal("99"),
        "price_eur": Decimal("90"),
        "products": ["زيت زيتون (2 لتر)", "تمر دقلة نور (2 كغ)", "عسل بلدي (500غ)", "كسكس بلدي (كغ)"],
        "frequency": "شهري",
        "shipping_included": "DHL Express",
    },
    "بلادي Family": {
        "price_usd": Decimal("149"),
        "price_eur": Decimal("135"),
        "products": [
            "زيت زيتون (3 لتر)",
            "تمر دقلة نور (3 كغ)",
            "عسل بلدي (كغ)",
            "كسكس بلدي (2 كغ)",
            "توابل مشكلة",
            "مربى بلدي",
        ],
        "frequency": "شهري",
        "shipping_included": "DHL Express Priority",
    },
    "بلادي Ramadan": {
        "price_usd": Decimal("199"),
        "price_eur": Decimal("180"),
        "products": ["جميع المنتجات + هدايا + شحن مجاني"],
        "frequency": "رمضاني (شهر واحد)",
        "shipping_included": "DHL Express Priority",
    },
}

# ─── Shipping Costs ─────────────────────────────────────────────


SHIPPING_COSTS: dict[str, dict[str, Decimal]] = {
    "بريد الجزائر": {
        "فرنسا": Decimal("15"),
        "كندا": Decimal("25"),
        "إسبانيا": Decimal("18"),
        "بريطانيا": Decimal("20"),
        "أمريكا": Decimal("30"),
    },
    "DHL": {
        "فرنسا": Decimal("25"),
        "كندا": Decimal("40"),
        "إسبانيا": Decimal("28"),
        "بريطانيا": Decimal("32"),
        "أمريكا": Decimal("50"),
    },
    "FedEx": {
        "فرنسا": Decimal("28"),
        "كندا": Decimal("45"),
        "إسبانيا": Decimal("30"),
        "بريطانيا": Decimal("35"),
        "أمريكا": Decimal("55"),
    },
}


async def create_subscription(
    customer_name: str,
    customer_email: str,
    customer_phone: str,
    country: str,
    plan_name: str,
    address: str,
) -> dict:
    """إنشاء اشتراك جديد لصندوق الجالية"""
    plan = SUBSCRIPTION_PLANS.get(plan_name)
    if not plan:
        return {"status": "error", "message": "الباقة غير موجودة"}

    shipping = SHIPPING_COSTS.get("DHL", {}).get(country, Decimal("30"))
    total = plan["price_usd"] + shipping

    return {
        "status": "created",
        "customer": customer_name,
        "plan": plan_name,
        "country": country,
        "monthly_total_usd": total,
        "products": plan["products"],
        "message": (
            f"✅ تم إنشاء اشتراكك في باقة '{plan_name}'!\n"
            f"📦 المنتجات: {', '.join(plan['products'])}\n"
            f"💰 السعر: ${plan['price_usd']} + شحن ${shipping} = ${total}/شهر\n"
            f"📍 التوصيل إلى: {country}\n"
            f"📬 سيتم شحن أول صندوق خلال 7 أيام"
        ),
    }


async def calculate_shipping(from_wilaya: str, to_country: str, weight_kg: Decimal) -> dict:
    """حساب تكلفة الشحن الدولي"""
    base_cost = SHIPPING_COSTS.get("DHL", {}).get(to_country, Decimal("30"))
    weight_surcharge = max(Decimal("0"), (weight_kg - Decimal("1")) * Decimal("5"))
    total = base_cost + weight_surcharge

    return {
        "from": from_wilaya,
        "to": to_country,
        "weight_kg": weight_kg,
        "base_cost_usd": base_cost,
        "surcharge_usd": weight_surcharge,
        "total_usd": total,
        "estimated_days": 5 if to_country == "فرنسا" else 7,
        "carrier": "DHL Express",
    }
