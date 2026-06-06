"""
محرك NLP بالدارجة — يستخدم NVIDIA AI كخيار أول، والكلمات المفتاحية كاحتياطي مجاني
"""

from __future__ import annotations

import logging
from enum import Enum

from src.backend.services.ai_service import analyze_nlp

logger = logging.getLogger("flaha.nlp")


class Intent(str, Enum):
    SELL = "sell"
    BUY = "buy"
    ADVISORY = "advisory"
    WEATHER = "weather"
    PRICE = "price"
    LOAN = "loan"
    GOV_SUPPORT = "gov_support"
    DIASPORA = "diaspora"
    HELP = "help"
    UNKNOWN = "unknown"


class FlahaNLPEngine:
    """محرك NLP — يستخدم NVIDIA AI إن وجد، أو الكلمات المفتاحية محلياً"""

    def __init__(self):
        pass

    def analyze(self, text: str) -> dict:
        """تحليل النص — يحاول AI أولاً، ثم يقع على المحلي"""
        return self._keyword_analyze(text)

    async def analyze_async(self, text: str) -> dict:
        """تحليل غير متزامن — يحاول AI"""
        result = await analyze_nlp(text)
        if result["intent"] != "unknown":
            return result
        return self._keyword_analyze(text)

    def _keyword_analyze(self, text: str) -> dict:
        """تحليل بالكلمات المفتاحية — مجاني 100%, يعمل بدون إنترنت"""
        text = text.strip()

        intents = {
            Intent.SELL: ["عندي", "نبيع", "بيع", "نحوس", "عندنا", "نبي نبيع", "حاب نبيع"],
            Intent.BUY: ["نشتري", "شراء", "نحوس نشتري", "حاب نشتري", "شكون عندو"],
            Intent.ADVISORY: ["مرض", "علاج", "مبيد", "ورقة", "زرع", "دود", "حشرة", "أصفر",
                              "نبات", "دواء", "سقي", "ري"],
            Intent.WEATHER: ["الطقس", "شتا", "حر", "برد", "مطر", "الجو", "الشمس", "بردان"],
            Intent.PRICE: ["السعر", "السوق", "كم", "قيمة", "شحال", "قداه", "ثمن", "بشحال"],
            Intent.LOAN: ["قرض", "تمويل", "بنك", "نقود", "شيك", "دينار"],
            Intent.GOV_SUPPORT: ["دعم", "مساعدة", "اعانة", "حكومة", "وزارة", "الدولة"],
            Intent.DIASPORA: ["فرنسا", "أوروبا", "تصدير", "جالية", "برشا", "هجرة", "خارج"],
            Intent.HELP: ["مرحبا", "السلام", "واش", "شنو", "بدينا", "help", "menu", "قائمة"],
        }

        best_intent = Intent.UNKNOWN
        max_score = 0

        for intent, keywords in intents.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > max_score:
                max_score = score
                best_intent = intent

        return {
            "intent": best_intent.value,
            "confidence": min(0.5 + max_score * 0.1, 0.95),
            "entities": self._extract_entities(text),
            "source": "keyword",
        }

    def _extract_entities(self, text: str) -> dict:
        """استخراج الكيانات من النص"""
        entities = {}

        # Wilaya detection
        from src.backend.services.weather_service import ALGERIAN_CITIES
        for wilaya in ALGERIAN_CITIES:
            if wilaya in text:
                entities["wilaya"] = wilaya
                break

        # Price detection
        import re
        price_match = re.search(r'(\d+)\s*(دج|دينار|€|يورو|دولار)', text)
        if price_match:
            entities["price"] = price_match.group(1)

        # Quantity detection
        qty_match = re.search(r'(\d+)\s*(قنطار|كغ|لتر|كلغ|kg|KG|L|l)', text)
        if qty_match:
            entities["quantity"] = qty_match.group(1)
            entities["unit"] = qty_match.group(2)

        return entities


# ─── Convenience functions ──────────────────────────────────────


def intent_to_arabic(intent: str) -> str:
    """ترجمة نوع النية إلى العربية"""
    mapping = {
        "sell": "بيع",
        "buy": "شراء",
        "advisory": "استشارة",
        "weather": "طقس",
        "price": "سعر",
        "loan": "قرض",
        "gov_support": "دعم حكومي",
        "diaspora": "جالية",
        "help": "مساعدة",
        "unknown": "غير معروف",
    }
    return mapping.get(intent, intent)
