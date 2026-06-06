from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.middleware.auth import require_farmer
from src.backend.schemas import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    TransactionCreate,
    TransactionResponse,
)
from src.database.connection import get_db
from src.database.models import (
    Farmer,
    PaymentStatus,
    Product,
    ProductCategory,
    ProductUnit,
    Transaction,
    TransactionStatus,
)

router = APIRouter()


@router.post("/products", response_model=ProductResponse)
async def create_product(body: ProductCreate, db: AsyncSession = Depends(get_db), farmer: Farmer = Depends(require_farmer)):
    result = await db.execute(select(Farmer).where(Farmer.phone == body.farmer_phone))
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(404, "فلاح غير موجود")

    product = Product(
        farmer_id=farmer.id,
        name=body.name,
        category=ProductCategory(body.category),
        description=body.description,
        quantity=body.quantity,
        unit=ProductUnit(body.unit),
        price=body.price,
        wilaya=body.wilaya,
        commune=body.commune,
        is_organic=body.is_organic,
    )
    db.add(product)
    await db.flush()

    return ProductResponse(
        id=product.id,
        farmer_id=farmer.id,
        farmer_name=farmer.name,
        farmer_phone=farmer.phone,
        farmer_rating=farmer.rating_avg,
        name=product.name,
        category=product.category.value,
        quantity=product.quantity,
        unit=product.unit.value,
        price=product.price,
        wilaya=product.wilaya,
        status=product.status,
        created_at=product.created_at,
    )


@router.get("/products", response_model=ProductListResponse)
async def list_products(
    category: str | None = Query(None),
    wilaya: str | None = Query(None),
    min_price: Decimal | None = Query(None),
    max_price: Decimal | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Product).where(Product.status == "available")
    if category:
        query = query.where(Product.category == ProductCategory(category))
    if wilaya:
        query = query.where(Product.wilaya == wilaya)
    if min_price:
        query = query.where(Product.price >= min_price)
    if max_price:
        query = query.where(Product.price <= max_price)

    query = query.order_by(Product.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    products = result.scalars().all()

    items = []
    for p in products:
        farmer = await db.get(Farmer, p.farmer_id)
        items.append(
            ProductResponse(
                id=p.id,
                farmer_id=farmer.id,
                farmer_name=farmer.name,
                farmer_phone=farmer.phone,
                farmer_rating=farmer.rating_avg,
                name=p.name,
                category=p.category.value,
                quantity=p.quantity,
                unit=p.unit.value,
                price=p.price,
                wilaya=p.wilaya,
                status=p.status,
                created_at=p.created_at,
            )
        )

    # Get the real total count for pagination
    from sqlalchemy import func as sa_func
    count_query = select(Product).where(Product.status == "available")
    if category:
        count_query = count_query.where(Product.category == ProductCategory(category))
    if wilaya:
        count_query = count_query.where(Product.wilaya == wilaya)
    count_result = await db.execute(select(sa_func.count()).select_from(count_query.subquery()))
    total_count = count_result.scalar() or 0

    return ProductListResponse(products=items, total=total_count)


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "منتج غير موجود")

    farmer = await db.get(Farmer, product.farmer_id)
    return ProductResponse(
        id=product.id,
        farmer_id=farmer.id,
        farmer_name=farmer.name,
        farmer_phone=farmer.phone,
        farmer_rating=farmer.rating_avg,
        name=product.name,
        category=product.category.value,
        quantity=product.quantity,
        unit=product.unit.value,
        price=product.price,
        wilaya=product.wilaya,
        status=product.status,
        created_at=product.created_at,
    )


@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(body: TransactionCreate, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, body.product_id)
    if not product or product.status != "available":
        raise HTTPException(404, "منتج غير متوفر")

    result = await db.execute(select(Farmer).where(Farmer.phone == body.buyer_phone))
    buyer = result.scalar_one_or_none()
    if not buyer:
        raise HTTPException(404, "مشتري غير موجود")

    if buyer.id == product.farmer_id:
        raise HTTPException(400, "لا يمكنك شراء منتجك الخاص")

    total_price = body.quantity * product.price
    commission_pct = Decimal("0.05")
    commission = total_price * commission_pct

    txn = Transaction(
        product_id=product.id,
        seller_id=product.farmer_id,
        buyer_id=buyer.id,
        quantity=body.quantity,
        unit_price=product.price,
        total_price=total_price,
        commission=commission,
        commission_pct=commission_pct * 100,
        delivery_status=TransactionStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
    )
    product.status = "sold"

    db.add(txn)
    await db.flush()

    seller = await db.get(Farmer, product.farmer_id)
    return TransactionResponse(
        id=txn.id,
        product_name=product.name,
        seller_name=seller.name,
        seller_phone=seller.phone,
        buyer_name=buyer.name,
        buyer_phone=buyer.phone,
        quantity=txn.quantity,
        total_price=txn.total_price,
        commission=txn.commission,
        delivery_status=txn.delivery_status.value,
        payment_status=txn.payment_status.value,
        created_at=txn.created_at,
    )


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str, db: AsyncSession = Depends(get_db)):
    txn = await db.get(Transaction, transaction_id)
    if not txn:
        raise HTTPException(404, "صفقة غير موجودة")

    product = await db.get(Product, txn.product_id)
    seller = await db.get(Farmer, txn.seller_id)
    buyer = await db.get(Farmer, txn.buyer_id)

    return TransactionResponse(
        id=txn.id,
        product_name=product.name,
        seller_name=seller.name,
        seller_phone=seller.phone,
        buyer_name=buyer.name,
        buyer_phone=buyer.phone,
        quantity=txn.quantity,
        total_price=txn.total_price,
        commission=txn.commission,
        delivery_status=txn.delivery_status.value,
        payment_status=txn.payment_status.value,
        created_at=txn.created_at,
    )
