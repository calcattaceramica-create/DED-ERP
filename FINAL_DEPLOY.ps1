# Final Deployment Script - Complete Automation
$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ERP System Deployment to Production" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$SERVER = "147.79.102.91"
$USER = "root"
$PASSWORD = "l6TkO4puC+WTHYH(-s-"

# Step 1: Install Posh-SSH
Write-Host "[1/4] Checking Posh-SSH module..." -ForegroundColor Yellow

if (-not (Get-Module -ListAvailable -Name Posh-SSH)) {
    Write-Host "      Installing Posh-SSH..." -ForegroundColor Cyan
    try {
        Install-Module -Name Posh-SSH -Force -Scope CurrentUser -AllowClobber -ErrorAction Stop
        Write-Host "      Posh-SSH installed!" -ForegroundColor Green
    } catch {
        Write-Host "      Failed to install Posh-SSH: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install manually:" -ForegroundColor Yellow
        Write-Host "  Install-Module -Name Posh-SSH -Force -Scope CurrentUser" -ForegroundColor White
        exit 1
    }
} else {
    Write-Host "      Posh-SSH already installed!" -ForegroundColor Green
}

Import-Module Posh-SSH -ErrorAction SilentlyContinue

Write-Host ""

# Step 2: Upload files
Write-Host "[2/4] Uploading files to server..." -ForegroundColor Yellow

$securePassword = ConvertTo-SecureString $PASSWORD -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential ($USER, $securePassword)

try {
    Write-Host "      Uploading erp_deploy.zip..." -ForegroundColor Cyan
    Set-SCPFile -ComputerName $SERVER -Credential $credential -LocalFile "C:\Users\DELL\DED\erp_deploy.zip" -RemotePath "/root/" -AcceptKey -ErrorAction Stop
    Write-Host "      erp_deploy.zip uploaded!" -ForegroundColor Green
    
    Write-Host "      Uploading deploy_erp_improved.sh..." -ForegroundColor Cyan
    Set-SCPFile -ComputerName $SERVER -Credential $credential -LocalFile "C:\Users\DELL\DED\deploy_erp_improved.sh" -RemotePath "/root/" -AcceptKey -ErrorAction Stop
    Write-Host "      deploy_erp_improved.sh uploaded!" -ForegroundColor Green
    
    Write-Host "      Uploading .env.production..." -ForegroundColor Cyan
    Set-SCPFile -ComputerName $SERVER -Credential $credential -LocalFile "C:\Users\DELL\DED\.env.production" -RemotePath "/root/" -AcceptKey -ErrorAction Stop
    Write-Host "      .env.production uploaded!" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "      All files uploaded successfully!" -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "      Upload failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "  1. Internet connection" -ForegroundColor White
    Write-Host "  2. Server is accessible" -ForegroundColor White
    Write-Host "  3. Password is correct" -ForegroundColor White
    exit 1
}

Write-Host ""

# Step 3: Connect and prepare
Write-Host "[3/4] Preparing deployment on server..." -ForegroundColor Yellow

try {
    $session = New-SSHSession -ComputerName $SERVER -Credential $credential -AcceptKey -ErrorAction Stop
    Write-Host "      Connected to server!" -ForegroundColor Green
    
    # Prepare commands
    $prepareCommands = @"
cd /root
ls -lh erp_deploy.zip deploy_erp_improved.sh .env.production
unzip -o erp_deploy.zip -d erp
cp /root/.env.production /root/erp/.env.production
chmod +x deploy_erp_improved.sh
echo "READY"
"@
    
    Write-Host "      Extracting files..." -ForegroundColor Cyan
    $result = Invoke-SSHCommand -SessionId $session.SessionId -Command $prepareCommands -TimeOut 120
    
    if ($result.Output -match "READY") {
        Write-Host "      Files prepared successfully!" -ForegroundColor Green
    } else {
        Write-Host "      Preparation output:" -ForegroundColor Yellow
        Write-Host $result.Output
    }
    
} catch {
    Write-Host ""
    Write-Host "      Connection failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Execute deployment
Write-Host "[4/4] Executing deployment script..." -ForegroundColor Yellow
Write-Host "      This will take 10-15 minutes. Please wait..." -ForegroundColor Cyan
Write-Host ""

try {
    $deployCommand = "cd /root && ./deploy_erp_improved.sh"
    
    $deployResult = Invoke-SSHCommand -SessionId $session.SessionId -Command $deployCommand -TimeOut 1200
    
    Write-Host $deployResult.Output
    
    if ($deployResult.ExitStatus -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  DEPLOYMENT COMPLETED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your application is now live at:" -ForegroundColor Cyan
        Write-Host "  https://srv1392516.hstgr.cloud" -ForegroundColor White
        Write-Host ""
        Write-Host "Login credentials:" -ForegroundColor Cyan
        Write-Host "  Username: admin" -ForegroundColor White
        Write-Host "  Password: admin123" -ForegroundColor White
        Write-Host ""
        Write-Host "IMPORTANT SECURITY STEPS:" -ForegroundColor Yellow
        Write-Host "  1. Change admin password in the application" -ForegroundColor White
        Write-Host "  2. Change SSH root password in Hostinger Panel" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "Deployment completed with exit code: $($deployResult.ExitStatus)" -ForegroundColor Yellow
        Write-Host "Check the output above for any errors." -ForegroundColor Yellow
    }
    
    Remove-SSHSession -SessionId $session.SessionId | Out-Null
    
} catch {
    Write-Host ""
    Write-Host "Deployment error: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

