from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum
from uuid import uuid4

from sqlalchemy import DECIMAL, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ─── Enums ───────────────────────────────────────────────────────


class ProductCategory(str, PyEnum):
    VEGETABLES = "خضار"
    FRUITS = "فواكه"
    GRAINS = "حبوب"
    OLIVE_OIL = "زيت"
    HONEY = "عسل"
    SPICES = "توابل"
    DATES = "تمر"
    DAIRY = "ألبان"
    MEAT = "لحوم"
    OTHER = "آخر"


class ProductUnit(str, PyEnum):
    KG = "كغ"
    LITER = "لتر"
    QUINTAL = "قنطار"
    PIECE = "وحدة"
    BOX = "صندوق"


class TransactionStatus(str, PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    HELD = "held"
    RELEASED = "released"
    REFUNDED = "refunded"
    FAILED = "failed"


class UserRole(str, PyEnum):
    FARMER = "فلاح"
    BUYER = "مشتري"
    BOTH = "فلاح_مشتري"
    ADMIN = "مدير"


# ─── Mixins ──────────────────────────────────────────────────────


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ─── Models ──────────────────────────────────────────────────────


class Farmer(Base, TimestampMixin):
    __tablename__ = "farmers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"DZ-F-{uuid4().hex[:8]}")
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.FARMER)
    wilaya: Mapped[str] = mapped_column(String(50))
    commune: Mapped[str] = mapped_column(String(50), nullable=True)
    land_hectares: Mapped[Decimal | None] = mapped_column(DECIMAL(6, 2), nullable=True)
    has_baridi_mob: Mapped[bool] = mapped_column(default=False)
    baridi_mob_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rating_avg: Mapped[Decimal] = mapped_column(DECIMAL(2, 1), default=0)
    total_transactions: Mapped[int] = mapped_column(default=0)
    is_verified: Mapped[bool] = mapped_column(default=False)
    preferred_language: Mapped[str] = mapped_column(String(10), default="ar")
    crops: Mapped[str | None] = mapped_column(Text, nullable=True)
    credit_score: Mapped[int | None] = mapped_column(nullable=True)

    products: Mapped[list[Product]] = relationship(back_populates="farmer")
    transactions_as_seller: Mapped[list[Transaction]] = relationship(
        back_populates="seller", foreign_keys="Transaction.seller_id"
    )
    transactions_as_buyer: Mapped[list[Transaction]] = relationship(
        back_populates="buyer", foreign_keys="Transaction.buyer_id"
    )


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"FL-{uuid4().hex[:8].upper()}")
    farmer_id: Mapped[str] = mapped_column(ForeignKey("farmers.id"))
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[ProductCategory] = mapped_column(Enum(ProductCategory))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    unit: Mapped[ProductUnit] = mapped_column(Enum(ProductUnit))
    price: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    wilaya: Mapped[str] = mapped_column(String(50))
    commune: Mapped[str | None] = mapped_column(String(50), nullable=True)
    images: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of URLs
    status: Mapped[str] = mapped_column(String(20), default="available")  # available, sold, cancelled
    is_organic: Mapped[bool] = mapped_column(default=False)
    harvest_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    farmer: Mapped[Farmer] = relationship(back_populates="products")
    transactions: Mapped[list[Transaction]] = relationship(back_populates="product")


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"TXN-{uuid4().hex[:8].upper()}")
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    seller_id: Mapped[str] = mapped_column(ForeignKey("farmers.id"))
    buyer_id: Mapped[str] = mapped_column(ForeignKey("farmers.id"))
    quantity: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    total_price: Mapped[Decimal] = mapped_column(DECIMAL(14, 2))
    commission: Mapped[Decimal] = mapped_column(DECIMAL(14, 2))
    commission_pct: Mapped[Decimal] = mapped_column(DECIMAL(4, 2))
    delivery_status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus), default=TransactionStatus.PENDING
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.PENDING
    )
    delivery_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_cost: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2), nullable=True)
    delivery_partner: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tracking_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    buyer_rating: Mapped[int | None] = mapped_column(nullable=True)
    seller_rating: Mapped[int | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    product: Mapped[Product] = relationship(back_populates="transactions")
    seller: Mapped[Farmer] = relationship(back_populates="transactions_as_seller", foreign_keys=[seller_id])
    buyer: Mapped[Farmer] = relationship(back_populates="transactions_as_buyer", foreign_keys=[buyer_id])


class PriceHistory(Base, TimestampMixin):
    __tablename__ = "price_history"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"PRC-{uuid4().hex[:8].upper()}")
    product_name: Mapped[str] = mapped_column(String(100))
    category: Mapped[ProductCategory] = mapped_column(Enum(ProductCategory))
    wilaya: Mapped[str] = mapped_column(String(50))
    price_min: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    price_max: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    price_avg: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    source: Mapped[str] = mapped_column(String(50), default="flaha")


class AdvisoryQuery(Base, TimestampMixin):
    __tablename__ = "advisory_queries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"ADV-{uuid4().hex[:8].upper()}")
    farmer_id: Mapped[str] = mapped_column(ForeignKey("farmers.id"))
    query_type: Mapped[str] = mapped_column(String(30))  # disease, planting, weather, soil
    query_text: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_confidence: Mapped[Decimal | None] = mapped_column(DECIMAL(4, 3), nullable=True)
    disease_detected: Mapped[str | None] = mapped_column(String(100), nullable=True)
    was_helpful: Mapped[bool | None] = mapped_column(nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    farmer: Mapped[Farmer] = relationship()


class LoanApplication(Base, TimestampMixin):
    __tablename__ = "loan_applications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"LOAN-{uuid4().hex[:8].upper()}")
    farmer_id: Mapped[str] = mapped_column(ForeignKey("farmers.id"))
    bank: Mapped[str] = mapped_column(String(50))  # BADR, CPA, BNA
    amount: Mapped[Decimal] = mapped_column(DECIMAL(14, 2))
    purpose: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, approved, rejected, disbursed
    flaha_score: Mapped[Decimal | None] = mapped_column(DECIMAL(3, 2), nullable=True)
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    disbursed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    farmer: Mapped[Farmer] = relationship()


class WhatsAppMessage(Base, TimestampMixin):
    __tablename__ = "whatsapp_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"WA-{uuid4().hex[:8].upper()}")
    from_number: Mapped[str] = mapped_column(String(20), index=True)
    to_number: Mapped[str] = mapped_column(String(20))
    message_type: Mapped[str] = mapped_column(String(20))  # text, image, audio, document
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    wa_message_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    direction: Mapped[str] = mapped_column(String(10))  # incoming, outgoing
    processed: Mapped[bool] = mapped_column(default=False)
    intent: Mapped[str | None] = mapped_column(String(50), nullable=True)  # sell, buy, advisory, etc.

    farmer_id: Mapped[str | None] = mapped_column(ForeignKey("farmers.id"), nullable=True)


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"NOTIF-{uuid4().hex[:8].upper()}")
    farmer_id: Mapped[str] = mapped_column(ForeignKey("farmers.id"))
    channel: Mapped[str] = mapped_column(String(20))  # whatsapp, ussd, push
    template_key: Mapped[str] = mapped_column(String(50))
    template_vars: Mapped[str] = mapped_column(Text)  # JSON
    status: Mapped[str] = mapped_column(String(20), default="pending")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    farmer: Mapped[Farmer] = relationship()


class Device(Base, TimestampMixin):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"DEV-{uuid4().hex[:8].upper()}")
    farmer_id: Mapped[str] = mapped_column(ForeignKey("farmers.id"))
    device_type: Mapped[str] = mapped_column(String(20))  # whatsapp, ussd, android, ios
    device_id: Mapped[str] = mapped_column(String(200))
    push_token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    farmer: Mapped[Farmer] = relationship()


class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"CHAT-{uuid4().hex[:8].upper()}")
    farmer_id: Mapped[str] = mapped_column(ForeignKey("farmers.id"))
    channel: Mapped[str] = mapped_column(String(20))  # whatsapp, ussd
    session_state: Mapped[str] = mapped_column(String(50), default="main_menu")
    session_data: Mapped[str] = mapped_column(Text, default="{}")  # JSON
    is_active: Mapped[bool] = mapped_column(default=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    farmer: Mapped[Farmer] = relationship()
