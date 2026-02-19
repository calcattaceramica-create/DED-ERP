# DED ERP - HTTPS Launcher
# اختصار فتح نظام DED ERP

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DED ERP - Opening System" -ForegroundColor Green
Write-Host "🚀 فتح نظام DED ERP" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔒 Opening HTTPS URL: https://localhost:5000" -ForegroundColor Yellow
Write-Host "🔒 فتح الرابط الآمن: https://localhost:5000" -ForegroundColor Yellow
Write-Host ""

# Open the URL in default browser
Start-Process "https://localhost:5000"

Write-Host "✅ Browser opened successfully!" -ForegroundColor Green
Write-Host "✅ تم فتح المتصفح بنجاح!" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Note: You may see a security warning for the self-signed certificate." -ForegroundColor Yellow
Write-Host "⚠️  ملاحظة: قد ترى تحذير أمان للشهادة ذاتية التوقيع." -ForegroundColor Yellow
Write-Host "    Click 'Advanced' → 'Proceed to localhost' to continue" -ForegroundColor Gray
Write-Host "    اضغط 'متقدم' ← 'المتابعة إلى localhost' للاستمرار" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Cyan
Write-Host "اضغط أي زر لإغلاق هذه النافذة..." -ForegroundColor Cyan

$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

