"""مراقبة صحة النظام والقياسات"""

from __future__ import annotations

import platform
import time
from datetime import datetime, timedelta

from psutil import cpu_percent, disk_usage, virtual_memory
from sqlalchemy import func, select, text

from src.backend.config import settings
from src.database.connection import async_session_factory, engine
from src.database.models import Farmer, Product, Transaction

# ─── Task Monitoring ─────────────────────────────────────────────


class TaskStats:
    def __init__(self):
        self.last_price_update: datetime | None = None
        self.last_weather_check: datetime | None = None
        self.last_reminder: datetime | None = None
        self.price_update_count: int = 0
        self.weather_alerts_sent: int = 0
        self.reminders_sent: int = 0
        self.errors: list[tuple[str, str]] = []
        self.total_runs: int = 0

    def record_task(self, task_name: str, count: int = 0):
        now = datetime.now()
        self.total_runs += 1
        if task_name == "price_update":
            self.last_price_update = now
            self.price_update_count = count
        elif task_name == "weather_check":
            self.last_weather_check = now
            self.weather_alerts_sent = count
        elif task_name == "reminder":
            self.last_reminder = now
            self.reminders_sent = count

    def record_error(self, task_name: str, error: str):
        self.errors.append((task_name, error))
        if len(self.errors) > 50:
            self.errors.pop(0)

    @property
    def status(self) -> dict:
        return {
            "total_runs": self.total_runs,
            "last_price_update": self.last_price_update.isoformat() if self.last_price_update else None,
            "last_weather_check": self.last_weather_check.isoformat() if self.last_weather_check else None,
            "last_reminder": self.last_reminder.isoformat() if self.last_reminder else None,
            "products_updated": self.price_update_count,
            "weather_alerts_sent": self.weather_alerts_sent,
            "reminders_sent": self.reminders_sent,
            "recent_errors": self.errors[-5:],
            "healthy": len(self.errors) == 0 or self.errors[-1][0] != "fatal",
        }


task_stats = TaskStats()

# ─── System Monitor ──────────────────────────────────────────────


class SystemMonitor:
    """مراقبة أداء النظام"""

    def __init__(self):
        self.start_time = time.time()
        self._uptime_cache: str | None = None
        self._uptime_updated = 0.0

    @property
    def uptime(self) -> str:
        now = time.time()
        if now - self._uptime_updated > 60:
            delta = timedelta(seconds=int(now - self.start_time))
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            parts = []
            if days > 0:
                parts.append(f"{days} يوم")
            if hours > 0:
                parts.append(f"{hours} ساعة")
            parts.append(f"{minutes} دقيقة")
            self._uptime_cache = "، ".join(parts)
            self._uptime_updated = now

        return self._uptime_cache or "جاري الحساب"

    async def check_database(self) -> dict:
        """فحص حالة قاعدة البيانات"""
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                db_ok = True
        except Exception:
            db_ok = False

        async with async_session_factory() as db:
            try:
                farmer_count = (await db.execute(select(func.count(Farmer.id)))).scalar() or 0
                product_count = (await db.execute(
                    select(func.count(Product.id)).where(Product.status == "available")
                )).scalar() or 0
                txn_count = (await db.execute(select(func.count(Transaction.id)))).scalar() or 0
                total_volume = (await db.execute(
                    select(func.coalesce(func.sum(Transaction.total_price), 0))
                )).scalar() or 0
                verified_farmers = (await db.execute(
                    select(func.count(Farmer.id)).where(Farmer.is_verified == True)
                )).scalar() or 0
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "farmer_count": 0,
                    "product_count": 0,
                    "transaction_count": 0,
                    "total_volume": 0,
                    "verified_farmers": 0,
                }

        return {
            "status": "connected" if db_ok else "error",
            "farmer_count": farmer_count,
            "product_count": product_count,
            "transaction_count": txn_count,
            "total_volume": float(total_volume),
            "verified_farmers": verified_farmers,
        }

    async def health_check(self) -> dict:
        """فحص صحي شامل للنظام"""
        db_stats = await self.check_database()

        cpu = cpu_percent(interval=0.1)
        mem = virtual_memory()
        disk = disk_usage(".")

        return {
            "status": "healthy" if db_stats["status"] == "connected" else "degraded",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "uptime": self.uptime,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "system": {
                "cpu_percent": cpu,
                "memory_percent": mem.percent,
                "memory_used_gb": round(mem.used / (1024**3), 2),
                "memory_total_gb": round(mem.total / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
            },
            "database_stats": db_stats,
            "background_tasks": task_stats.status,
            "timestamp": datetime.now().isoformat(),
        }


monitor = SystemMonitor()
