# تكامل خدمات التوصيل Yalidine

## الوصف
ربط منصة فلاحة مع Yalidine لخدمات التوصيل في الجزائر.

## API
- **الموقع**: https://api.yalidine.net
- **المصادقة**: API Key
- **التوثيق**: https://docs.yalidine.net

## الأوامر

### create_delivery
إنشاء طلب توصيل.

```json
{
  "from": {
    "wilaya": "البويرة",
    "commune": "سوق الخميس",
    "address": "مزرعة فلاح"
  },
  "to": {
    "wilaya": "الجزائر",
    "commune": "باب الزوار",
    "address": "سوق الجملة"
  },
  "parcel": {
    "weight_kg": 50,
    "description": "طماطم طازجة",
    "value": 5000
  },
  "payment": "cash_on_delivery"
}
```

### track_delivery
تتبع الشحنة.

```json
{
  "tracking_id": "YL-2026-XXXXX"
}
```

### get_price
حساب تكلفة التوصيل.

```json
{
  "from_wilaya": "البويرة",
  "to_wilaya": "الجزائر",
  "weight_kg": 50
}
```

## المميزات
- تغطية 58 ولاية
- دفع عند الاستلام (Cash on Delivery)
- تتبع مباشر
- تأمين الشحنات
