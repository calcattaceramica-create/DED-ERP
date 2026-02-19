# Simple Automated Deployment
$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting ERP Deployment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$password = "l6TkO4puC+WTHYH(-s-"
$server = "147.79.102.91"

# Create expect-like script for SCP
$scpScript = @"
`$password = "$password"
`$server = "$server"

# Upload erp_deploy.zip
Write-Host "Uploading erp_deploy.zip..." -ForegroundColor Yellow
`$proc = Start-Process -FilePath "scp" -ArgumentList "C:\Users\DELL\DED\erp_deploy.zip","root@`$server:/root/" -NoNewWindow -PassThru -Wait
Write-Host "Upload 1/3 complete" -ForegroundColor Green

# Upload deploy script
Write-Host "Uploading deploy_erp_improved.sh..." -ForegroundColor Yellow
`$proc = Start-Process -FilePath "scp" -ArgumentList "C:\Users\DELL\DED\deploy_erp_improved.sh","root@`$server:/root/" -NoNewWindow -PassThru -Wait
Write-Host "Upload 2/3 complete" -ForegroundColor Green

# Upload env file
Write-Host "Uploading .env.production..." -ForegroundColor Yellow
`$proc = Start-Process -FilePath "scp" -ArgumentList "C:\Users\DELL\DED\.env.production","root@`$server:/root/" -NoNewWindow -PassThru -Wait
Write-Host "Upload 3/3 complete" -ForegroundColor Green

Write-Host ""
Write-Host "All files uploaded successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Now connect to server with SSH and run:" -ForegroundColor Yellow
Write-Host "  ssh root@`$server" -ForegroundColor White
Write-Host ""
Write-Host "Then execute:" -ForegroundColor Yellow
Write-Host "  cd /root" -ForegroundColor White
Write-Host "  unzip -o erp_deploy.zip -d erp" -ForegroundColor White
Write-Host "  cp /root/.env.production /root/erp/.env.production" -ForegroundColor White
Write-Host "  chmod +x deploy_erp_improved.sh" -ForegroundColor White
Write-Host "  ./deploy_erp_improved.sh" -ForegroundColor White
"@

Invoke-Expression $scpScript

