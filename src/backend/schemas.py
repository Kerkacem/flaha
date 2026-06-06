from __future__ import annotations

from datetime import datetime
from decimal import Decimal as _Decimal

from pydantic import BaseModel, Field

Decimal = _Decimal


# ─── Farmer ──────────────────────────────────────────────────────


class FarmerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^\+213\d{9}$")
    wilaya: str = Field(..., min_length=2, max_length=50)
    commune: str | None = None
    land_hectares: Decimal | None = None
    has_baridi_mob: bool = False
    baridi_mob_number: str | None = None
    preferred_language: str = "ar"


class FarmerResponse(BaseModel):
    id: str
    name: str
    phone: str
    role: str
    wilaya: str
    commune: str | None = None
    rating_avg: Decimal = Decimal("0")
    total_transactions: int = 0
    is_verified: bool = False
    credit_score: int | None = None
    land_hectares: Decimal | None = None
    crops: str | None = None
    has_baridi_mob: bool = False
    baridi_mob_number: str | None = None
    preferred_language: str = "ar"


# ─── Product ─────────────────────────────────────────────────────


class ProductCreate(BaseModel):
    farmer_phone: str = Field(..., pattern=r"^\+213\d{9}$")
    name: str = Field(..., min_length=1, max_length=100)
    category: str
    description: str | None = None
    quantity: Decimal
    unit: str
    price: Decimal
    wilaya: str
    commune: str | None = None
    is_organic: bool = False


class ProductResponse(BaseModel):
    id: str
    farmer_id: str
    farmer_name: str
    farmer_phone: str
    farmer_rating: Decimal
    name: str
    category: str
    quantity: Decimal
    unit: str
    price: Decimal
    wilaya: str
    status: str
    created_at: datetime


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int


# ─── Transaction ─────────────────────────────────────────────────


class TransactionCreate(BaseModel):
    product_id: str
    buyer_phone: str = Field(..., pattern=r"^\+213\d{9}$")
    quantity: Decimal


class TransactionResponse(BaseModel):
    id: str
    product_name: str
    seller_name: str
    seller_phone: str
    buyer_name: str
    buyer_phone: str
    quantity: Decimal
    total_price: Decimal
    commission: Decimal
    delivery_status: str
    payment_status: str
    created_at: datetime


# ─── WhatsApp ────────────────────────────────────────────────────


class WhatsAppIncoming(BaseModel):
    From: str
    Body: str | None = None
    MediaUrl0: str | None = None
    MediaContentType0: str | None = None
    ProfileName: str | None = None
    MessageSid: str


class WhatsAppResponse(BaseModel):
    status: str
    message: str
    data: dict | None = None


# ─── Advisory ────────────────────────────────────────────────────


class AdvisoryRequest(BaseModel):
    farmer_phone: str
    query: str
    image_url: str | None = None


class AdvisoryResponse(BaseModel):
    query_id: str
    response: str
    confidence: Decimal | None = None
    disease: str | None = None
    products: list[dict] | None = None


# ─── USSD ────────────────────────────────────────────────────────


class USSDRequest(BaseModel):
    sessionId: str
    serviceCode: str
    phoneNumber: str
    text: str


class USSDResponse(BaseModel):
    response: str
    sessionId: str


# ─── Payment ─────────────────────────────────────────────────────


class PaymentInitiate(BaseModel):
    transaction_id: str
    from_phone: str
    amount: Decimal


class PaymentVerify(BaseModel):
    transaction_id: str
    reference: str
