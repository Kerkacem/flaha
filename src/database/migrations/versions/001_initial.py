"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-06
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "farmers",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("role", sa.Enum("فلاح", "مشتري", "فلاح_مشتري", "مدير", name="userrole"), nullable=False),
        sa.Column("wilaya", sa.String(50), nullable=False),
        sa.Column("commune", sa.String(50), nullable=True),
        sa.Column("land_hectares", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("has_baridi_mob", sa.Boolean(), nullable=False),
        sa.Column("baridi_mob_number", sa.String(20), nullable=True),
        sa.Column("rating_avg", sa.DECIMAL(2, 1), nullable=False),
        sa.Column("total_transactions", sa.Integer(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("preferred_language", sa.String(10), nullable=False),
        sa.Column("crops", sa.Text(), nullable=True),
        sa.Column("credit_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_farmers_phone", "farmers", ["phone"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("farmer_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.Enum("خضار", "فواكه", "حبوب", "زيت", "عسل", "توابل", "تمر", "ألبان", "لحوم", "آخر", name="productcategory"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quantity", sa.DECIMAL(10, 2), nullable=False),
        sa.Column("unit", sa.Enum("كغ", "لتر", "قنطار", "وحدة", "صندوق", name="productunit"), nullable=False),
        sa.Column("price", sa.DECIMAL(12, 2), nullable=False),
        sa.Column("wilaya", sa.String(50), nullable=False),
        sa.Column("commune", sa.String(50), nullable=True),
        sa.Column("images", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("is_organic", sa.Boolean(), nullable=False),
        sa.Column("harvest_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("seller_id", sa.String(), nullable=False),
        sa.Column("buyer_id", sa.String(), nullable=False),
        sa.Column("quantity", sa.DECIMAL(10, 2), nullable=False),
        sa.Column("unit_price", sa.DECIMAL(12, 2), nullable=False),
        sa.Column("total_price", sa.DECIMAL(14, 2), nullable=False),
        sa.Column("commission", sa.DECIMAL(14, 2), nullable=False),
        sa.Column("commission_pct", sa.DECIMAL(4, 2), nullable=False),
        sa.Column("delivery_status", sa.Enum("pending", "confirmed", "in_transit", "delivered", "cancelled", "disputed", name="transactionstatus"), nullable=False),
        sa.Column("payment_status", sa.Enum("pending", "held", "released", "refunded", "failed", name="paymentstatus"), nullable=False),
        sa.Column("delivery_address", sa.Text(), nullable=True),
        sa.Column("delivery_cost", sa.DECIMAL(12, 2), nullable=True),
        sa.Column("delivery_partner", sa.String(50), nullable=True),
        sa.Column("tracking_id", sa.String(100), nullable=True),
        sa.Column("buyer_rating", sa.Integer(), nullable=True),
        sa.Column("seller_rating", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["seller_id"], ["farmers.id"]),
        sa.ForeignKeyConstraint(["buyer_id"], ["farmers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "price_history",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("product_name", sa.String(100), nullable=False),
        sa.Column("category", sa.Enum("خضار", "فواكه", "حبوب", "زيت", "عسل", "توابل", "تمر", "ألبان", "لحوم", "آخر", name="productcategory"), nullable=False),
        sa.Column("wilaya", sa.String(50), nullable=False),
        sa.Column("price_min", sa.DECIMAL(10, 2), nullable=False),
        sa.Column("price_max", sa.DECIMAL(10, 2), nullable=False),
        sa.Column("price_avg", sa.DECIMAL(10, 2), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "advisory_queries",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("farmer_id", sa.String(), nullable=False),
        sa.Column("query_type", sa.String(30), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("ai_response", sa.Text(), nullable=True),
        sa.Column("ai_confidence", sa.DECIMAL(4, 3), nullable=True),
        sa.Column("disease_detected", sa.String(100), nullable=True),
        sa.Column("was_helpful", sa.Boolean(), nullable=True),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "loan_applications",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("farmer_id", sa.String(), nullable=False),
        sa.Column("bank", sa.String(50), nullable=False),
        sa.Column("amount", sa.DECIMAL(14, 2), nullable=False),
        sa.Column("purpose", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("flaha_score", sa.DECIMAL(3, 2), nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("disbursed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "whatsapp_messages",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("from_number", sa.String(20), nullable=False),
        sa.Column("to_number", sa.String(20), nullable=False),
        sa.Column("message_type", sa.String(20), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("media_url", sa.Text(), nullable=True),
        sa.Column("wa_message_id", sa.String(100), nullable=True),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("processed", sa.Boolean(), nullable=False),
        sa.Column("intent", sa.String(50), nullable=True),
        sa.Column("farmer_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_whatsapp_messages_from_number", "whatsapp_messages", ["from_number"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("farmer_id", sa.String(), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("template_key", sa.String(50), nullable=False),
        sa.Column("template_vars", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "devices",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("farmer_id", sa.String(), nullable=False),
        sa.Column("device_type", sa.String(20), nullable=False),
        sa.Column("device_id", sa.String(200), nullable=False),
        sa.Column("push_token", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("farmer_id", sa.String(), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("session_state", sa.String(50), nullable=False),
        sa.Column("session_data", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("chat_sessions")
    op.drop_table("devices")
    op.drop_table("notifications")
    op.drop_index("ix_whatsapp_messages_from_number")
    op.drop_table("whatsapp_messages")
    op.drop_table("loan_applications")
    op.drop_table("advisory_queries")
    op.drop_table("price_history")
    op.drop_table("transactions")
    op.drop_table("products")
    op.drop_index("ix_farmers_phone")
    op.drop_table("farmers")
