"""
مهام الخلفية — بديل مجاني لـ Celery/Redis
تشتغل عبر asyncio.create_task — لا تحتاج أي خدمات إضافية
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import func, select

from src.backend.monitoring.health import task_stats
from src.backend.services.whatsapp_service import send_whatsapp
from src.database.connection import async_session_factory
from src.database.models import Farmer, PriceHistory, Product, Transaction

logger = logging.getLogger("flaha.tasks")

# ─── Background Task Manager ────────────────────────────────────

_background_tasks: set[asyncio.Task] = set()


def start_background_tasks():
    """بدء جميع مهام الخلفية"""
    task = asyncio.create_task(_run_scheduler())
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    logger.info("✅ Background tasks started (no Celery/Redis needed)")


def stop_background_tasks():
    """إيقاف جميع مهام الخلفية عند إغلاق التطبيق"""
    for task in _background_tasks.copy():
        task.cancel()
    logger.info("✅ Background tasks stopped")


async def _run_scheduler():
    """المجدول الأساسي — يشتغل كل 60 ثانية ويتحقق من الوقت"""
    interval = timedelta(seconds=60)
    last_price_update = datetime.min
    last_weather_check = datetime.min
    last_reminder = datetime.min

    while True:
        now = datetime.now()

        # كل 6 ساعات: تحديث الأسعار
        if now - last_price_update >= timedelta(hours=6):
            try:
                count = await _update_market_prices()
                logger.info(f"✅ Price update: {count} products")
                task_stats.record_task("price_update", count)
            except Exception as e:
                logger.error(f"Price update failed: {e}")
                task_stats.record_error("price_update", str(e))
            last_price_update = now

        # كل 4 ساعات: فحص الطقس
        if now - last_weather_check >= timedelta(hours=4):
            try:
                count = await _check_weather_alerts()
                logger.info(f"✅ Weather check: {count} alerts sent")
                task_stats.record_task("weather_check", count)
            except Exception as e:
                logger.error(f"Weather check failed: {e}")
                task_stats.record_error("weather_check", str(e))
            last_weather_check = now

        # كل 24 ساعة: تذكير
        if now - last_reminder >= timedelta(hours=24):
            try:
                count = await _send_reminders()
                logger.info(f"✅ Reminders sent: {count}")
                task_stats.record_task("reminder", count)
            except Exception as e:
                logger.error(f"Reminder failed: {e}")
                task_stats.record_error("reminder", str(e))
            last_reminder = now

        await asyncio.sleep(interval.total_seconds())


# ─── Tasks ──────────────────────────────────────────────────────


async def _update_market_prices() -> int:
    """تحديث أسعار السوق من المنتجات النشطة"""
    async with async_session_factory() as db:
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

        from src.database.models import ProductCategory
        count = 0
        for row in rows:
            history = PriceHistory(
                product_name=row.name,
                category=ProductCategory.OTHER,
                wilaya=row.wilaya,
                price_min=row.min_price,
                price_max=row.max_price,
                price_avg=row.avg_price,
                source="flaha",
            )
            db.add(history)
            count += 1

        await db.commit()
        return count


async def _check_weather_alerts() -> int:
    """فحص الطقس وإرسال تنبيهات"""
    try:
        from src.backend.services.weather_service import get_agricultural_advice

        async with async_session_factory() as db:
            result = await db.execute(select(Farmer).where(Farmer.is_verified == True))
            farmers = result.scalars().all()

            alerts_sent = 0
            for farmer in farmers:
                try:
                    result = await db.execute(
                        select(Product.name)
                        .where(Product.farmer_id == farmer.id, Product.status == "available")
                        .limit(1)
                    )
                    crop = result.scalar() or "طماطم"
                    advice = await get_agricultural_advice(farmer.wilaya, crop, db)

                    if "⚠️" in advice or "تحذير" in advice:
                        await send_whatsapp(
                            to=farmer.phone,
                            text=f"🌾 **تنبيه فلاحي من فلاحة**\n\n{advice}\n\n— وكيل فلاحة",
                        )
                        alerts_sent += 1
                except Exception:
                    pass

            return alerts_sent
    except Exception as e:
        logger.error(f"Weather check error: {e}")
        return 0


async def _send_reminders() -> int:
    """إرسال تذكيرات يومية"""
    try:
        async with async_session_factory() as db:
            three_days_ago = datetime.now() - timedelta(days=3)
            result = await db.execute(
                select(Transaction).where(
                    Transaction.delivery_status == "in_transit",
                    Transaction.updated_at < three_days_ago,
                )
            )
            pending = result.scalars().all()

            reminders = 0
            for txn in pending:
                seller = await db.get(Farmer, txn.seller_id)
                if seller:
                    await send_whatsapp(
                        to=seller.phone,
                        text=f"🔔 تذكير: الصفقة {txn.id} لا تزال قيد التوصيل. هل تم التسليم؟",
                    )
                    reminders += 1

            return reminders
    except Exception as e:
        logger.error(f"Reminder error: {e}")
        return 0


async def send_broadcast(phone_numbers: list[str], message: str) -> int:
    """إرسال رسالة جماعية"""
    if not phone_numbers:
        return 0
    results = await asyncio.gather(
        *(send_whatsapp(to=phone, text=message) for phone in phone_numbers),
        return_exceptions=True,
    )
    return sum(1 for r in results if not isinstance(r, Exception))
