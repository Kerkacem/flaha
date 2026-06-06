from __future__ import annotations

from fastapi import APIRouter, Query

from src.backend.services.weather_service import get_forecast, get_weather

router = APIRouter()


@router.get("/current")
async def weather_current(wilaya: str = Query(..., description="اسم الولاية بالعربية")):
    """الطقس الحالي لولاية معينة"""
    result = await get_weather(wilaya)
    return result


@router.get("/forecast")
async def weather_forecast(wilaya: str = Query(..., description="اسم الولاية بالعربية"), days: int = Query(7, ge=1, le=14)):
    """توقعات الطقس للأيام القادمة"""
    return await get_forecast(wilaya, days)
