@echo off
REM Multi-Tenant Migration Script Runner
REM =====================================

echo.
echo ========================================
echo   DED ERP Multi-Tenant Migration
echo ========================================
echo.

REM Change to project directory
cd /d "%~dp0"

echo [INFO] Current directory: %CD%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python first
    pause
    exit /b 1
)

echo [OK] Python is available
echo.

REM Check if migration script exists
if not exist "migrate_to_multitenant.py" (
    echo [ERROR] Migration script not found: migrate_to_multitenant.py
    pause
    exit /b 1
)

echo [OK] Migration script found
echo.

echo ========================================
echo   IMPORTANT WARNING
echo ========================================
echo.
echo This script will modify your database!
echo.
echo Before proceeding, make sure you have:
echo   1. Backed up your database
echo   2. Stopped the Flask server
echo   3. Closed all database connections
echo.
echo ========================================
echo.

set /p CONFIRM="Do you want to continue? (yes/no): "

if /i not "%CONFIRM%"=="yes" (
    echo.
    echo [CANCELLED] Migration cancelled by user
    pause
    exit /b 0
)

echo.
echo [INFO] Starting migration...
echo.

REM Run the migration script
python migrate_to_multitenant.py

if errorlevel 1 (
    echo.
    echo [ERROR] Migration failed!
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Migration Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Start the Flask server
echo   2. Test login functionality
echo   3. Verify data is visible
echo.

pause

