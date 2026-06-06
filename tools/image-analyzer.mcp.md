# MCP Tool: Image Analyzer

## الوصف
تحليل صور النباتات لتشخيص الأمراض والآفات ونقص العناصر الغذائية.

## التقنية
- **النموذج**: Vision Transformer (ViT) مدرب على قاعدة بيانات أمراض النباتات
- **البديل**: PlantVillage API, TensorFlow Serving
- **النوع**: REST API

## الأوامر

### diagnose_plant
تشخيص حالة النبات من الصورة.

```json
{
  "image_url": "https://...",
  "crop_type": "tomato|potato|olive|date_palm|wheat|citrus",
  "region": "البويرة"
}
```

النتيجة:
```json
{
  "disease": "Early Blight (Alternaria solani)",
  "confidence": 0.92,
  "treatment": "رش بمبيد X بتركيز Y",
  "severity": "متوسط",
  "recommended_products": [
    {"name": "مبيد X", "price": "1500 دج/لتر", "supplier": "مورد Y"}
  ]
}
```

### analyze_soil
تحليل التربة من الصورة (تقديري).

```json
{
  "image_url": "https://...",
  "region": "البويرة"
}
```

### detect_pest
كشف الآفات من الصور.

## تحسينات للهجة الجزائرية
- تدريب إضافي على أمراض المحاصيل الجزائرية
- قاعدة بيانات صور من حقول جزائرية
- أسماء الأمراض بالدارجة + الفرنسية + العربية
