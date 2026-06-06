# تكامل Facebook Ads API

## الوصف
ربط منصة فلاحة مع Facebook/Instagram Ads لإعلانات تلقائية لمنتجات الفلاحين.

## API
- **المصدر**: Meta Business API
- **المصادقة**: Facebook Access Token (صفحة + Business Manager)

## الأوامر

### create_ad_campaign
إنشاء حملة إعلانية لمنتج فلاحي.

```json
{
  "product": {
    "name": "زيت زيتون بكري",
    "description": "زيت زيتون بكري ممتاز من البويرة",
    "price": 3000,
    "images": ["https://..."],
    "farmer_name": "علي بن محمد",
    "region": "البويرة"
  },
  "target": {
    "audience": "diaspora|local",
    "country": "FR|CA|DZ",
    "age_min": 25,
    "age_max": 65,
    "interests": ["Algerian food", "North African cuisine", "مطبخ جزائري"]
  },
  "budget": {
    "daily": 500,  // دج
    "total": 5000  // دج
  }
}
```

### create_product_catalog
إنشاء كتالوج منتجات للفلاح.

## الفئات المستهدفة للإعلانات

| الفئة | الجمهور | الميزانية المقترحة (دج/يوم) |
|-------|---------|---------------------------|
| الجالية في فرنسا | جزائريون 25-55 سنة | 2000-5000 |
| الجالية في كندا | جزائريون 30-50 سنة | 1500-3000 |
| محلي (ولاية) | سكان الولاية | 500-1000 |
| محلي (وطني) | كل الجزائر | 1000-3000 |
