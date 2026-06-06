# 🏗️ المعمارية التقنية — Technical Architecture

> **ملاحظة:** هذه المعمارية تعكس الإصدار الحالي (v0.1.0) المبني على **100% Free Tier**.
> كل الخدمات الأساسية تشتغل بدون أي API key مدفوع.

## نظرة عامة

```
┌─────────────────────────────────────────────────────────────┐
│                        قنوات الوصول                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │  واتساب   │  │   USSD   │  │  أندرويد │  │    صوتي     │ │
│  │ WhatsApp  │  │  *233#   │  │   (مستقبلاً)│  │  (مستقبلاً)  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬──────┘ │
└───────┼──────────────┼────────────┼────────────────┼───────┘
        │              │            │                │
        ▼              ▼            ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                    طبقة API (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  auth │  rate-limit │  webhook router  │  Dashboard  │   │
│  │  JWT  │  60 req/min │  WhatsApp/Meta   │  /health    │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────┬──────────────────────────────────────────┬───┘
                │                                          │
        ┌───────┴──────────┐                    ┌──────────┴──────┐
        ▼                  ▼                    ▼                 ▼
┌───────────────┐  ┌───────────────┐  ┌──────────────────────┐
│  وكيل فلاحة    │  │  محرك AI      │  │  مهام الخلفية        │
│  Conversation │  │  Gemini (مجاني)│  │  (asyncio — لا Redis)│
│  ┌─────────┐  │  │  ┌──────────┐ │  │  ┌──────────────┐   │
│  │Marketpl.│  │  │  │ NLP     │ │  │  │ تحديث الأسعار│   │
│  ├─────────┤  │  │  │بالدارجة │ │  │  │ كل 6 ساعات   │   │
│  │Advisory │  │  │  ├──────────┤ │  │  ├──────────────┤   │
│  ├─────────┤  │  │  │استشارات │ │  │  │ فحص الطقس    │   │
│  │Finance  │  │  │  │فلاحية   │ │  │  │ كل 4 ساعات   │   │
│  ├─────────┤  │  │  ├──────────┤ │  │  ├────────────┤   │
│  │Logistics│  │  │  │ Vision   │ │  │  │ تذكيرات     │   │
│  └─────────┘  │  │  │(صور نبات)│ │  │  │ يومياً      │   │
│               │  │  └──────────┘ │  │  └──────────────┘   │
│  • 12 حالة    │  │  أو محاكاة   │  └──────────────────────┘
│  • 9 نوايا    │  │  محلية مجانية│
└───────────────┘  └───────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                      قاعدة البيانات                          │
│  ┌──────────────────────┐  ┌────────────────────────────┐   │
│  │  SQLite (افتراضي)    │  │  PostgreSQL (اختياري)      │   │
│  │   • مجاني — بدون إعداد│  │   • للفلاحين الكبار        │   │
│  │   • WAL mode         │  │   • Scalability عالية      │   │
│  │   • مناسب لـ 1000    │  │                            │   │
│  │     فلاح/ولاية       │  │                            │   │
│  └──────────────────────┘  └────────────────────────────┘   │
│  • 11 جدول: المستخدمون, المنتجات, الصفقات, الأسعار,         │
│    الاستشارات, القروض, واتساب, الإشعارات, الأجهزة, الجلسات  │
└─────────────────────────────────────────────────────────────┘
```

## مكدس التقنيات الحالي (100% Free Tier)

### Backend
- **اللغة**: Python 3.12+
- **الFramework**: FastAPI (جميع endpoints)
- **قاعدة البيانات**: SQLite (aiosqlite) — افتراضي، أو PostgreSQL
- **المهام الخلفية**: asyncio.create_task (بديل Celery/Redis مجاني)
- **التخزين المؤقت**: In-memory dict (للطقس — 10 دقائق TTL)

### الذكاء الاصطناعي
- **المحرك الرئيسي**: Google Gemini 2.0 Flash (مجاني ∞)
- **المحاكاة المحلية**: mock_* functions تعمل بدون API key
- **NLP بالدارجة**: تحليل نوايا + كلمات مفتاحية
- **تشخيص الصور**: Gemini Vision أو mock diagnosis

### قنوات التواصل
- **واتساب**: Meta Cloud API (مجاني 1000 محادثة/شهر)
- **USSD**: *233# (يتطلب اتفاق مع المتصل)
- **التطبيق**: قيد التطوير (ويب dashboard حالياً)

### التكاملات الخارجية (كلها اختيارية — تعمل بالمحاكاة)
- **التوصيل**: Yalidine API
- **الدفع**: Baridi Mob API
- **الطقس**: OpenWeatherMap (مجاني 1000 طلب/يوم)

### الأمان
- **المصادقة**: JWT (HMAC-SHA256 مخصص)
- **معدل الطلبات**: 60 طلب/دقيقة لكل IP
- **Webhook**: التحقق من توقيع Meta

## ملاحظات التطوير

### للتشغيل المحلي
```bash
pip install -e .
uvicorn src.backend.main:app --reload
# → http://localhost:8000 (Dashboard)
# → http://localhost:8000/docs (Swagger)
# → http://localhost:8000/health (System Health)
```

### للترقية إلى PostgreSQL
1. غيّر `DATABASE_TYPE=postgresql` في `.env`
2. اضبط `DATABASE_URL`
3. شغل `pip install asyncpg`
4. أعد تشغيل الخادم

### للإضافة المستقبلية (عند توفر التمويل)
- LangChain / CrewAI للوكلاء المتقدمين
- Whisper + Edge TTS للصوت
- React Native (Expo) للتطبيق
- Redis للتخزين المؤقت المتقدم
- Object Storage (S3) للصور
- ViT المدرب لتشخيص الأمراض
- **الخرائط**: Google Maps API / OpenStreetMap
- **الإعلانات**: Meta Business API (Facebook/Instagram)

## نموذج البيانات الأساسي

```sql
-- الفلاحين
CREATE TABLE farmers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  phone TEXT UNIQUE NOT NULL,
  wilaya TEXT NOT NULL,
  commune TEXT NOT NULL,
  land_hectares DECIMAL(5,2),
  has_baridi_mob BOOLEAN DEFAULT false,
  rating_avg DECIMAL(2,1) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- المنتجات
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id UUID REFERENCES farmers(id),
  name TEXT NOT NULL,
  category TEXT NOT NULL,  -- خضار/فواكه/حبوب/زيت/عسل
  quantity DECIMAL(10,2),
  unit TEXT NOT NULL,  -- كغ/لتر/قنطار
  price DECIMAL(10,2),
  wilaya TEXT NOT NULL,
  images TEXT[],
  status TEXT DEFAULT 'available',  -- available/sold/cancelled
  created_at TIMESTAMPTZ DEFAULT now()
);

-- الصفقات
CREATE TABLE transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID REFERENCES products(id),
  buyer_id UUID REFERENCES farmers(id),
  seller_id UUID REFERENCES farmers(id),
  quantity DECIMAL(10,2),
  total_price DECIMAL(10,2),
  commission DECIMAL(10,2),
  delivery_status TEXT DEFAULT 'pending',  -- pending/in_transit/delivered
  payment_status TEXT DEFAULT 'pending',  -- pending/held/released
  buyer_rating INTEGER CHECK (buyer_rating BETWEEN 1 AND 5),
  seller_rating INTEGER CHECK (seller_rating BETWEEN 1 AND 5),
  created_at TIMESTAMPTZ DEFAULT now()
);
```

## تدفق البيانات (مثال: بيع عبر واتساب)

```
1. فلاح → واتساب: "عندي طماطم 5 قناطير بليدة ب 2000"
2. Webhook → API Gateway → مشغّل الوكيل
3. وكيل السوق يحلل الرسالة:
   - يستخرج: المنتج=طماطم, الكمية=5, الوحدة=قنطار, المنطقة=بليدة, السعر=2000
   - يسجل في قاعدة البيانات (products)
   - يبحث عن مشترين مهتمين في نفس المنطقة
4. وكيل السوق يرد عبر واتساب:
   "تم تسجيل إعلانك ✅ رمز المتابعة: FL-2026-001
    في عندك 3 مشترين مهتمين:
    1. تاجر X - بليدة - 1800 دج
    2. تاجر Y - الجزائر - 2000 دج
    نضغط على الرقم باش تقبل؟"
5. الفلاح يختار → الصفقة تتأكد
6. وكيل اللوجستيك يرتب التوصيل
7. بعد الاستلام → الدفع يتحرر للفلاح
```

## مقاييس الأداء المستهدفة

| المقياس | الهدف |
|---------|-------|
| وقت استجابة واتساب | < 5 ثواني |
| وقت تحليل الصورة | < 10 ثواني |
| وقت معالجة الطلب | < 30 ثانية |
| وقت التوصيل المحلي | < 24 ساعة |
| وقت التوصيل الدولي | < 7 أيام |
| uptime | 99.9% |
| التكلفة لكل فلاح | < $1.50/موسم |
