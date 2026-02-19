# Automated Deployment Script
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting ERP Deployment to Server" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$password = ConvertTo-SecureString "l6TkO4puC+WTHYH(-s-" -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential ("root", $password)

Write-Host "Step 1: Installing Posh-SSH module..." -ForegroundColor Yellow

# Check if Posh-SSH is installed
if (-not (Get-Module -ListAvailable -Name Posh-SSH)) {
    Write-Host "Installing Posh-SSH..." -ForegroundColor Yellow
    Install-Module -Name Posh-SSH -Force -Scope CurrentUser -AllowClobber
    Write-Host "Posh-SSH installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Posh-SSH already installed!" -ForegroundColor Green
}

Import-Module Posh-SSH

Write-Host ""
Write-Host "Step 2: Uploading files to server..." -ForegroundColor Yellow

try {
    # Upload erp_deploy.zip
    Write-Host "  Uploading erp_deploy.zip..." -ForegroundColor Cyan
    Set-SCPFile -ComputerName "147.79.102.91" -Credential $credential -LocalFile "C:\Users\DELL\DED\erp_deploy.zip" -RemotePath "/root/" -AcceptKey -ErrorAction Stop
    Write-Host "  ✅ erp_deploy.zip uploaded!" -ForegroundColor Green
    
    # Upload deploy_erp_improved.sh
    Write-Host "  Uploading deploy_erp_improved.sh..." -ForegroundColor Cyan
    Set-SCPFile -ComputerName "147.79.102.91" -Credential $credential -LocalFile "C:\Users\DELL\DED\deploy_erp_improved.sh" -RemotePath "/root/" -AcceptKey -ErrorAction Stop
    Write-Host "  ✅ deploy_erp_improved.sh uploaded!" -ForegroundColor Green
    
    # Upload .env.production
    Write-Host "  Uploading .env.production..." -ForegroundColor Cyan
    Set-SCPFile -ComputerName "147.79.102.91" -Credential $credential -LocalFile "C:\Users\DELL\DED\.env.production" -RemotePath "/root/" -AcceptKey -ErrorAction Stop
    Write-Host "  ✅ .env.production uploaded!" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "All files uploaded successfully!" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Step 3: Connecting to server and executing deployment..." -ForegroundColor Yellow
    
    # Create SSH session
    $session = New-SSHSession -ComputerName "147.79.102.91" -Credential $credential -AcceptKey -ErrorAction Stop
    Write-Host "  ✅ Connected to server!" -ForegroundColor Green
    
    # Execute deployment commands
    $commands = @"
cd /root
echo "📁 Current directory: `$(pwd)"
echo ""
echo "📋 Files in /root:"
ls -lh erp_deploy.zip deploy_erp_improved.sh .env.production
echo ""
echo "📦 Extracting project..."
unzip -o erp_deploy.zip -d erp
echo ""
echo "📄 Copying environment file..."
cp /root/.env.production /root/erp/.env.production
echo ""
echo "🔧 Making script executable..."
chmod +x deploy_erp_improved.sh
echo ""
echo "🚀 Starting deployment..."
./deploy_erp_improved.sh
"@
    
    Write-Host ""
    Write-Host "Executing deployment script on server..." -ForegroundColor Yellow
    Write-Host "This will take 10-15 minutes. Please wait..." -ForegroundColor Yellow
    Write-Host ""
    
    $result = Invoke-SSHCommand -SessionId $session.SessionId -Command $commands -TimeOut 1200
    
    Write-Host $result.Output
    
    if ($result.ExitStatus -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your application is now live at:" -ForegroundColor Cyan
        Write-Host "   https://srv1392516.hstgr.cloud" -ForegroundColor White
        Write-Host ""
        Write-Host "Login credentials:" -ForegroundColor Cyan
        Write-Host "   Username: admin" -ForegroundColor White
        Write-Host "   Password: admin123" -ForegroundColor White
        Write-Host ""
        Write-Host "IMPORTANT: Change the admin password immediately!" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ Deployment failed with exit code: $($result.ExitStatus)" -ForegroundColor Red
        Write-Host "Check the output above for errors." -ForegroundColor Yellow
    }
    
    # Close SSH session
    Remove-SSHSession -SessionId $session.SessionId | Out-Null
    
} catch {
    Write-Host ""
    Write-Host "❌ Error occurred: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check your internet connection" -ForegroundColor White
    Write-Host "2. Verify the server password is correct" -ForegroundColor White
    Write-Host "3. Make sure the server is accessible" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

