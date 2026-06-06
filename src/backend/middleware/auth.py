from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import settings
from src.database.connection import get_db
from src.database.models import Farmer

logger = logging.getLogger("flaha.auth")

security = HTTPBearer(auto_error=False)

# ─── JWT ──────────────────────────────────────────────────────────


def create_token(farmer_id: str, role: str = "فلاح") -> str:
    payload = {
        "sub": farmer_id,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + settings.JWT_EXPIRY_HOURS * 3600,
    }
    header = {"alg": "HS256", "typ": "JWT"}
    segments = []
    segments.append(_b64encode(json.dumps(header, ensure_ascii=False).encode()))
    segments.append(_b64encode(json.dumps(payload, ensure_ascii=False).encode()))
    signing_input = ".".join(segments).encode()
    signature = hmac.new(settings.JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    segments.append(_b64encode(signature))
    return ".".join(segments)


def verify_token(token: str) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        signing_input = ".".join(parts[:2]).encode()
        expected_sig = hmac.new(settings.JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
        actual_sig = _b64decode(parts[2])
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError("Invalid signature")
        payload = json.loads(_b64decode(parts[1]))
        if payload.get("exp", 0) < time.time():
            raise ValueError("Token expired")
        return payload
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="❌ رمز الدخول غير صالح")


def _b64encode(data: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64decode(data: str) -> bytes:
    import base64
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


# ─── FastAPI Dependencies ─────────────────────────────────────────


async def get_current_farmer(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Farmer | None:
    if credentials is None:
        return None
    try:
        payload = verify_token(credentials.credentials)
        farmer = await db.get(Farmer, payload["sub"])
        return farmer
    except HTTPException:
        return None


async def require_farmer(
    farmer: Farmer | None = Depends(get_current_farmer),
) -> Farmer:
    if farmer is None:
        raise HTTPException(status_code=401, detail="❌ يتطلب تسجيل الدخول")
    return farmer


# ─── Rate Limiter ─────────────────────────────────────────────────


class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clients: dict[str, list[float]] = {}

    async def check(self, request: Request):
        forwarded = request.headers.get("X-Forwarded-For")
        client_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")
        now = time.time()
        window_start = now - self.window_seconds
        timestamps = [t for t in self._clients.get(client_ip, []) if t > window_start]
        if len(timestamps) >= self.max_requests:
            raise HTTPException(status_code=429, detail="❌ طلبات كثيرة. حاول بعد قليل")
        timestamps.append(now)
        self._clients[client_ip] = timestamps


rate_limiter = RateLimiter()


# ─── WhatsApp Webhook Signature Verification ──────────────────────


def verify_whatsapp_signature(request: Request, payload: bytes) -> bool:
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not signature or not settings.WHATSAPP_ACCESS_TOKEN:
        return settings.DEBUG
    expected = hmac.new(
        settings.WHATSAPP_ACCESS_TOKEN.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
