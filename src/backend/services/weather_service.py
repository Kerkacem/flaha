from __future__ import annotations

import time
from datetime import datetime, timedelta
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import settings
from src.database.models import PriceHistory, Product, ProductCategory

# ─── Simple TTL Cache ─────────────────────────────────────────────

_weather_cache: dict[str, tuple[float, dict]] = {}
_cache_ttl: int = 600  # 10 minutes


def _get_cached(key: str) -> dict | None:
    entry = _weather_cache.get(key)
    if entry and time.time() - entry[0] < _cache_ttl:
        return entry[1]
    return None


def _set_cache(key: str, value: dict):
    _weather_cache[key] = (time.time(), value)

# ─── OpenWeatherMap API ─────────────────────────────────────────


ALGERIAN_CITIES: dict[str, dict] = {
    # الولايات الـ 48 الأصلية
    "أدرار": {"lat": 27.8715, "lon": -0.2876},
    "الشلف": {"lat": 36.1681, "lon": 1.3392},
    "الأغواط": {"lat": 33.8000, "lon": 2.8833},
    "أم البواقي": {"lat": 35.8692, "lon": 7.1167},
    "باتنة": {"lat": 35.5580, "lon": 6.1741},
    "بجاية": {"lat": 36.7509, "lon": 5.0647},
    "بسكرة": {"lat": 34.8465, "lon": 5.7293},
    "بشار": {"lat": 31.6167, "lon": -2.2167},
    "البليدة": {"lat": 36.4728, "lon": 2.8275},
    "البويرة": {"lat": 36.3789, "lon": 3.9005},
    "تمنراست": {"lat": 22.7850, "lon": 5.5228},
    "تبسة": {"lat": 35.4042, "lon": 8.1248},
    "تلمسان": {"lat": 34.8783, "lon": -1.3150},
    "تيارت": {"lat": 35.3756, "lon": 1.3171},
    "تيزي وزو": {"lat": 36.7171, "lon": 4.0564},
    "الجزائر": {"lat": 36.7538, "lon": 3.0588},
    "الجلفة": {"lat": 34.6706, "lon": 3.2504},
    "جيجل": {"lat": 36.8214, "lon": 5.7667},
    "سطيف": {"lat": 36.1911, "lon": 5.4103},
    "سعيدة": {"lat": 34.8301, "lon": 0.1511},
    "سكيكدة": {"lat": 36.8767, "lon": 6.9092},
    "سيدي بلعباس": {"lat": 35.1939, "lon": -0.6411},
    "عنابة": {"lat": 36.9013, "lon": 7.7549},
    "قالمة": {"lat": 36.4633, "lon": 7.4333},
    "قسنطينة": {"lat": 36.3377, "lon": 6.6709},
    "المدية": {"lat": 36.2679, "lon": 2.7528},
    "مستغانم": {"lat": 35.9316, "lon": 0.0884},
    "المسيلة": {"lat": 35.7058, "lon": 4.5417},
    "معسكر": {"lat": 35.3978, "lon": 0.1444},
    "ورقلة": {"lat": 31.9526, "lon": 5.3253},
    "وهران": {"lat": 35.7000, "lon": -0.6500},
    "البيض": {"lat": 33.6790, "lon": 1.0190},
    "إليزي": {"lat": 26.4833, "lon": 8.4667},
    "برج بوعريريج": {"lat": 36.0667, "lon": 4.7667},
    "بومرداس": {"lat": 36.7667, "lon": 3.4833},
    "الطارف": {"lat": 36.7667, "lon": 8.3167},
    "تندوف": {"lat": 27.6747, "lon": -8.1306},
    "تسمسيلت": {"lat": 35.6072, "lon": 1.8111},
    "الوادي": {"lat": 33.4667, "lon": 6.8667},
    "خنشلة": {"lat": 35.4167, "lon": 7.1333},
    "سوق أهراس": {"lat": 36.2833, "lon": 7.9500},
    "تيبازة": {"lat": 36.5903, "lon": 2.4475},
    "ميلة": {"lat": 36.4500, "lon": 6.2667},
    "عين الدفلى": {"lat": 36.2583, "lon": 1.9583},
    "النعامة": {"lat": 33.2667, "lon": -0.3167},
    "عين تموشنت": {"lat": 35.3000, "lon": -1.1333},
    "غرداية": {"lat": 32.4833, "lon": 3.6674},
    "غليزان": {"lat": 35.7333, "lon": 0.5500},
    # الولايات الـ 10 الجديدة (2019)
    "تيميمون": {"lat": 29.2500, "lon": 0.2333},
    "برج باجي مختار": {"lat": 21.3333, "lon": 0.9500},
    "أولاد جلال": {"lat": 34.4333, "lon": 5.0667},
    "بني عباس": {"lat": 30.1333, "lon": -2.1667},
    "عين صالح": {"lat": 27.2000, "lon": 2.4667},
    "عين قزام": {"lat": 19.5667, "lon": 5.7667},
    "المغير": {"lat": 33.9500, "lon": 5.9333},
    "المنيعة": {"lat": 30.5833, "lon": 2.8667},
    "جانت": {"lat": 24.5500, "lon": 9.4833},
    "تقرت": {"lat": 33.1000, "lon": 6.0667},
}

# Frost-sensitive crops and their threshold temperatures
FROST_THRESHOLDS: dict[str, Decimal] = {
    "طماطم": Decimal("10"),
    "بطاطا": Decimal("5"),
    "فلفل": Decimal("12"),
    "زيتون": Decimal("-2"),
    "حمضيات": Decimal("3"),
    "بطيخ": Decimal("15"),
    "كوسة": Decimal("10"),
    "باذنجان": Decimal("12"),
}


async def get_weather(wilaya: str) -> dict:
    """الحصول على حالة الطقس لولاية جزائرية (مع cache 10 دقائق)"""
    cached = _get_cached(f"weather:{wilaya}")
    if cached:
        return cached

    city = ALGERIAN_CITIES.get(wilaya, ALGERIAN_CITIES["الجزائر"])

    if not settings.OPENWEATHER_API_KEY:
        result = _mock_weather(wilaya)
        _set_cache(f"weather:{wilaya}", result)
        return result

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": city["lat"],
        "lon": city["lon"],
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "ar",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            result = {
                "wilaya": wilaya,
                "temp_c": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity_pct": data["main"]["humidity"],
                "pressure_hpa": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "clouds_pct": data["clouds"]["all"],
                "sunrise": data["sys"]["sunrise"],
                "sunset": data["sys"]["sunset"],
                "source": "OpenWeatherMap",
            }
            _set_cache(f"weather:{wilaya}", result)
            return result

        result = _mock_weather(wilaya)
        _set_cache(f"weather:{wilaya}", result)
        return result


async def get_forecast(wilaya: str, days: int = 7) -> list[dict]:
    """الحصول على توقعات الطقس للأيام القادمة (مع cache 10 دقائق)"""
    cache_key = f"forecast:{wilaya}:{days}"
    cached = _get_cached(cache_key)
    if cached:
        return cached.get("list", [])

    city = ALGERIAN_CITIES.get(wilaya, ALGERIAN_CITIES["الجزائر"])

    if not settings.OPENWEATHER_API_KEY:
        return _mock_forecast(wilaya, days)

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": city["lat"],
        "lon": city["lon"],
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
        "cnt": days * 8,
        "lang": "ar",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            forecasts = []
            for item in data["list"][::8]:  # One per day
                forecasts.append({
                    "wilaya": wilaya,
                    "date": item["dt_txt"],
                    "temp_max": item["main"]["temp_max"],
                    "temp_min": item["main"]["temp_min"],
                    "humidity": item["main"]["humidity"],
                    "description": item["weather"][0]["description"],
                    "rain_mm": item.get("rain", {}).get("3h", 0),
                })
            _set_cache(cache_key, {"list": forecasts})
            return forecasts

        result = _mock_forecast(wilaya, days)
        _set_cache(cache_key, {"list": result})
        return result


async def get_agricultural_advice(wilaya: str, crop: str, db: AsyncSession) -> str:
    """توليد نصيحة فلاحية بناءً على الطقس"""
    weather = await get_weather(wilaya)
    forecast = await get_forecast(wilaya, 3)

    temp = weather["temp_c"]
    humidity = weather["humidity_pct"]
    advice_parts = []

    # Temperature alerts
    threshold = FROST_THRESHOLDS.get(crop)
    if threshold is not None:
        if temp < threshold:
            advice_parts.append(f"⚠️ تحذير: درجة الحرارة ({temp}°C) أقل من الحد الآمن لـ {crop} ({threshold}°C). أنصح بتغطية النباتات.")
        elif temp > 38:
            advice_parts.append(f"🔥 تحذير: درجة الحرارة مرتفعة ({temp}°C). أنصح بتأخير الري إلى وقت الغروب.")

    # Humidity alerts
    if humidity > 85:
        advice_parts.append(f"💧 الرطوبة عالية ({humidity}%). خطر الإصابة بالأمراض الفطرية. أنصح بالتهوية والرش الوقائي.")
    elif humidity < 20:
        advice_parts.append(f"🏜️ الرطوبة منخفضة ({humidity}%). أنصح بزيادة الري.")

    # Rain alerts
    total_rain = sum(f.get("rain_mm", 0) for f in forecast)
    if total_rain > 20:
        advice_parts.append(f"🌧️ متوقع هطول أمطار غزيرة ({total_rain}mm). أنصح بتأخير التسميد والرش.")

    # Wind alerts
    wind = weather["wind_speed"]
    if wind > 50:
        advice_parts.append(f"💨 رياح قوية ({wind} km/h). أنصح بحماية الدفيئات والأشجار الصغيرة.")

    if not advice_parts:
        advice_parts.append(f"✅ الطقس مناسب لـ {crop} في {wilaya}. درجة الحرارة {temp}°C, الرطوبة {humidity}%.")

    return "\n".join(advice_parts)


def _mock_weather(wilaya: str) -> dict:
    """بيانات طقس وهمية للتطوير"""
    import random
    return {
        "wilaya": wilaya,
        "temp_c": round(random.uniform(18, 36), 1),
        "feels_like": round(random.uniform(20, 38), 1),
        "humidity_pct": round(random.uniform(25, 85)),
        "pressure_hpa": round(random.uniform(1010, 1025)),
        "description": "طقس صافي" if random.random() > 0.3 else "غائم جزئياً",
        "wind_speed": round(random.uniform(5, 35), 1),
        "clouds_pct": round(random.uniform(0, 80)),
        "source": "محاكاة (API غير مهيأ)",
    }


def _mock_forecast(wilaya: str, days: int) -> list[dict]:
    """توقعات وهمية للتطوير"""
    import random
    forecasts = []
    base = datetime.now()
    for i in range(days):
        forecasts.append({
            "wilaya": wilaya,
            "date": (base + timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "temp_max": round(random.uniform(22, 38), 1),
            "temp_min": round(random.uniform(15, 25), 1),
            "humidity": round(random.uniform(30, 80)),
            "description": random.choice(["مشمس", "غائم جزئياً", "غائم", "مطر خفيف"]),
            "rain_mm": round(random.uniform(0, 5), 1),
        })
    return forecasts


# ─── Price Update Task ──────────────────────────────────────────


async def update_market_prices(db: AsyncSession):
    """تحديث أسعار السوق من قاعدة البيانات"""
    from sqlalchemy import func

    result = await db.execute(
        select(
            Product.name,
            Product.wilaya,
            func.avg(Product.price).label("avg_price"),
            func.min(Product.price).label("min_price"),
            func.max(Product.price).label("max_price"),
        )
        .where(Product.status == "available")
        .group_by(Product.name, Product.wilaya)
    )
    rows = result.all()

    for row in rows:
        history = PriceHistory(
            product_name=row.name,
            category=ProductCategory.OTHER,
            wilaya=row.wilaya,
            price_min=Decimal(str(row.min_price)),
            price_max=Decimal(str(row.max_price)),
            price_avg=Decimal(str(row.avg_price)),
            source="flaha_marketplace",
        )
        db.add(history)

    await db.commit()
    return len(rows)
