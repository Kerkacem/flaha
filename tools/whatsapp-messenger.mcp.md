# MCP Tool: WhatsApp Messenger

## الوصف
أداة إرسال واستقبال رسائل واتساب. القناة الرئيسية للتواصل مع الفلاحين.

## التقنية
- **API**: 360dialog (WhatsApp Business API Partner)
- **البديل**: Twilio WhatsApp API
- **النوع**: REST API / Webhook

## الأوامر

### send_message
إرسال رسالة نصية أو وسائط عبر واتساب.

```json
{
  "to": "+213XXXXXXXXX",
  "type": "text|image|document|audio",
  "content": "السلام عليكم...",
  "media_url": "https://..." // إذا type = image/document/audio
}
```

### send_template
إرسال قالب واتساب معتمد (للتذكيرات، الإشعارات).

```json
{
  "to": "+213XXXXXXXXX",
  "template": "order_confirmation",
  "parameters": ["المنتج", "الكمية", "السعر"]
}
```

### receive_webhook
استقبال الرسائل الواردة من الفلاحين.

```json
{
  "from": "+213XXXXXXXXX",
  "type": "text|image|audio",
  "body": "عندي طماطم 5 قناطير",
  "media_id": "..." // للصور والصوت
}
```

## المتطلبات
- رقم واتساب Business معتمد
- Webhook endpoint (Ngrok في التطوير)
- قوالب واتساب معتمدة (للإشعارات)
