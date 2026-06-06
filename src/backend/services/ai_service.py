from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from src.backend.config import settings

logger = logging.getLogger("flaha.nvidia")

SYSTEM_PROMPT_ADVISORY = """أنت وكيل فلاحي ذكي اسمك "فلاحة". أنت متخصص في الزراعة الجزائرية.
مهمتك: تقديم نصائح فلاحية دقيقة باللهجة الجزائرية (الدارجة) أو العربية الفصحى حسب لغة المستخدم.

قدراتك:
1. تشخيص أمراض النباتات (البياض الزغبي, التبقع, المن, ذبول, إلخ)
2. تقديم علاجات مناسبة (مبيدات متوفرة في الجزائر)
3. اقتراح مواعيد الزراعة والري
4. نصائح التسميد (الكيمياوي والعضوي)
5. التنبؤ بالمشاكل حسب الموسم والمنطقة

عند تشخيص مرض:
- اذكر اسم المرض بالعربية والفرنسية
- اشرح الأعراض التي يراها الفلاح
- أعط علاجاً عملياً باسم مبيد متوفر في السوق الجزائري
- حدد الجرعة وطريقة الاستعمال

ملاحظة: إذا لم تكن متأكداً من التشخيص، انصح الفلاح باستشارة مهندس فلاحي.
كن عملياً ومختصراً. الفلاح يحتاج حلولاً سريعة وواضحة."""

SYSTEM_PROMPT_NLP = """أنت خبير في فهم اللهجة الجزائرية (الدارجة) والعربية.
مهمتك: تحليل مقصد الفلاح من رسالته وإرجاعه بصيغة JSON.

أنواع المقاصد (intents):
- "sell": الفلاح يريد بيع منتج (عندي, نبيع, نحوس نبيع, عندنا فلاحة)
- "buy": يريد شراء (نشتري, حاب نشتري, شكون عندو)
- "advisory": استشارة عن مرض أو زرع (ورقة صفراء, دود, مرض, مسكين)
- "weather": سؤال عن الطقس (الشتا, الحر, البرد, الطقس)
- "price": سؤال عن الأسعار (شحال, قداه, السوم, السوق)
- "loan": طلب تمويل أو قرض (قرض, فلوس, نقود, بنك)
- "gov_support": سؤال عن الدعم (دعم, مساعدة, اعانة, الدولة)
- "diaspora": الجالية (فرنسا, أوروبا, تصدير, برشا)
- "help": طلب مساعدة عامة (مرحبا, واش, بدينا, شنو)
- "unknown": غير معروف

أرجع JSON بالشكل:
{"intent": "sell", "confidence": 0.95, "entities": {"crop": "طماطم", "quantity": "5", "unit": "قنطار", "wilaya": "البويرة"}}

في entities, استخرج المعلومات الموجودة فقط. اترك الحقول الفارغة إذا لم تكن موجودة."""


@dataclass
class AIResult:
    text: str
    success: bool
    error: str | None = None


async def ask_ai(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 1024,
    model: str = "",
) -> AIResult:
    """إرسال طلب إلى NVIDIA AI عبر OpenAI-compatible API"""
    if not settings.ai_available:
        return AIResult(
            text="",
            success=False,
            error="AI_API_KEY غير مضبوط. استخدم وضع المحاكاة.",
        )

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            base_url=settings.AI_BASE_URL,
            api_key=settings.AI_API_KEY,
        )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=model or settings.AI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return AIResult(text=response.choices[0].message.content, success=True)

    except ImportError:
        return AIResult(
            text="",
            success=False,
            error='حزمة openai غير مثبتة. شغّل: pip install openai',
        )
    except Exception as e:
        logger.error(f"NVIDIA AI error: {e}")
        return AIResult(text="", success=False, error=str(e))


async def analyze_nlp(text: str) -> dict:
    """تحليل نية الفلاح باستخدام NVIDIA AI"""
    if not settings.ai_available:
        return _mock_nlp(text)

    result = await ask_ai(
        prompt=f"حلل هذه الرسالة: {text}",
        system_prompt=SYSTEM_PROMPT_NLP,
        temperature=0.1,
        max_tokens=512,
    )

    if result.success:
        try:
            response_text = result.text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            parsed = json.loads(response_text)
            return {
                "intent": parsed.get("intent", "unknown"),
                "confidence": parsed.get("confidence", 0.5),
                "entities": parsed.get("entities", {}),
            }
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.warning(f"Failed to parse AI NLP response: {e}")
            return _mock_nlp(text)

    return _mock_nlp(text)


async def get_advisory(query: str, crop: str = "", wilaya: str = "") -> str:
    """استشارة فلاحية عبر NVIDIA AI"""
    if not settings.ai_available:
        return _mock_advisory(query, crop, wilaya)

    context = f"الفلاح في {wilaya}" if wilaya else ""
    context += f" ويسأل عن {crop}" if crop else ""

    prompt = f"{context}\n\nسؤال الفلاح: {query}\n\nأعطه نصيحة عملية بالدارجة أو العربية:"

    result = await ask_ai(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT_ADVISORY,
        temperature=0.5,
        max_tokens=1024,
    )

    if result.success:
        return result.text
    return _mock_advisory(query, crop, wilaya)


async def diagnose_image_from_bytes(image_bytes: bytes, crop: str = "") -> str:
    """تشخيص مرض من صورة عبر NVIDIA AI"""
    if not settings.ai_available:
        return _mock_image_diagnosis(crop)

    try:
        import base64

        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            base_url=settings.AI_BASE_URL,
            api_key=settings.AI_API_KEY,
        )

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        prompt = f"شخص هذا النبات. المحصول: {crop if crop else 'غير معروف'}. ماذا تلاحظ؟ وما العلاج؟"

        response = await client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_ADVISORY},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                    ],
                },
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content

    except ImportError:
        return _mock_image_diagnosis(crop)
    except Exception as e:
        logger.error(f"NVIDIA Vision error: {e}")
        return f"❌ تعذر تحليل الصورة: {str(e)}\n\n{_mock_image_diagnosis(crop)}"


async def translate_to_darja(text: str) -> str:
    """ترجمة أي نص إلى اللهجة الجزائرية"""
    if not settings.ai_available:
        return text

    result = await ask_ai(
        prompt=f"ترجم هذا النص إلى اللهجة الجزائرية الدارجة:\n\n{text}",
        temperature=0.3,
        max_tokens=512,
    )

    return result.text if result.success else text


# ─── Mock functions (مجانية تماماً — تعمل بدون أي API key) ─────


def _mock_nlp(text: str) -> dict:
    """تحليل النص محلياً بدون أي API"""
    sell_words = ["عندي", "نبيع", "بيع", "نحوس", "عندنا", "نبي نبيع"]
    buy_words = ["نشتري", "شراء", "نحوس نشتري", "حاب نشتري", "شكون"]
    advisory_words = ["مرض", "علاج", "مبيد", "ورقة", "زرع", "دود", "حشرة", "أصفر"]
    weather_words = ["الطقس", "شتا", "حر", "برد", "مطر", "الجو", "الشمس"]
    price_words = ["السعر", "السوق", "كم", "قيمة", "شحال", "قداه", "فلوس"]
    loan_words = ["قرض", "تمويل", "بنك", "نقود", "شيك"]
    gov_words = ["دعم", "مساعدة", "اعانة", "حكومة", "وزارة"]

    def _intent():
        for w in advisory_words:
            if w in text:
                return "advisory"
        for w in sell_words:
            if w in text:
                return "sell"
        for w in buy_words:
            if w in text:
                return "buy"
        for w in weather_words:
            if w in text:
                return "weather"
        for w in price_words:
            if w in text:
                return "price"
        for w in loan_words:
            if w in text:
                return "loan"
        for w in gov_words:
            if w in text:
                return "gov_support"
        if any(w in text for w in ["مرحبا", "السلام", "help", "واش"]):
            return "help"
        return "unknown"

    return {
        "intent": _intent(),
        "confidence": 0.7,
        "entities": {},
    }


def _mock_advisory(query: str, crop: str, wilaya: str) -> str:
    """رد استشارة وهمي يعمل بدون أي API"""
    disease_responses = {
        "البياض": (
            "🌱 تشخيص: **البياض الزغبي (Mildiou)**\n\n"
            "الأعراض: بقع صفراء على الأوراق + نمو أبيض تحت الورقة\n"
            "العلاج: رش **مانكوزب (Mancozèbe)** 2.5 كغ/هكتار أو **ريدوميل (Ridomil)**\n"
            "كرر الرش كل 7 أيام بعد المطر\n"
        ),
        "المن": (
            "🌱 تشخيص: **المن (Puceron)**\n\n"
            "الأعراض: حشرات صغيرة خضراء/سوداء + أوراق ملتوية\n"
            "العلاج: رش **بيريميكارب (Pirimicarb)** أو صابون بوتاسيوم\n"
            "طريقة طبيعية: رش ماء + سائل غسيل\n"
        ),
        "ذبول": (
            "🌱 تشخيص: **ذبول الفيوزاريوم (Fusarium)**\n\n"
            "الأعراض: ذبول مفاجئ + اصفرار الأوراق السفلية\n"
            "العلاج: عزل النبات المصاب + تعقيم التربة\n"
            "مبيد: **بيلوس (Bélos)** أو **توبسين (Topsine)**\n"
        ),
    }

    for key, response in disease_responses.items():
        if key in query:
            return response

    return (
        f"🌱 **نصيحة فلاحية**{ ' لـ ' + crop if crop else ''}{' في ' + wilaya if wilaya else ''}\n\n"
        f"لمعلومات دقيقة، يرجى وصف المشكلة بالتفصيل:\n"
        f"• ما هي الأعراض التي تلاحظها على النبات؟\n"
        f"• متى بدأت المشكلة؟\n"
        f"• هل انتشرت إلى نباتات أخرى؟\n\n"
        f"أو أرسل صورة للنبات للتشخيص الدقيق"
    )


def _mock_image_diagnosis(crop: str) -> str:
    """تشخيص وهمي للصور"""
    crops_with_responses = {
        "طماطم": (
            "🔍 **تحليل الصورة**\n\n"
            "بناءً على الصورة، الأعراض تشير إلى احتمال **البياض الزغبي (Mildiou)**\n\n"
            "✅ العلاج: رش Mancozèbe 80% WP 2.5 كغ/هكتار\n"
            "✅ وقاية: تصريف المياه + تهوية النباتات\n"
            "⚠️ ينصح باستشارة مهندس فلاحي لتأكيد التشخيص"
        ),
        "زيتون": (
            "🔍 **تحليل الصورة**\n\n"
            "الأعراض تشير إلى احتمالية **عين الطاووس (Œil de Paon)**\n\n"
            "✅ العلاج: رش نحاس (Bouillie Bordelaise) 10 كغ/هكتار\n"
            "✅ وقاية: تقليم الأفرع المصابة + جمع الأوراق المتساقطة"
        ),
    }

    return crops_with_responses.get(
        crop,
        "🔍 **تحليل الصورة**\n\n"
        "تم استلام الصورة للتشخيص.\n\n"
        "لنتيجة أدق، يرجى:\n"
        "1️⃣ ذكر اسم المحصول\n"
        "2️⃣ وصف الأعراض التي تلاحظها\n"
        "3️⃣ إرسال صورة واضحة للأوراق المصابة\n\n"
        "يمكنك تفعيل NVIDIA AI API للتشخيص الدقيق عبر الذكاء الاصطناعي",
    )
