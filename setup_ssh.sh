#!/bin/bash

SERVER_IP="147.79.102.91"
USER="root"
PASSWORD="l6TkO4puC+WTHYH(-s-"

echo "===== STEP 1: Generate SSH Key If Not Exists ====="
if [ ! -f ~/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -C "production-deploy-key" -f ~/.ssh/id_ed25519 -N ""
    echo "SSH key generated!"
else
    echo "SSH key already exists!"
fi

echo ""
echo "===== STEP 2: Upload Public Key To Server ====="
echo "Note: You will be asked for password: $PASSWORD"

# Use sshpass if available, otherwise manual
if command -v sshpass &> /dev/null; then
    cat ~/.ssh/id_ed25519.pub | sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER_IP "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
else
    echo "Please enter password when prompted: $PASSWORD"
    cat ~/.ssh/id_ed25519.pub | ssh -o StrictHostKeyChecking=no $USER@$SERVER_IP "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
fi

echo ""
echo "===== STEP 3: Testing Connection ====="
ssh -o StrictHostKeyChecking=no $USER@$SERVER_IP "echo 'SECURE SSH CONNECTION SUCCESSFUL'"

if [ $? -eq 0 ]; then
    echo ""
    echo "===== STEP 4: Deploying Application ====="
    
    # Upload files
    echo "Uploading erp_deploy.zip..."
    scp -o StrictHostKeyChecking=no /mnt/c/Users/DELL/DED/erp_deploy.zip $USER@$SERVER_IP:/root/
    
    echo "Uploading deploy_erp_improved.sh..."
    scp -o StrictHostKeyChecking=no /mnt/c/Users/DELL/DED/deploy_erp_improved.sh $USER@$SERVER_IP:/root/
    
    echo "Uploading .env.production..."
    scp -o StrictHostKeyChecking=no /mnt/c/Users/DELL/DED/.env.production $USER@$SERVER_IP:/root/
    
    echo ""
    echo "Files uploaded successfully!"
    echo ""
    
    # Execute deployment
    echo "Executing deployment on server..."
    echo "This will take 10-15 minutes. Please wait..."
    echo ""
    
    ssh -o StrictHostKeyChecking=no $USER@$SERVER_IP << 'ENDSSH'
cd /root
echo "=== Files in /root ==="
ls -lh erp_deploy.zip deploy_erp_improved.sh .env.production
echo ""
echo "=== Extracting project ==="
unzip -o erp_deploy.zip -d erp
echo ""
echo "=== Copying environment file ==="
cp /root/.env.production /root/erp/.env.production
echo ""
echo "=== Making script executable ==="
chmod +x deploy_erp_improved.sh
echo ""
echo "=== Starting deployment ==="
./deploy_erp_improved.sh
ENDSSH
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "========================================"
        echo "DEPLOYMENT COMPLETED SUCCESSFULLY!"
        echo "========================================"
        echo ""
        echo "Your application is now live at:"
        echo "  https://srv1392516.hstgr.cloud"
        echo ""
        echo "Login credentials:"
        echo "  Username: admin"
        echo "  Password: admin123"
        echo ""
        echo "IMPORTANT: Change the admin password immediately!"
        echo ""
    else
        echo ""
        echo "Deployment failed. Check the output above."
    fi
else
    echo ""
    echo "SSH connection failed!"
fi

echo ""
echo "===== DONE ====="

