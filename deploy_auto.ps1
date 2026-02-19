# Automated Deployment Script
$password = "l6TkO4puC+WTHYH(-s-"
$server = "root@147.79.102.91"

Write-Host "Starting deployment..." -ForegroundColor Green

# Install Posh-SSH if not installed
if (-not (Get-Module -ListAvailable -Name Posh-SSH)) {
    Write-Host "Installing Posh-SSH module..." -ForegroundColor Yellow
    Install-Module -Name Posh-SSH -Force -Scope CurrentUser
}

Import-Module Posh-SSH

# Create credential
$securePassword = ConvertTo-SecureString $password -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential ("root", $securePassword)

try {
    # Upload files
    Write-Host "Uploading erp_deploy.zip..." -ForegroundColor Yellow
    Set-SCPFile -ComputerName "147.79.102.91" -Credential $credential -LocalFile "C:\Users\DELL\DED\erp_deploy.zip" -RemotePath "/root/" -AcceptKey
    
    Write-Host "Uploading deploy_erp_improved.sh..." -ForegroundColor Yellow
    Set-SCPFile -ComputerName "147.79.102.91" -Credential $credential -LocalFile "C:\Users\DELL\DED\deploy_erp_improved.sh" -RemotePath "/root/" -AcceptKey
    
    Write-Host "Uploading .env.production..." -ForegroundColor Yellow
    Set-SCPFile -ComputerName "147.79.102.91" -Credential $credential -LocalFile "C:\Users\DELL\DED\.env.production" -RemotePath "/root/" -AcceptKey
    
    Write-Host "Files uploaded successfully!" -ForegroundColor Green
    
    # Execute deployment
    Write-Host "Connecting to server and executing deployment..." -ForegroundColor Yellow
    
    $session = New-SSHSession -ComputerName "147.79.102.91" -Credential $credential -AcceptKey
    
    $commands = @"
cd /root
unzip -o erp_deploy.zip -d erp
cp /root/.env.production /root/erp/.env.production
chmod +x deploy_erp_improved.sh
./deploy_erp_improved.sh
"@
    
    $result = Invoke-SSHCommand -SessionId $session.SessionId -Command $commands -TimeOut 900
    
    Write-Host $result.Output
    
    Remove-SSHSession -SessionId $session.SessionId
    
    Write-Host "Deployment completed!" -ForegroundColor Green
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

# Clean up password file
if (Test-Path "C:\Users\DELL\DED\ssh_pass.txt") {
    Remove-Item "C:\Users\DELL\DED\ssh_pass.txt" -Force
}

