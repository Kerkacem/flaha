"""
تحليل الصور الفلاحية — يستخدم Gemini Vision (مجاني) للكشف عن الأمراض
"""

from __future__ import annotations

import logging
from datetime import datetime

from src.backend.services.ai_service import diagnose_image_from_bytes

logger = logging.getLogger("flaha.image_analysis")


async def diagnose_image(
    image_bytes: bytes,
    crop_type: str = "",
    farmer_phone: str = "",
) -> dict:
    """تشخيص مرض من صورة نبات — يستخدم Gemini Vision مجاناً"""
    try:
        diagnosis = await diagnose_image_from_bytes(image_bytes, crop_type)

        return {
            "status": "analysed",
            "diagnosis": diagnosis,
            "analyzed_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Image diagnosis error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "diagnosis": "تعذر تحليل الصورة. تأكد من جودة الصورة وحاول مرة أخرى.",
            "analyzed_at": datetime.now().isoformat(),
        }
