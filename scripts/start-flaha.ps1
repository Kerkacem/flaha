# سكريبت بدء تشغيل فلاحة في OpenCode

# هذا السكريبت يشغل وكلاء فلاحة من سطر الأوامر

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Show-Menu {
    Clear-Host
    Write-Host "╔══════════════════════════════════════════╗"
    Write-Host "║        🌾 فْلاحة — الوكيل الفلاحي        ║"
    Write-Host "║          "من البذرة إلى السوق"            ║"
    Write-Host "╚══════════════════════════════════════════╝"
    Write-Host ""
    Write-Host "1. 🏪  وكيل السوق (Marketplace)"
    Write-Host "2. 🌱  وكيل الإرشاد الزراعي (Advisory)"
    Write-Host "3. 💰  وكيل التمويل والتأمين (Finance)"
    Write-Host "4. 📢  وكيل التسويق (Marketing)"
    Write-Host "5. 🚚  وكيل اللوجستيك (Logistics)"
    Write-Host "6. 📋  وكيل الدعم الحكومي (Gov Support)"
    Write-Host "7. 🌍  وكيل الجالية بالخارج (Diaspora)"
    Write-Host "8. 📚  عرض معلومات المشروع"
    Write-Host "Q. 🚪  خروج"
    Write-Host ""
}

function Show-ProjectInfo {
    Clear-Host
    Write-Host "🌾 فْلاحة — الوكيل الفلاحي الذكي للجزائر"
    Write-Host "══════════════════════════════════════════"
    Write-Host ""
    Write-Host "📂 هيكل المشروع:"
    Write-Host "  ├── agents/       - 7 وكلاء OpenCode"
    Write-Host "  ├── tools/        - 6 أدوات MCP"
    Write-Host "  ├── knowledge/    - 4 قواعد معرفة"
    Write-Host "  ├── integrations/ - 4 تكاملات خارجية"
    Write-Host "  ├── skills/       - تعريف Skill"
    Write-Host "  └── docs/         - وثائق المشروع"
    Write-Host ""
    Write-Host "👥 الجمهور المستهدف:"
    Write-Host "  - الفلاح الصغير (<10 هكتار): ~500,000"
    Write-Host "  - الفلاح المتوسط (10-50 هكتار): ~150,000"
    Write-Host "  - التاجر/المشتري: ~100,000"
    Write-Host "  - الجالية بالخارج: ~6,000,000"
    Write-Host ""
    Write-Host "📱 قنوات الوصول: واتساب | USSD | أندرويد | صوتي"
    Write-Host ""
    Write-Host "📍 مستوحى من: Twiga, DeHaat, Ninjacart, Farmer.Chat..."
    Write-Host ""
    Write-Host "إضغط أي مفتاح للعودة..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

do {
    Show-Menu
    $choice = Read-Host "اختر رقم الوحدة"
    
    switch ($choice) {
        "1" { opencode --agent flaha-marketplace }
        "2" { opencode --agent flaha-advisory }
        "3" { opencode --agent flaha-finance }
        "4" { opencode --agent flaha-marketing }
        "5" { opencode --agent flaha-logistics }
        "6" { opencode --agent flaha-gov-support }
        "7" { opencode --agent flaha-diaspora }
        "8" { Show-ProjectInfo }
        "Q" { Write-Host "السلام عليكم 👋"; break }
        "q" { Write-Host "السلام عليكم 👋"; break }
        default { Write-Host "❌ اختيار غير صحيح"; Start-Sleep -Seconds 1 }
    }
} while ($choice -ne "Q" -and $choice -ne "q")
