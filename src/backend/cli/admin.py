"""سكربتات لإدارة فلاحة من سطر الأوامر"""

from __future__ import annotations

import asyncio
from decimal import Decimal

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table

from src.database.connection import async_session_factory, engine, init_db
from src.database.models import (
    Base,
    Farmer,
    Product,
    ProductCategory,
    ProductUnit,
    Transaction,
)

cli = typer.Typer(name="flaha", help="فلاحة — الوكيل الفلاحي الذكي")
console = Console()


# ─── Database ───────────────────────────────────────────────────


@cli.command()
def init_database(force: bool = typer.Option(False, "--force", "-f", help="مسح وإعادة إنشاء الجداول")):
    """تهيئة قاعدة البيانات"""
    async def _run():
        if force:
            answer = Confirm.ask("⛔ هذا سيمسح جميع البيانات الموجودة. هل أنت متأكد؟")
            if not answer:
                console.print("[yellow]تم الإلغاء[/yellow]")
                return
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            console.print("[red]🗑️ تم مسح جميع الجداول[/red]")

        await init_db()
        console.print("[green]✅ تم إنشاء جميع الجداول بنجاح[/green]")

    asyncio.run(_run())


# ─── Seed Data ──────────────────────────────────────────────────


@cli.command()
def seed():
    """إضافة بيانات وهمية للتجربة"""
    async def _run():
        async with async_session_factory() as db:
            farmers = [
                Farmer(
                    name="محمد بن أحمد",
                    phone="+213555123456",
                    wilaya="البويرة",
                    commune="الأخضرية",
                    land_hectares=12.5,
                    crops="طماطم, فلفل, بطاطا",
                    is_verified=True,
                    credit_score=72,
                    preferred_language="ar",
                ),
                Farmer(
                    name="علي بلقاسم",
                    phone="+213666789012",
                    wilaya="بليدة",
                    commune="الشبلي",
                    land_hectares=8.0,
                    crops="حمضيات, زيتون",
                    is_verified=True,
                    credit_score=65,
                    preferred_language="ar",
                ),
                Farmer(
                    name="فاطمة بن علي",
                    phone="+213777345678",
                    wilaya="سطيف",
                    commune="عين ولمان",
                    land_hectares=20.0,
                    crops="قمح, شعير",
                    is_verified=False,
                    credit_score=45,
                    preferred_language="ar",
                ),
                Farmer(
                    name="عبد الله ناصر",
                    phone="+213558901234",
                    wilaya="ورقلة",
                    commune="تقرت",
                    land_hectares=50.0,
                    crops="تمور, بطيخ",
                    is_verified=True,
                    credit_score=80,
                    preferred_language="ar",
                ),
                Farmer(
                    name="خديجة سعيد",
                    phone="+213699456789",
                    wilaya="تيزي وزو",
                    commune="ذراع بن خدة",
                    land_hectares=5.5,
                    crops="زيتون, تين",
                    is_verified=True,
                    credit_score=58,
                    preferred_language="kab",
                ),
            ]
            db.add_all(farmers)
            await db.flush()

            products = [
                Product(
                    farmer_id=farmers[0].id,
                    name="طماطم",
                    category=ProductCategory.VEGETABLES,
                    price=Decimal("45.00"),
                    unit=ProductUnit.KG,
                    quantity=Decimal("500"),
                    wilaya="البويرة",
                    description="طماطم موسمية طازجة من البويرة",
                ),
                Product(
                    farmer_id=farmers[0].id,
                    name="فلفل أخضر",
                    category=ProductCategory.VEGETABLES,
                    price=Decimal("60.00"),
                    unit=ProductUnit.KG,
                    quantity=Decimal("300"),
                    wilaya="البويرة",
                    description="فلفل أخضر حلو",
                ),
                Product(
                    farmer_id=farmers[1].id,
                    name="برتقال",
                    category=ProductCategory.FRUITS,
                    price=Decimal("80.00"),
                    unit=ProductUnit.KG,
                    quantity=Decimal("1000"),
                    wilaya="بليدة",
                    description="برتقال بلدي من بليدة",
                ),
                Product(
                    farmer_id=farmers[1].id,
                    name="زيت زيتون",
                    category=ProductCategory.OLIVE_OIL,
                    price=Decimal("800.00"),
                    unit=ProductUnit.LITER,
                    quantity=Decimal("200"),
                    wilaya="بليدة",
                    description="زيت زيتون بكر ممتاز",
                ),
                Product(
                    farmer_id=farmers[3].id,
                    name="تمر دقلة نور",
                    category=ProductCategory.FRUITS,
                    price=Decimal("350.00"),
                    unit=ProductUnit.KG,
                    quantity=Decimal("2000"),
                    wilaya="ورقلة",
                    description="تمور دقلة نور فاخرة من ورقلة",
                ),
                Product(
                    farmer_id=farmers[3].id,
                    name="بطيخ أحمر",
                    category=ProductCategory.VEGETABLES,
                    price=Decimal("30.00"),
                    unit=ProductUnit.KG,
                    quantity=Decimal("5000"),
                    wilaya="ورقلة",
                ),
                Product(
                    farmer_id=farmers[4].id,
                    name="زيت زيتون عوكلو",
                    category=ProductCategory.OLIVE_OIL,
                    price=Decimal("1200.00"),
                    unit=ProductUnit.LITER,
                    quantity=Decimal("100"),
                    wilaya="تيزي وزو",
                    description="زيت زيتون تقليدي من منطقة عوكلو",
                ),
            ]
            db.add_all(products)
            await db.commit()

        console.print("[green]✅ تم إضافة بيانات التجربة بنجاح[/green]")
        console.print(f"  - {len(farmers)} فلاح")
        console.print(f"  - {len(products)} منتج")

    asyncio.run(_run())


# ─── List ───────────────────────────────────────────────────────


@cli.command()
def farmers():
    """عرض قائمة الفلاحين"""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            result = await db.execute(select(Farmer))
            rows = result.scalars().all()

            table = Table(title="🌾 الفلاحون المسجلون")
            table.add_column("ID", style="cyan")
            table.add_column("الاسم", style="green")
            table.add_column("الهاتف")
            table.add_column("الولاية")
            table.add_column("المساحة (هكتار)")
            table.add_column("نشط?")
            table.add_column("الدرجة الائتمانية")

            for f in rows:
                table.add_row(
                    str(f.id),
                    f.name,
                    f.phone,
                    f.wilaya,
                    str(f.land_hectares) if f.land_hectares else "-",
                    "✅" if f.is_verified else "❌",
                    str(f.credit_score) if f.credit_score else "-",
                )

            console.print(table)
            console.print(f"\nالمجموع: {len(rows)} فلاح")

    asyncio.run(_run())


@cli.command()
def products(wilaya: str | None = typer.Argument(None, help="تصفية حسب الولاية")):
    """عرض المنتجات المتاحة"""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            q = select(Product).where(Product.status == "available")
            if wilaya:
                q = q.where(Product.wilaya == wilaya)
            result = await db.execute(q)
            rows = result.scalars().all()

            table = Table(title="🛒 المنتجات المتاحة")
            table.add_column("ID")
            table.add_column("المنتج", style="green")
            table.add_column("الفئة")
            table.add_column("السعر (دج)")
            table.add_column("الكمية")
            table.add_column("الولاية")

            for p in rows:
                table.add_row(
                    str(p.id),
                    p.name,
                    p.category.value if p.category else "-",
                    str(p.price),
                    f"{p.quantity} {p.unit}",
                    p.wilaya,
                )

            console.print(table)
            console.print(f"\nالمجموع: {len(rows)} منتج")

    asyncio.run(_run())


# ─── Send Test Message ──────────────────────────────────────────


@cli.command()
def send_test(phone: str = typer.Argument(..., help="رقم الهاتف (مثال: +213555123456)")):
    """إرسال رسالة واتساب تجريبية"""
    async def _run():
        from src.backend.services.whatsapp_service import send_whatsapp
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            progress.add_task(description="جاري الإرسال...", total=None)
            result = await send_whatsapp(
                to=phone,
                text="🌾 مرحباً بك في فلاحة — الوكيل الفلاحي الذكي!\n\n"
                     "أنا هنا لمساعدتك في:\n"
                     "1️⃣ بيع وشراء المنتجات الفلاحية\n"
                     "2️⃣ تشخيص أمراض النباتات\n"
                     "3️⃣ معلومات الطقس والري\n"
                     "4️⃣ التمويل والقروض\n"
                     "5️⃣ التوصيل والشحن\n\n"
                     "أرسل أي رسالة لبدء المحادثة",
            )

        if result.get("status") == "sent":
            console.print(f"[green]✅ تم إرسال الرسالة إلى {phone}[/green]")
        else:
            console.print(f"[red]❌ فشل الإرسال: {result.get('error', 'خطأ غير معروف')}[/red]")

    asyncio.run(_run())


# ─── Stats ──────────────────────────────────────────────────────


@cli.command()
def stats():
    """إحصائيات عامة عن المنصة"""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import func, select

            farmer_count = (await db.execute(select(func.count(Farmer.id)))).scalar()
            product_count = (await db.execute(select(func.count(Product.id)).where(Product.status == "available"))).scalar()
            txn_count = (await db.execute(select(func.count(Transaction.id)))).scalar()
            total_volume = (await db.execute(select(func.coalesce(func.sum(Transaction.total_price), 0)))).scalar()

            table = Table(title="📊 إحصائيات فلاحة")
            table.add_column("المؤشر", style="cyan")
            table.add_column("القيمة", style="green")

            table.add_row("عدد الفلاحين", str(farmer_count))
            table.add_row("المنتجات المتاحة", str(product_count))
            table.add_row("عدد الصفقات", str(txn_count))
            table.add_row("حجم التداول", f"{total_volume:,.0f} دج")

            console.print(table)

    asyncio.run(_run())


# ─── Run Server ─────────────────────────────────────────────────


@cli.command()
def serve(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """تشغيل خادم API"""
    import uvicorn
    console.print(f"[green]🚀 تشغيل فلاحة API على http://{host}:{port}[/green]")
    uvicorn.run("src.backend.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    cli()
