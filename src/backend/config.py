from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Flaha — الوكيل الفلاحي الذكي"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    LOG_LEVEL: str = "INFO"

    # ─── Database ─────────────────────────────────────────
    DATABASE_TYPE: str = "sqlite"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/flaha"

    # ─── AI — NVIDIA / OpenAI-compatible ────────────────
    AI_API_KEY: str = ""
    AI_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    AI_MODEL: str = "minimaxai/minimax-m2.7"

    # ─── WhatsApp (Meta Cloud API)
    WHATSAPP_API_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = "flaha-webhook-2026"
    WHATSAPP_ACCESS_TOKEN: str = ""

    # ─── USSD
    USSD_API_KEY: str = ""

    # ─── Weather — OpenWeatherMap ───
    OPENWEATHER_API_KEY: str = ""

    # ─── Payments ────────────────────────────────────────
    BARIDI_MOB_API_KEY: str = ""

    # ─── Delivery ────────────────────────────────────────
    YALIDINE_API_KEY: str = ""

    # JWT
    JWT_SECRET: str = "flaha-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24

    DATA_DIR: Path = Path("data")

    # ─── Computed ────────────────────────────────────────
    @property
    def database_url_async(self) -> str:
        if self.DATABASE_TYPE == "sqlite":
            db_path = self.DATA_DIR / "flaha.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite+aiosqlite:///{db_path}"
        return self.DATABASE_URL

    @property
    def ai_available(self) -> bool:
        return bool(self.AI_API_KEY)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True}


settings = Settings()
