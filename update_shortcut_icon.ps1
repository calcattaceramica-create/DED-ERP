# تحديث أيقونة الاختصار على سطح المكتب

Write-Host "🔄 جاري تحديث أيقونة الاختصار..." -ForegroundColor Cyan

$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $DesktopPath "DED Application.lnk"

if (Test-Path $ShortcutPath) {
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    
    # محاولة استخدام الأيقونة الجديدة
    $newIconPath = "C:\Users\DELL\DED\assets\calcatta_logo.ico"
    $defaultIconPath = "C:\Users\DELL\DED\assets\app_icon.ico"
    
    if (Test-Path $newIconPath) {
        $Shortcut.IconLocation = $newIconPath
        Write-Host "✅ تم استخدام الأيقونة الجديدة: calcatta_logo.ico" -ForegroundColor Green
    }
    elseif (Test-Path $defaultIconPath) {
        $Shortcut.IconLocation = $defaultIconPath
        Write-Host "✅ تم استخدام الأيقونة الافتراضية: app_icon.ico" -ForegroundColor Yellow
    }
    else {
        Write-Host "⚠️ لم يتم العثور على ملف أيقونة" -ForegroundColor Yellow
    }
    
    $Shortcut.Save()
    Write-Host "✅ تم تحديث الاختصار بنجاح!" -ForegroundColor Green
    Write-Host "📍 الموقع: $ShortcutPath" -ForegroundColor Cyan
}
else {
    Write-Host "❌ الاختصار غير موجود على سطح المكتب" -ForegroundColor Red
    Write-Host "يرجى تشغيل: .\create_shortcut.ps1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📝 ملاحظة: لاستخدام شعار Calcatta الجديد:" -ForegroundColor Cyan
Write-Host "   1. احفظ الصورة باسم: calcatta_logo.png في مجلد assets" -ForegroundColor White
Write-Host "   2. قم بتحويلها إلى .ico باستخدام أداة تحويل أونلاين" -ForegroundColor White
Write-Host "   3. احفظ الملف .ico في: assets\calcatta_logo.ico" -ForegroundColor White
Write-Host "   4. شغل هذا السكريبت مرة أخرى" -ForegroundColor White

