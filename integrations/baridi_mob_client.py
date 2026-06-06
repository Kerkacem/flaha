"""عميل API خارجي — Baridi Mob للدفع الإلكتروني"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from decimal import Decimal
from typing import Optional

import httpx

from src.backend.config import settings


async def initiate_payment(
    amount_dzd: Decimal,
    farmer_phone: str,
    farmer_name: str,
    reference: str,
    description: str = "عملية فلاحة",
) -> dict:
    """بدء عملية دفع عبر Baridi Mob"""
    if not settings.BARIDI_MOB_API_KEY:
        return {
            "status": "simulated",
            "reference": reference,
            "note": "وضع المحاكاة — API غير مهيأ",
            "otp": "123456",
        }

    url = "https://api.baridimob.dz/v1/payments/init"
    timestamp = str(int(time.time()))
    payload = {
        "merchant_id": settings.BARIDI_MOB_MERCHANT_ID,
        "amount": float(amount_dzd),
        "currency": "DZD",
        "phone": farmer_phone,
        "name": farmer_name,
        "reference": reference,
        "description": description,
        "timestamp": timestamp,
    }

    payload_str = json.dumps(payload, separators=(",", ":"))
    signature = hmac.new(
        settings.BARIDI_MOB_SECRET.encode(),
        payload_str.encode(),
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "X-API-Key": settings.BARIDI_MOB_API_KEY,
        "X-Signature": signature,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "status": "pending",
                "transaction_id": data.get("transaction_id"),
                "reference": reference,
                "amount": float(amount_dzd),
                "otp_required": True,
                "expires_at": data.get("expires_at"),
            }

        return {"status": "error", "error": resp.text}


async def confirm_payment(transaction_id: str, otp: str) -> dict:
    """تأكيد الدفع عبر OTP"""
    if not settings.BARIDI_MOB_API_KEY:
        return {
            "status": "confirmed",
            "transaction_id": transaction_id,
            "note": "وضع المحاكاة — API غير مهيأ",
        }

    url = "https://api.baridimob.dz/v1/payments/confirm"
    payload = {
        "transaction_id": transaction_id,
        "otp": otp,
    }

    payload_str = json.dumps(payload, separators=(",", ":"))
    signature = hmac.new(
        settings.BARIDI_MOB_SECRET.encode(),
        payload_str.encode(),
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "X-API-Key": settings.BARIDI_MOB_API_KEY,
        "X-Signature": signature,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            return {"status": "confirmed", "transaction_id": transaction_id}
        return {"status": "error", "error": resp.text}


async def check_balance(phone: str) -> dict:
    """الاستعلام عن رصيد Edahabia"""
    if not settings.BARIDI_MOB_API_KEY:
        return {
            "status": "simulated",
            "phone": phone,
            "balance_dzd": 150000.00,
            "note": "وضع المحاكاة",
        }

    url = "https://api.baridimob.dz/v1/accounts/balance"
    headers = {
        "X-API-Key": settings.BARIDI_MOB_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"phone": phone}

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            return {"status": "available", "balance_dzd": data.get("balance", 0)}
        return {"status": "error", "error": resp.text}
