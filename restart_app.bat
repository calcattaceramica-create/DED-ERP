@echo off
echo ========================================
echo   Restarting DED ERP System
echo   اعادة تشغيل نظام DED ERP
echo ========================================
echo.

REM Kill any running Python processes
taskkill /F /IM python.exe 2>nul

echo Waiting for processes to close...
timeout /t 2 /nobreak >nul

echo.
echo Starting application...
echo جاري تشغيل التطبيق...
echo.

start "" python run.py

echo.
echo ========================================
echo   Application is starting...
echo   التطبيق يعمل الآن...
echo ========================================
echo.
echo Open your browser and go to:
echo http://localhost:5000
echo.
pause

