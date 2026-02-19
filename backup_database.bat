@echo off
REM Database Backup Script
REM ======================

echo.
echo ========================================
echo   DED ERP Database Backup
echo ========================================
echo.

REM Set backup directory
set BACKUP_DIR=%~dp0backups
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Generate timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%

REM Set backup filename
set BACKUP_FILE=%BACKUP_DIR%\ded_erp_backup_%TIMESTAMP%.sql

echo [INFO] Backup directory: %BACKUP_DIR%
echo [INFO] Backup file: %BACKUP_FILE%
echo.

REM Database credentials (update these if needed)
set DB_USER=postgres
set DB_NAME=ded_erp
set DB_HOST=localhost
set DB_PORT=5432

echo [INFO] Database: %DB_NAME%
echo [INFO] User: %DB_USER%
echo [INFO] Host: %DB_HOST%
echo.

REM Check if pg_dump is available
where pg_dump >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pg_dump not found in PATH
    echo.
    echo Please add PostgreSQL bin directory to PATH
    echo Example: C:\Program Files\PostgreSQL\15\bin
    echo.
    echo Or run this command manually:
    echo pg_dump -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -f "%BACKUP_FILE%"
    echo.
    pause
    exit /b 1
)

echo [INFO] Creating backup...
echo.

REM Create backup
pg_dump -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -f "%BACKUP_FILE%"

if errorlevel 1 (
    echo.
    echo [ERROR] Backup failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Backup Complete!
echo ========================================
echo.
echo Backup saved to:
echo %BACKUP_FILE%
echo.

REM Get file size
for %%A in ("%BACKUP_FILE%") do set FILESIZE=%%~zA

echo File size: %FILESIZE% bytes
echo.

echo You can now run the migration script.
echo.

pause

