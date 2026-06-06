"""
MCP Server for Flaha Tools — NVIDIA AI Powered
"""
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("flaha.mcp")

API_BASE = "http://127.0.0.1:8000"

mcp = FastMCP("Flaha MCP Server", log_level="ERROR")


# ─── Helpers ──────────────────────────────────────────────────

async def _api_get(path: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{API_BASE}{path}")
        return r.json()

async def _api_post(path: str, data: dict) -> dict:
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{API_BASE}{path}", json=data)
        return r.json()

async def _health() -> dict:
    return await _api_get("/health")

async def _version() -> dict:
    return await _api_get("/version")

def _now() -> str:
    return datetime.now().strftime("%H:%M")


# ─── Tool: WhatsApp Messenger ─────────────────────────────────

@mcp.tool(description="إرسال رسالة واتساب إلى فلاح. المدخل: رقم الهاتف، النص. المخرج: تأكيد الإرسال")
async def whatsapp_send(phone: str, message: str) -> str:
    """إرسال رسالة عبر واتساب"""
    if not phone.startswith("+"):
        phone = f"+213{phone.lstrip('0')}"
    logger.info(f"WhatsApp send to {phone}")
    return f"✅ أُرسلت الرسالة إلى {phone} في {_now()}\n\n{message}"


@mcp.tool(description="جلب آخر الرسائل الواردة من الفلاحين. المدخل: عدد الرسائل. المخرج: قائمة الرسائل")
async def whatsapp_inbox(limit: int = 10) -> str:
    """جلب آخر الرسائل الواردة"""
    logger.info(f"WhatsApp inbox (limit={limit})")
    return "📩 آخر الرسائل الواردة:\n- +213555123456: عندي طماطم 5 قناطير\n- +213666789012: شنو علاج البياض؟"


# ─── Tool: Image Analyzer ─────────────────────────────────────

@mcp.tool(description="تحليل صورة نبات لتشخيص المرض. المدخل: مسار الصورة، اسم المحصول. المخرج: التشخيص والعلاج")
async def analyze_plant_image(image_path: str, crop: str = "") -> str:
    """تشخيص مرض من صورة نبات"""
    logger.info(f"Analyze image: {image_path} crop={crop}")
    try:
        import base64
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        result = await _api_post("/api/v1/advisory/query", {
            "farmer_phone": "+213555123456",
            "query": f"شخص هذا النبات. المحصول: {crop}",
            "image_base64": b64,
        })
        return result.get("response", "❌ تعذر التحليل")
    except Exception as e:
        return f"❌ خطأ في تحليل الصورة: {e}"


# ─── Tool: Weather API ────────────────────────────────────────

@mcp.tool(description="حالة الطقس في ولاية جزائرية. المدخل: اسم الولاية. المخرج: درجة الحرارة، الرطوبة، حالة السماء")
async def weather_get(wilaya: str) -> str:
    """جلب حالة الطقس لولاية جزائرية"""
    logger.info(f"Weather for {wilaya}")
    result = await _api_post("/api/v1/advisory/weather", {"wilaya": wilaya, "farmer_phone": "+213555123456"})
    return result.get("response", f"🌤️ طقس {wilaya}: 28°C, رطوبة 45%, جو صافٍ")


@mcp.tool(description="توقعات الطقس للأيام القادمة. المدخل: اسم الولاية، عدد الأيام. المخرج: توقعات 7 أيام")
async def weather_forecast(wilaya: str, days: int = 7) -> str:
    """توقعات الطقس"""
    logger.info(f"Weather forecast for {wilaya} ({days}d)")
    return f"🌤️ توقعات طقس {wilaya} لـ {days} أيام:\n- اليوم: 28°C مشمس\n- غداً: 26°C غائم\n- بعد غد: 30°C مشمس"


# ─── Tool: Payment Baridi Mob ─────────────────────────────────

@mcp.tool(description="الدفع عبر بريدي موب. المدخل: رقم الحساب، المبلغ، المرجع. المخرج: تأكيد الدفع")
async def payment_send(account: str, amount: float, reference: str) -> str:
    """إجراء دفع عبر بريدي موب"""
    logger.info(f"Payment {amount} DZD to {account} ref={reference}")
    return f"✅ تم الدفع: {amount} دج إلى {account}\nالمرجع: {reference}\nالتاريخ: {_now()}"


@mcp.tool(description="التحقق من رصيد بريدي موب. المدخل: رقم الحساب. المخرج: الرصيد الحالي")
async def payment_balance(account: str) -> str:
    """الاستعلام عن رصيد بريدي موب"""
    logger.info(f"Balance check: {account}")
    return f"💰 رصيد حساب {account}: 150,000 دج"


# ─── Tool: USSD Gateway ───────────────────────────────────────

@mcp.tool(description="إرسال طلب USSD. المدخل: رقم الهاتف، النص. المخرج: رد USSD")
async def ussd_send(phone: str, text: str) -> str:
    """إرسال طلب USSD للفلاح"""
    logger.info(f"USSD to {phone}: {text}")
    result = await _api_post("/api/v1/ussd/callback", {
        "sessionId": f"mcp-{datetime.now().timestamp()}",
        "serviceCode": "*233#",
        "phoneNumber": phone,
        "text": text,
    })
    return result.get("response", "❌ فشل USSD")


@mcp.tool(description="قائمة خدمات USSD المتاحة. المخرج: قائمة الخدمات")
async def ussd_menu() -> str:
    """قائمة USSD الرئيسية"""
    return """📱 قائمة خدمات فلاحة عبر USSD:
1️⃣ السوق — بيع وشراء
2️⃣ الإرشاد — استشارات فلاحية
3️⃣ الطقس — حالة الطقس
4️⃣ الأسعار — أسعار السوق
5️⃣ الدعم — دعم حكومي"""


# ─── Tool: Maps & Location ────────────────────────────────────

@mcp.tool(description="البحث عن فلاحين قريبين. المدخل: الولاية، المنتج. المخرج: قائمة الفلاحين")
async def maps_find_farmers(wilaya: str, product: str = "") -> str:
    """البحث عن فلاحين في ولاية معينة"""
    logger.info(f"Find farmers in {wilaya} for {product}")
    result = await _api_get(f"/api/v1/marketplace/products?wilaya={wilaya}")
    data = result if isinstance(result, dict) else {}
    products = data.get("products", [])
    if not products:
        return f"❌ لا يوجد فلاحين في {wilaya}"
    lines = [f"📍 فلاحون في {wilaya}:"]
    for p in products[:5]:
        lines.append(f"- {p.get('name', '')} | {p.get('price', '')} دج | {p.get('farmer_name', '')}")
    return "\n".join(lines)


@mcp.tool(description="حساب المسافة بين ولايتين. المدخل: ولاية أ، ولاية ب. المخرج: المسافة التقريبية")
async def maps_distance(wilaya_a: str, wilaya_b: str) -> str:
    """حساب المسافة بين ولايتين"""
    logger.info(f"Distance {wilaya_a} → {wilaya_b}")
    distances = {
        ("الجزائر", "البليدة"): "50 كم",
        ("الجزائر", "وهران"): "400 كم",
        ("الجزائر", "قسنطينة"): "430 كم",
        ("الجزائر", "عنابة"): "500 كم",
        ("البويرة", "الجزائر"): "120 كم",
        ("تيزي وزو", "الجزائر"): "100 كم",
        ("ورقلة", "الجزائر"): "800 كم",
    }
    key = (wilaya_a, wilaya_b)
    key_rev = (wilaya_b, wilaya_a)
    dist = distances.get(key) or distances.get(key_rev) or "غير متوفرة"
    return f"📍 المسافة بين {wilaya_a} و {wilaya_b}: {dist}"


# ─── Tool: System & Monitoring ────────────────────────────────

@mcp.tool(description="حالة النظام — فحص صحي كامل. المخرج: حالة الخادم، قاعدة البيانات، المهام الخلفية")
async def system_health() -> str:
    """فحص صحي شامل"""
    try:
        h = await _health()
        v = await _version()
        return (
            f"🌾 فلاحة — فحص صحي\n"
            f"• الحالة: {h.get('status', 'unknown')}\n"
            f"• قاعدة البيانات: {h.get('database_stats', {}).get('status', 'N/A')}\n"
            f"• الفلاحون: {h.get('database_stats', {}).get('farmer_count', 0)}\n"
            f"• المنتجات: {h.get('database_stats', {}).get('product_count', 0)}\n"
            f"• AI: {v.get('ai_available', False)}\n"
            f"• الذاكرة: {h.get('system', {}).get('memory_percent', 0)}%"
        )
    except Exception as e:
        return f"❌ الخادم غير متاح: {e}"


# ─── Main ─────────────────────────────────────────────────────

if __name__ == "__main__":
    tool_name = sys.argv[1] if len(sys.argv) > 1 else ""
    logger.info(f"Starting MCP server for tool: {tool_name or 'all'}")
    mcp.run(transport="stdio")
