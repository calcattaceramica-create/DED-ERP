# ERP Deployment Script for Windows
# Simple version without Arabic text

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting ERP Deployment from Windows" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Server Configuration
$SERVER_IP = "147.79.102.91"
$SERVER_USER = "root"
$PROJECT_LOCAL = "C:\Users\DELL\DED"
$PROJECT_REMOTE = "/root/erp"

Write-Host "Server Information:" -ForegroundColor Yellow
Write-Host "  Server IP: $SERVER_IP"
Write-Host "  Username: $SERVER_USER"
Write-Host "  Local Path: $PROJECT_LOCAL"
Write-Host "  Remote Path: $PROJECT_REMOTE"
Write-Host ""

# Check SSH
Write-Host "Checking SSH..." -ForegroundColor Yellow
$sshExists = Get-Command ssh -ErrorAction SilentlyContinue
if (-not $sshExists) {
    Write-Host "ERROR: SSH not found!" -ForegroundColor Red
    Write-Host "Please install OpenSSH or use WinSCP + PuTTY" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host "SSH found!" -ForegroundColor Green
Write-Host ""

# Compress Project
Write-Host "Compressing project..." -ForegroundColor Yellow
$zipFile = "$PROJECT_LOCAL\erp_deploy.zip"

if (Test-Path $zipFile) {
    Remove-Item $zipFile -Force
}

# Create zip excluding unnecessary files
$excludePatterns = @('__pycache__', '*.pyc', '*.db', 'flask_session', 'backups', 'logs', '.git', 'venv', 'env')

Write-Host "  Creating archive..." -ForegroundColor Gray

# Get all files except excluded ones
$filesToZip = Get-ChildItem -Path $PROJECT_LOCAL -Recurse -File | Where-Object {
    $file = $_
    $shouldExclude = $false
    foreach ($pattern in $excludePatterns) {
        if ($file.FullName -like "*$pattern*") {
            $shouldExclude = $true
            break
        }
    }
    -not $shouldExclude
}

# Create zip
Compress-Archive -Path $filesToZip.FullName -DestinationPath $zipFile -Force -ErrorAction SilentlyContinue

if (Test-Path $zipFile) {
    $fileSize = (Get-Item $zipFile).Length / 1MB
    $fileSizeRounded = [math]::Round($fileSize, 2)
    Write-Host "Compressed successfully! Size: $fileSizeRounded MB" -ForegroundColor Green
} else {
    Write-Host "Compression failed!" -ForegroundColor Red
    pause
    exit 1
}
Write-Host ""

# Upload to Server
Write-Host "Uploading to server..." -ForegroundColor Yellow
Write-Host "  (This may take a few minutes)" -ForegroundColor Gray
Write-Host ""

$scpCommand = "scp `"$zipFile`" ${SERVER_USER}@${SERVER_IP}:/root/erp_deploy.zip"
Invoke-Expression $scpCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host "Upload failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "1. SSH access to server" -ForegroundColor White
    Write-Host "2. Server IP is correct: $SERVER_IP" -ForegroundColor White
    Write-Host "3. Username is correct: $SERVER_USER" -ForegroundColor White
    Write-Host ""
    pause
    exit 1
}

Write-Host "Upload successful!" -ForegroundColor Green
Write-Host ""

# Upload deployment script
Write-Host "Uploading deployment script..." -ForegroundColor Yellow
$scpScript = "scp `"$PROJECT_LOCAL\deploy_erp_improved.sh`" ${SERVER_USER}@${SERVER_IP}:/root/"
Invoke-Expression $scpScript

Write-Host "Deployment script uploaded!" -ForegroundColor Green
Write-Host ""

# Execute deployment on server
Write-Host "Executing deployment on server..." -ForegroundColor Yellow
Write-Host ""

$sshCommands = @"
cd /root && \
unzip -o erp_deploy.zip -d erp && \
chmod +x deploy_erp_improved.sh && \
./deploy_erp_improved.sh
"@

$sshCommand = "ssh ${SERVER_USER}@${SERVER_IP} `"$sshCommands`""
Invoke-Expression $sshCommand

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Visit: https://srv1392516.hstgr.cloud" -ForegroundColor Yellow
Write-Host ""
Write-Host "Login:" -ForegroundColor Yellow
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT: Change password immediately!" -ForegroundColor Red
Write-Host ""

pause

