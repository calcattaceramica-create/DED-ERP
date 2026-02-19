# ==============================================
# سكريبت النشر من Windows إلى Linux Server
# Deploy from Windows to Linux Server
# ==============================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 بدء نشر نظام ERP من Windows" -ForegroundColor Green
Write-Host "🚀 Starting ERP Deployment from Windows" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ==============================================
# إعدادات السيرفر
# ==============================================
$SERVER_IP = "147.79.102.91"
$SERVER_USER = "root"
$PROJECT_LOCAL = "C:\Users\DELL\DED"
$PROJECT_REMOTE = "/root/erp"

Write-Host "📋 معلومات السيرفر:" -ForegroundColor Yellow
Write-Host "   Server IP: $SERVER_IP"
Write-Host "   Username: $SERVER_USER"
Write-Host "   Local Path: $PROJECT_LOCAL"
Write-Host "   Remote Path: $PROJECT_REMOTE"
Write-Host ""

# ==============================================
# التحقق من وجود SSH
# ==============================================
Write-Host "🔍 التحقق من وجود SSH..." -ForegroundColor Yellow

$sshExists = Get-Command ssh -ErrorAction SilentlyContinue
if (-not $sshExists) {
    Write-Host "❌ SSH غير موجود!" -ForegroundColor Red
    Write-Host ""
    Write-Host "يرجى تثبيت OpenSSH أو استخدام WinSCP + PuTTY" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "لتثبيت OpenSSH على Windows 10/11:" -ForegroundColor Cyan
    Write-Host "1. Settings → Apps → Optional Features" -ForegroundColor White
    Write-Host "2. Add a feature → OpenSSH Client" -ForegroundColor White
    Write-Host ""
    Write-Host "أو استخدم الطريقة اليدوية:" -ForegroundColor Cyan
    Write-Host "1. حمّل WinSCP: https://winscp.net/" -ForegroundColor White
    Write-Host "2. حمّل PuTTY: https://www.putty.org/" -ForegroundColor White
    Write-Host "3. راجع ملف: DEPLOY_FROM_WINDOWS.md" -ForegroundColor White
    Write-Host ""
    pause
    exit 1
}

Write-Host "✅ SSH موجود!" -ForegroundColor Green
Write-Host ""

# ==============================================
# ضغط المشروع
# ==============================================
Write-Host "📦 ضغط المشروع..." -ForegroundColor Yellow

$zipFile = "$PROJECT_LOCAL\erp_deploy.zip"

# حذف الملف المضغوط القديم إن وجد
if (Test-Path $zipFile) {
    Remove-Item $zipFile -Force
}

# ضغط المشروع (استثناء الملفات غير الضرورية)
$excludeItems = @(
    "*.pyc",
    "__pycache__",
    "*.db",
    "flask_session",
    "backups",
    "logs",
    ".git",
    "venv",
    "env",
    "node_modules"
)

Write-Host "   جاري الضغط..." -ForegroundColor Gray

# استخدام 7-Zip إذا كان موجوداً، وإلا استخدم Compress-Archive
$7zipPath = "C:\Program Files\7-Zip\7z.exe"
if (Test-Path $7zipPath) {
    & $7zipPath a -tzip $zipFile "$PROJECT_LOCAL\*" -xr!__pycache__ -xr!*.pyc -xr!*.db -xr!flask_session -xr!backups -xr!logs -xr!.git -xr!venv -xr!env | Out-Null
} else {
    # استخدام PowerShell المدمج
    Get-ChildItem -Path $PROJECT_LOCAL -Recurse | 
        Where-Object { 
            $_.FullName -notmatch '(__pycache__|\.pyc$|\.db$|flask_session|backups|logs|\.git|venv|env)' 
        } | 
        Compress-Archive -DestinationPath $zipFile -Force
}

if (Test-Path $zipFile) {
    $fileSize = (Get-Item $zipFile).Length / 1MB
    Write-Host "✅ تم الضغط بنجاح! ($([math]::Round($fileSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "❌ فشل الضغط!" -ForegroundColor Red
    pause
    exit 1
}
Write-Host ""

# ==============================================
# رفع الملف للسيرفر
# ==============================================
Write-Host "📤 رفع الملف للسيرفر..." -ForegroundColor Yellow
Write-Host "   (قد يستغرق بضع دقائق حسب سرعة الإنترنت)" -ForegroundColor Gray
Write-Host ""

scp $zipFile "${SERVER_USER}@${SERVER_IP}:/root/erp_deploy.zip"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ فشل رفع الملف!" -ForegroundColor Red
    Write-Host ""
    Write-Host "تأكد من:" -ForegroundColor Yellow
    Write-Host "1. أن لديك وصول SSH للسيرفر" -ForegroundColor White
    Write-Host "2. أن IP السيرفر صحيح: $SERVER_IP" -ForegroundColor White
    Write-Host "3. أن اسم المستخدم صحيح: $SERVER_USER" -ForegroundColor White
    Write-Host ""
    pause
    exit 1
}

Write-Host "✅ تم رفع الملف بنجاح!" -ForegroundColor Green
Write-Host ""

# ==============================================
# تنفيذ السكريبت على السيرفر
# ==============================================
Write-Host "🚀 تنفيذ سكريبت النشر على السيرفر..." -ForegroundColor Yellow
Write-Host ""

$deployScript = @"
#!/bin/bash
set -e

echo '=========================================='
echo '🚀 بدء النشر على السيرفر'
echo '=========================================='
echo ''

# فك الضغط
echo '📦 فك ضغط المشروع...'
cd /root
rm -rf erp_temp
mkdir -p erp_temp
unzip -q erp_deploy.zip -d erp_temp
echo '✅ تم فك الضغط'
echo ''

# نقل الملفات
echo '📁 نقل الملفات...'
rm -rf $PROJECT_REMOTE
mv erp_temp $PROJECT_REMOTE
echo '✅ تم نقل الملفات'
echo ''

# جعل السكريبت قابل للتنفيذ
echo '🔧 إعداد السكريبت...'
cd /root
chmod +x deploy_erp_improved.sh
echo '✅ السكريبت جاهز'
echo ''

# تشغيل السكريبت
echo '🚀 تشغيل سكريبت النشر...'
echo ''
./deploy_erp_improved.sh
"@

# حفظ السكريبت في ملف مؤقت
$tempScript = "$env:TEMP\deploy_temp.sh"
$deployScript | Out-File -FilePath $tempScript -Encoding UTF8 -NoNewline

# رفع السكريبت وتنفيذه
scp $tempScript "${SERVER_USER}@${SERVER_IP}:/root/deploy_temp.sh"
ssh "${SERVER_USER}@${SERVER_IP}" "chmod +x /root/deploy_temp.sh && /root/deploy_temp.sh"

# حذف الملف المؤقت
Remove-Item $tempScript -Force

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ اكتمل النشر بنجاح!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 زيارة الموقع:" -ForegroundColor Yellow
Write-Host "   https://srv1392516.hstgr.cloud" -ForegroundColor White
Write-Host ""
Write-Host "🔑 تسجيل الدخول:" -ForegroundColor Yellow
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  لا تنسى تغيير كلمة المرور فوراً!" -ForegroundColor Red
Write-Host ""

pause

