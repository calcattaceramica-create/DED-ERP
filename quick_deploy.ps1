# Quick Deployment Script
$SERVER = "147.79.102.91"
$USER = "root"
$PASSWORD = "l6TkO4puC+WTHYH(-s-"

Write-Host "Starting deployment..." -ForegroundColor Green

# Remove old SSH key
ssh-keygen -R $SERVER 2>$null

# Create credential
$securePassword = ConvertTo-SecureString $PASSWORD -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential ($USER, $securePassword)

# Install Posh-SSH if needed
if (-not (Get-Module -ListAvailable -Name Posh-SSH)) {
    Write-Host "Installing Posh-SSH (this may take 2-3 minutes)..." -ForegroundColor Yellow
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -Scope CurrentUser | Out-Null
    Install-Module -Name Posh-SSH -Force -Scope CurrentUser -AllowClobber -SkipPublisherCheck -Confirm:$false
    Write-Host "Posh-SSH installed!" -ForegroundColor Green
}

Import-Module Posh-SSH -Force -ErrorAction Stop
Write-Host "Posh-SSH loaded successfully!" -ForegroundColor Green

Write-Host "Uploading files..." -ForegroundColor Cyan

# Upload files
Set-SCPFile -ComputerName $SERVER -Credential $credential -LocalFile "C:\Users\DELL\DED\erp_deploy.zip" -RemotePath "/root/" -AcceptKey -NoProgress
Set-SCPFile -ComputerName $SERVER -Credential $credential -LocalFile "C:\Users\DELL\DED\deploy_erp_improved.sh" -RemotePath "/root/" -AcceptKey -NoProgress
Set-SCPFile -ComputerName $SERVER -Credential $credential -LocalFile "C:\Users\DELL\DED\.env.production" -RemotePath "/root/" -AcceptKey -NoProgress

Write-Host "Files uploaded!" -ForegroundColor Green

# Connect and deploy
$session = New-SSHSession -ComputerName $SERVER -Credential $credential -AcceptKey

Write-Host "Preparing deployment..." -ForegroundColor Cyan
Invoke-SSHCommand -SessionId $session.SessionId -Command "cd /root && unzip -o erp_deploy.zip -d erp && cp /root/.env.production /root/erp/.env.production && chmod +x deploy_erp_improved.sh" -TimeOut 120 | Out-Null

Write-Host "Starting deployment (10-15 minutes)..." -ForegroundColor Yellow
$result = Invoke-SSHCommand -SessionId $session.SessionId -Command "cd /root && ./deploy_erp_improved.sh" -TimeOut 1200

Write-Host $result.Output

Remove-SSHSession -SessionId $session.SessionId | Out-Null

Write-Host ""
Write-Host "DEPLOYMENT COMPLETED!" -ForegroundColor Green
Write-Host "Visit: https://srv1392516.hstgr.cloud" -ForegroundColor Cyan
Write-Host "Login: admin / admin123" -ForegroundColor White

