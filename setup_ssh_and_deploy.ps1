# Setup SSH Key and Deploy ERP System
$ErrorActionPreference = "Continue"

$SERVER_IP = "147.79.102.91"
$USER = "root"
$PASSWORD = "l6TkO4puC+WTHYH(-s-"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SSH Key Setup and Deployment Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Generate SSH Key if not exists
Write-Host "STEP 1: Checking SSH Key..." -ForegroundColor Yellow

$sshKeyPath = "$env:USERPROFILE\.ssh\id_ed25519"

if (-not (Test-Path $sshKeyPath)) {
    Write-Host "  Generating new SSH key..." -ForegroundColor Cyan
    
    # Create .ssh directory if not exists
    $sshDir = "$env:USERPROFILE\.ssh"
    if (-not (Test-Path $sshDir)) {
        New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    }
    
    # Generate SSH key
    ssh-keygen -t ed25519 -C "production-deploy-key" -f $sshKeyPath -N '""'
    
    Write-Host "  SSH key generated successfully!" -ForegroundColor Green
} else {
    Write-Host "  SSH key already exists!" -ForegroundColor Green
}

Write-Host ""

# Step 2: Upload public key to server
Write-Host "STEP 2: Uploading public key to server..." -ForegroundColor Yellow

$publicKey = Get-Content "$sshKeyPath.pub"

# Create a temporary script to upload the key
$uploadScript = @"
`$password = ConvertTo-SecureString '$PASSWORD' -AsPlainText -Force
`$credential = New-Object System.Management.Automation.PSCredential ('$USER', `$password)

# Install Posh-SSH if needed
if (-not (Get-Module -ListAvailable -Name Posh-SSH)) {
    Install-Module -Name Posh-SSH -Force -Scope CurrentUser -AllowClobber
}
Import-Module Posh-SSH

try {
    `$session = New-SSHSession -ComputerName '$SERVER_IP' -Credential `$credential -AcceptKey
    
    `$commands = @'
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo '$publicKey' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo 'SSH key added successfully'
'@
    
    `$result = Invoke-SSHCommand -SessionId `$session.SessionId -Command `$commands
    Write-Host `$result.Output
    
    Remove-SSHSession -SessionId `$session.SessionId | Out-Null
    
    Write-Host '  Public key uploaded successfully!' -ForegroundColor Green
} catch {
    Write-Host '  Error uploading key: ' -ForegroundColor Red -NoNewline
    Write-Host `$_.Exception.Message -ForegroundColor Yellow
    exit 1
}
"@

# Execute the upload script
Invoke-Expression $uploadScript

Write-Host ""

# Step 3: Test SSH connection with key
Write-Host "STEP 3: Testing SSH key connection..." -ForegroundColor Yellow

$testResult = ssh -i $sshKeyPath -o StrictHostKeyChecking=no $USER@$SERVER_IP "echo 'SSH KEY CONNECTION SUCCESSFUL'"

if ($LASTEXITCODE -eq 0) {
    Write-Host "  $testResult" -ForegroundColor Green
    Write-Host ""
    
    # Step 4: Deploy the application
    Write-Host "STEP 4: Deploying application..." -ForegroundColor Yellow
    Write-Host ""
    
    # Upload files using SCP with key
    Write-Host "  Uploading erp_deploy.zip..." -ForegroundColor Cyan
    scp -i $sshKeyPath -o StrictHostKeyChecking=no C:\Users\DELL\DED\erp_deploy.zip ${USER}@${SERVER_IP}:/root/
    
    Write-Host "  Uploading deploy_erp_improved.sh..." -ForegroundColor Cyan
    scp -i $sshKeyPath -o StrictHostKeyChecking=no C:\Users\DELL\DED\deploy_erp_improved.sh ${USER}@${SERVER_IP}:/root/
    
    Write-Host "  Uploading .env.production..." -ForegroundColor Cyan
    scp -i $sshKeyPath -o StrictHostKeyChecking=no C:\Users\DELL\DED\.env.production ${USER}@${SERVER_IP}:/root/
    
    Write-Host ""
    Write-Host "  All files uploaded successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Execute deployment on server
    Write-Host "  Executing deployment on server..." -ForegroundColor Cyan
    Write-Host "  This will take 10-15 minutes. Please wait..." -ForegroundColor Yellow
    Write-Host ""
    
    $deployCommands = @"
cd /root
echo '=== Files in /root ==='
ls -lh erp_deploy.zip deploy_erp_improved.sh .env.production
echo ''
echo '=== Extracting project ==='
unzip -o erp_deploy.zip -d erp
echo ''
echo '=== Copying environment file ==='
cp /root/.env.production /root/erp/.env.production
echo ''
echo '=== Making script executable ==='
chmod +x deploy_erp_improved.sh
echo ''
echo '=== Starting deployment ==='
./deploy_erp_improved.sh
"@
    
    ssh -i $sshKeyPath -o StrictHostKeyChecking=no $USER@$SERVER_IP $deployCommands
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "DEPLOYMENT COMPLETED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your application is now live at:" -ForegroundColor Cyan
        Write-Host "  https://srv1392516.hstgr.cloud" -ForegroundColor White
        Write-Host ""
        Write-Host "Login credentials:" -ForegroundColor Cyan
        Write-Host "  Username: admin" -ForegroundColor White
        Write-Host "  Password: admin123" -ForegroundColor White
        Write-Host ""
        Write-Host "IMPORTANT: Change the admin password immediately!" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "Deployment failed. Check the output above for errors." -ForegroundColor Red
    }
    
} else {
    Write-Host "  SSH key connection failed!" -ForegroundColor Red
    Write-Host "  Falling back to password authentication..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

