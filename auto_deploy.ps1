# Automatic Deployment Script
$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Automatic ERP Deployment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$SERVER = "147.79.102.91"
$USER = "root"
$PASSWORD = "l6TkO4puC+WTHYH(-s-"

# Step 1: Remove old SSH key
Write-Host "[1/5] Removing old SSH fingerprint..." -ForegroundColor Yellow
ssh-keygen -R $SERVER 2>$null
Write-Host "      Done!" -ForegroundColor Green
Write-Host ""

# Step 2: Install Posh-SSH if needed
Write-Host "[2/5] Checking Posh-SSH..." -ForegroundColor Yellow
if (-not (Get-Module -ListAvailable -Name Posh-SSH)) {
    Write-Host "      Installing Posh-SSH..." -ForegroundColor Cyan
    Install-Module -Name Posh-SSH -Force -Scope CurrentUser -AllowClobber -SkipPublisherCheck
}
Import-Module Posh-SSH
Write-Host "      Posh-SSH ready!" -ForegroundColor Green
Write-Host ""

# Step 3: Upload files
Write-Host "[3/5] Uploading files to server..." -ForegroundColor Yellow

$securePassword = ConvertTo-SecureString $PASSWORD -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential ($USER, $securePassword)

try {
    Write-Host "      Uploading erp_deploy.zip..." -ForegroundColor Cyan
    Set-SCPFile -ComputerName $SERVER -Credential $credential -LocalFile "C:\Users\DELL\DED\erp_deploy.zip" -RemotePath "/root/" -AcceptKey -NoProgress
    
    Write-Host "      Uploading deploy_erp_improved.sh..." -ForegroundColor Cyan
    Set-SCPFile -ComputerName $SERVER -Credential $credential -LocalFile "C:\Users\DELL\DED\deploy_erp_improved.sh" -RemotePath "/root/" -AcceptKey -NoProgress
    
    Write-Host "      Uploading .env.production..." -ForegroundColor Cyan
    Set-SCPFile -ComputerName $SERVER -Credential $credential -LocalFile "C:\Users\DELL\DED\.env.production" -RemotePath "/root/" -AcceptKey -NoProgress
    
    Write-Host "      All files uploaded!" -ForegroundColor Green
} catch {
    Write-Host "      Upload failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Prepare deployment
Write-Host "[4/5] Preparing deployment..." -ForegroundColor Yellow

try {
    $session = New-SSHSession -ComputerName $SERVER -Credential $credential -AcceptKey
    
    $prepareCmd = "cd /root && unzip -o erp_deploy.zip -d erp && cp /root/.env.production /root/erp/.env.production && chmod +x deploy_erp_improved.sh && echo READY"
    
    $result = Invoke-SSHCommand -SessionId $session.SessionId -Command $prepareCmd -TimeOut 120
    
    if ($result.Output -match "READY") {
        Write-Host "      Files prepared!" -ForegroundColor Green
    }
} catch {
    Write-Host "      Preparation failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 5: Execute deployment
Write-Host "[5/5] Executing deployment..." -ForegroundColor Yellow
Write-Host "      This will take 10-15 minutes..." -ForegroundColor Cyan
Write-Host ""

try {
    $deployCmd = "cd /root && ./deploy_erp_improved.sh"
    
    $deployResult = Invoke-SSHCommand -SessionId $session.SessionId -Command $deployCmd -TimeOut 1200
    
    Write-Host $deployResult.Output
    
    Remove-SSHSession -SessionId $session.SessionId | Out-Null
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  DEPLOYMENT COMPLETED!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your application:" -ForegroundColor Cyan
    Write-Host "  https://srv1392516.hstgr.cloud" -ForegroundColor White
    Write-Host ""
    Write-Host "Login:" -ForegroundColor Cyan
    Write-Host "  Username: admin" -ForegroundColor White
    Write-Host "  Password: admin123" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "      Deployment error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

