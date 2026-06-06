from __future__ import annotations

from datetime import datetime

# ─── Government Programs Database ──────────────────────────────


GOV_PROGRAMS: dict[str, dict] = {
    "FNDIA": {
        "name": "الصندوق الوطني للتنمية الفلاحية",
        "description": "دعم الفلاحين الصغار",
        "max_amount_dzd": 500000,
        "requirements": [
            "بطاقة فلاح سارية",
            "شهادة ملكية الأرض",
            "رخصة استغلال",
            "بطاقة التعريف الوطنية",
            "شهادة الإقامة",
            "شهادة كفالة (إذا كان مستأجراً)",
        ],
        "conditions": ["أقل من 10 هكتار", "الاستفادة مرة كل 5 سنوات", "ملء الاستمارة"],
        "deadline": "30 جوان 2026",
        "bank": "BADR",
    },
    "FGVA": {
        "name": "صندوق ضمان الفلاحة",
        "description": "ضمان القروض الفلاحية للبنوك",
        "max_amount_dzd": 10000000,
        "coverage_pct": 70,
        "requirements": [
            "بطاقة فلاح",
            "دراسة الجدوى",
            "سجل زراعي (إن وجد)",
            "كشف حساب بنكي",
        ],
        "conditions": ["حتى 7 سنوات", "رسوم 2% من مبلغ القرض"],
        "bank": "CPA / BADR",
    },
    "دعم المدخلات": {
        "name": "دعم المدخلات الفلاحية",
        "description": "دعم شراء البذور والأسمدة والمبيدات",
        "support_rates": {
            "البذور المعتمدة": "50%",
            "الأسمدة": "40%",
            "المبيدات": "30%",
            "معدات الري بالتنقيط": "45%",
            "الدفيئات البلاستيكية": "50%",
        },
        "max_amount_dzd": 500000,
        "requirements": ["بطاقة فلاح", "فاتورة الشراء", "إثبات التسليم"],
    },
    "التأمين الفلاحي (CNA)": {
        "name": "التأمين الفلاحي",
        "description": "تأمين المحاصيل ضد الكوارث الطبيعية",
        "risks": ["البرد", "الصقيع", "الجفاف", "الفيضانات", "الحرائق"],
        "coverage_pct": {
            "البرد": 80,
            "الصقيع": 70,
            "الجفاف": 60,
            "الفيضانات": 85,
            "الحرائق": 90,
        },
    },
    "الفلاحة التضامنية": {
        "name": "برنامج الفلاحة التضامنية",
        "description": "تشجيع الفلاحة في المناطق الجبلية والسهوب",
        "support_pct": 80,
        "target_wilayas": [
            "البويرة", "تيزي وزو", "بجاية", "باتنة", "خنشلة",
            "تبسة", "الأغواط", "الجلفة", "المسيلة", "تيسمسيلت",
        ],
        "projects": ["غرس أشجار", "تربية مواشي", "نحل", "زراعة جبلية"],
    },
}

# ─── Deadline Tracker ──────────────────────────────────────────


UPCOMING_DEADLINES: list[dict] = [
    {
        "program": "FNDIA",
        "deadline": datetime(2026, 6, 30),
        "description": "آخر أجل لتقديم ملفات الدعم",
        "days_remaining": lambda: (datetime(2026, 6, 30) - datetime.now()).days,
    },
    {
        "program": "دعم المدخلات",
        "deadline": datetime(2026, 7, 15),
        "description": "آخر أجل لشراء المدخلات المدعومة",
        "days_remaining": lambda: (datetime(2026, 7, 15) - datetime.now()).days,
    },
]


async def get_program_info(program_code: str) -> dict:
    """الحصول على معلومات برنامج دعم"""
    program = GOV_PROGRAMS.get(program_code)
    if not program:
        return {"status": "error", "message": f"البرنامج '{program_code}' غير موجود"}

    return {"status": "found", "program": program_code, "details": program}


async def generate_application_form(program: str, farmer_data: dict) -> dict:
    """توليد استمارة الطلب آلياً"""
    program_info = GOV_PROGRAMS.get(program, {})
    requirements = program_info.get("requirements", [])

    # Check which documents we have
    missing_docs = []
    for req in requirements:
        if req not in farmer_data.get("documents", []):
            missing_docs.append(req)

    form_data = {
        "program": program,
        "farmer_name": farmer_data.get("name"),
        "farmer_phone": farmer_data.get("phone"),
        "wilaya": farmer_data.get("wilaya"),
        "land_hectares": farmer_data.get("land_hectares"),
        "generated_at": datetime.now().isoformat(),
    }

    return {
        "form": form_data,
        "missing_documents": missing_docs,
        "status": "incomplete" if missing_docs else "ready",
        "message": (
            "📋 استمارة الطلب جاهزة!\n"
            + (f"\n⚠️ الوثائق الناقصة: {', '.join(missing_docs)}" if missing_docs else "")
            + "\nللتقديم، أرسل صور الوثائق الناقصة."
        ),
    }


async def check_upcoming_deadlines() -> list[dict]:
    """فحص المواعيد النهائية القادمة"""
    reminders = []
    for deadline in UPCOMING_DEADLINES:
        days = (deadline["deadline"] - datetime.now()).days
        if 0 <= days <= 30:
            reminders.append(
                {
                    "program": deadline["program"],
                    "description": deadline["description"],
                    "days_remaining": days,
                    "urgent": days <= 7,
                }
            )
    return reminders


async def get_wilaya_delegate(wilaya: str) -> dict:
    """الحصول على معلومات المندوب الفلاحي للولاية"""
    delegates = {
        "البويرة": {"name": "مفتش الفلاحة لولاية البويرة", "phone": "026 92 12 34", "address": "مديرية المصالح الفلاحية، البويرة"},
        "بليدة": {"name": "مفتش الفلاحة لولاية بليدة", "phone": "025 41 23 45", "address": "مديرية المصالح الفلاحية، بليدة"},
    }

    delegate = delegates.get(wilaya)
    if not delegate:
        return {"status": "not_found", "message": f"لم نجد معلومات المندوب لولاية {wilaya}"}

    return {"status": "found", "wilaya": wilaya, "delegate": delegate}
