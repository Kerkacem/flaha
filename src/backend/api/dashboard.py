"""واجهة المستخدم الأساسية (Dashboard HTML)"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard"])


DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>فلاحة — لوحة التحكم</title>
    <style>
        :root {
            --primary: #16a34a;
            --primary-dark: #15803d;
            --secondary: #f59e0b;
            --bg: #f0fdf4;
            --card: #ffffff;
            --text: #1f2937;
            --text-light: #6b7280;
            --danger: #ef4444;
            --info: #3b82f6;
            --radius: 12px;
        }
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 20px;
        }
        .container { max-width: 1200px; margin:0 auto; }
        header {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            padding: 24px 32px;
            border-radius: var(--radius);
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        header h1 { font-size: 1.8rem; }
        header .subtitle { opacity:0.9; font-size:0.9rem; }
        .badge {
            background: rgba(255,255,255,0.2);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
        }
        .grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap:16px; margin-bottom:24px; }
        .card {
            background: var(--card);
            border-radius: var(--radius);
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .card .label { color:var(--text-light); font-size:0.85rem; }
        .card .value { font-size:2rem; font-weight:700; color:var(--primary); }
        .card .change { font-size:0.8rem; margin-top:4px; }
        .card .change.up { color:var(--primary); }
        .card .change.down { color:var(--danger); }
        .section { margin-bottom: 24px; }
        .section h2 { font-size:1.3rem; margin-bottom:12px; color:var(--primary-dark); }
        table {
            width:100%;
            border-collapse: collapse;
            background: var(--card);
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        th, td { padding:12px 16px; text-align:right; }
        th { background: #f8fafc; color:var(--text-light); font-size:0.85rem; font-weight:600; }
        tr:not(:last-child) td { border-bottom:1px solid #f1f5f9; }
        tr:hover td { background:#f8fafc; }
        .status {
            display:inline-block;
            padding:2px 10px;
            border-radius:12px;
            font-size:0.8rem;
        }
        .status.active { background:#dcfce7; color:#166534; }
        .status.pending { background:#fef3c7; color:#92400e; }
        .status.error { background:#fee2e2; color:#991b1b; }
        .quick-actions {
            display:flex;
            gap:8px;
            flex-wrap:wrap;
        }
        .btn {
            display:inline-flex;
            align-items:center;
            gap:6px;
            padding:10px 20px;
            border-radius:8px;
            border:none;
            font-size:0.9rem;
            cursor:pointer;
            text-decoration:none;
            transition: all 0.2s;
        }
        .btn-primary { background:var(--primary); color:white; }
        .btn-primary:hover { background:var(--primary-dark); }
        .btn-secondary { background:var(--secondary); color:white; }
        .btn-info { background:var(--info); color:white; }
        .btn-outline { background:transparent; border:2px solid var(--primary); color:var(--primary); }
        .btn-outline:hover { background:var(--primary); color:white; }
        .services {
            display:grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap:12px;
        }
        .service-card {
            background:var(--card);
            border-radius:var(--radius);
            padding:16px;
            text-align:center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            cursor:pointer;
            transition: transform 0.2s;
        }
        .service-card:hover { transform:translateY(-2px); }
        .service-card .icon { font-size:2rem; margin-bottom:8px; }
        .service-card .name { font-weight:600; margin-bottom:4px; }
        .service-card .desc { font-size:0.8rem; color:var(--text-light); }
        footer {
            text-align:center;
            color:var(--text-light);
            font-size:0.85rem;
            padding:24px 0;
        }
        @media (max-width: 600px) {
            header { flex-direction:column; text-align:center; gap:8px; }
            .grid { grid-template-columns:1fr 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>🌾 فلاحة</h1>
                <div class="subtitle">الوكيل الفلاحي الذكي | النسخة 0.1.0</div>
            </div>
            <div class="badge">🟢 النظام شغال</div>
        </header>

        <div class="quick-actions section">
            <a href="/docs" class="btn btn-primary">📖 التوثيق</a>
            <a href="/api/v1/marketplace/products" class="btn btn-info">🛒 السوق</a>
            <a href="/health" class="btn btn-outline">❤️ الصحة</a>
        </div>

        <div class="grid" id="stats-grid">
            <div class="card"><div class="label">👨‍🌾 الفلاحون</div><div class="value" id="farmers">-</div></div>
            <div class="card"><div class="label">🛍️ المنتجات</div><div class="value" id="products">-</div></div>
            <div class="card"><div class="label">🤝 الصفقات</div><div class="value" id="transactions">-</div></div>
            <div class="card"><div class="label">💰 حجم التداول</div><div class="value" id="volume">-</div></div>
        </div>

        <div class="section">
            <h2>⚡ الخدمات</h2>
            <div class="services">
                <div class="service-card"><div class="icon">🛒</div><div class="name">السوق</div><div class="desc">بيع وشراء المنتجات</div></div>
                <div class="service-card"><div class="icon">🌤️</div><div class="name">الطقس</div><div class="desc">حالة الطقس + نصائح</div></div>
                <div class="service-card"><div class="icon">🔬</div><div class="name">التشخيص</div><div class="desc">كشف أمراض النباتات</div></div>
                <div class="service-card"><div class="icon">💳</div><div class="name">التمويل</div><div class="desc">قروض + تمويل</div></div>
                <div class="service-card"><div class="icon">📦</div><div class="name">التوصيل</div><div class="desc">شحن + لوجستيك</div></div>
                <div class="service-card"><div class="icon">🌍</div><div class="name">الجالية</div><div class="desc">تصدير للخارج</div></div>
                <div class="service-card"><div class="icon">🏛️</div><div class="name">الدعم</div><div class="desc">برامج حكومية</div></div>
                <div class="service-card"><div class="icon">🤖</div><div class="name">المساعد</div><div class="desc">واتساب + USSD</div></div>
            </div>
        </div>

        <div class="section">
            <h2>🎯 الروابط السريعة</h2>
            <table>
                <thead>
                    <tr><th>الخدمة</th><th>الرابط</th><th>الحالة</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <td>📖 توثيق API (Swagger)</td>
                        <td><code><a href="/docs">/docs</a></code></td>
                        <td><span class="status active">مفعل</span></td>
                    </tr>
                    <tr>
                        <td>📖 توثيق API (ReDoc)</td>
                        <td><code><a href="/redoc">/redoc</a></code></td>
                        <td><span class="status active">مفعل</span></td>
                    </tr>
                    <tr>
                        <td>❤️ فحص الصحة</td>
                        <td><code><a href="/health">/health</a></code></td>
                        <td><span class="status active">مفعل</span></td>
                    </tr>
                    <tr>
                        <td>🛒 قائمة المنتجات</td>
                        <td><code><a href="/api/v1/marketplace/products">/api/v1/marketplace/products</a></code></td>
                        <td><span class="status active">مفعل</span></td>
                    </tr>
                    <tr>
                        <td>🌍 باقات الجالية</td>
                        <td><code><a href="/api/v1/diaspora/plans">/api/v1/diaspora/plans</a></code></td>
                        <td><span class="status active">مفعل</span></td>
                    </tr>
                    <tr>
                        <td>🏛️ برامج الدعم</td>
                        <td><code>/api/v1/gov-support/programs/</code></td>
                        <td><span class="status active">مفعل</span></td>
                    </tr>
                    <tr>
                        <td>🤖 Webhook واتساب</td>
                        <td><code>/api/v1/whatsapp/webhook</code></td>
                        <td><span class="status pending">ينتظر التهيئة</span></td>
                    </tr>
                    <tr>
                        <td>📞 USSD Callback</td>
                        <td><code>/api/v1/ussd/callback</code></td>
                        <td><span class="status pending">ينتظر التهيئة</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <footer>
            🌾 فلاحة v0.1.0 — تم البناء بـ ❤️ للفلاح الجزائري
        </footer>
    </div>

    <script>
    async function loadStats() {
        try {
            const resp = await fetch('/health');
            const data = await resp.json();

            document.getElementById('farmers').textContent = data.database_stats?.farmer_count ?? '-';
            document.getElementById('products').textContent = data.database_stats?.product_count ?? '-';
            document.getElementById('transactions').textContent = data.database_stats?.transaction_count ?? '-';

            const vol = data.database_stats?.total_volume ?? 0;
            document.getElementById('volume').textContent = Number(vol).toLocaleString('ar-DZ') + ' دج';
        } catch(e) {
            document.getElementById('farmers').textContent = '⚠️';
            document.getElementById('products').textContent = '⚠️';
            document.getElementById('transactions').textContent = '⚠️';
            document.getElementById('volume').textContent = '⚠️';
        }
    }
    loadStats();
    setInterval(loadStats, 30000);
    </script>
</body>
</html>
"""


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def get_dashboard():
    """لوحة تحكم فلاحة"""
    return HTMLResponse(content=DASHBOARD_HTML)


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root_redirect():
    """توجيه الجذر إلى لوحة التحكم"""
    return HTMLResponse(content=DASHBOARD_HTML)
