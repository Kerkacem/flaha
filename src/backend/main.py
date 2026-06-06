from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.backend.api import (
    advisory,
    auth,
    dashboard,
    diaspora,
    gov_support,
    logistics,
    marketplace,
    payments,
    ussd,
    weather,
    whatsapp,
)
from src.backend.config import settings
from src.backend.middleware.auth import rate_limiter
from src.backend.monitoring.health import monitor
from src.backend.tasks.background import start_background_tasks, stop_background_tasks
from src.database.connection import close_db, init_db

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("flaha")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🌾 {settings.APP_NAME} v{settings.VERSION} starting...")
    await init_db()
    logger.info(f"✅ Database initialized ({settings.DATABASE_TYPE})")

    # Start background tasks (replace Celery — مجاني بدون Redis)
    start_background_tasks()
    logger.info("✅ Background scheduler started")

    if settings.ai_available:
        logger.info(f"🤖 AI available ({settings.AI_MODEL})")
    else:
        logger.info("🤖 AI not configured — using local mock AI (100% free)")

    yield
    stop_background_tasks()
    await close_db()
    logger.info("👋 Flaha shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="الوكيل الفلاحي الذكي — Intelligent Agricultural Agent for Algeria (100% Free Tier)",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "Flaha Team", "url": "https://flaha.dz"},
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        await rate_limiter.check(request)
    return await call_next(request)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "خطأ داخلي في الخادم"},
    )


app.include_router(dashboard.router, tags=["Dashboard"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(marketplace.router, prefix="/api/v1/marketplace", tags=["Marketplace"])
app.include_router(whatsapp.router, prefix="/api/v1/whatsapp", tags=["WhatsApp"])
app.include_router(ussd.router, prefix="/api/v1/ussd", tags=["USSD"])
app.include_router(advisory.router, prefix="/api/v1/advisory", tags=["Advisory"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(diaspora.router, prefix="/api/v1/diaspora", tags=["Diaspora"])
app.include_router(logistics.router, prefix="/api/v1/logistics", tags=["Logistics"])
app.include_router(gov_support.router, prefix="/api/v1/gov-support", tags=["Gov Support"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["Weather"])


@app.get("/health", tags=["System"])
async def health():
    """فحص صحي شامل للنظام"""
    return await monitor.health_check()


@app.get("/version", tags=["System"])
async def version():
    """معلومات الإصدار"""
    return {
        "version": settings.VERSION,
        "database_type": settings.DATABASE_TYPE,
        "ai_available": settings.ai_available,
        "debug": settings.DEBUG,
    }
