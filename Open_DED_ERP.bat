@echo off
chcp 65001 >nul
title DED ERP - HTTPS Launcher

echo ========================================
echo 🚀 DED ERP - Opening System
echo 🚀 فتح نظام DED ERP
echo ========================================
echo.
echo 🔒 Opening HTTPS URL: https://localhost:5000
echo 🔒 فتح الرابط الآمن: https://localhost:5000
echo.

start https://localhost:5000

echo ✅ Browser opened successfully!
echo ✅ تم فتح المتصفح بنجاح!
echo.
echo ⚠️  Note: You may see a security warning for the self-signed certificate.
echo ⚠️  ملاحظة: قد ترى تحذير أمان للشهادة ذاتية التوقيع.
echo     Click 'Advanced' - 'Proceed to localhost' to continue
echo     اضغط 'متقدم' - 'المتابعة إلى localhost' للاستمرار
echo.

timeout /t 5 /nobreak >nul
exit

