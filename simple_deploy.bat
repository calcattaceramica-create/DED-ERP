@echo off
echo ========================================
echo   ERP System Deployment
echo ========================================
echo.

set SERVER=147.79.102.91
set USER=root
set PASSWORD=l6TkO4puC+WTHYH(-s-

echo [1/4] Removing old SSH fingerprint...
ssh-keygen -R %SERVER% 2>nul
echo       Done!
echo.

echo [2/4] Uploading files to server...
echo       This will ask for password 3 times
echo       Password: %PASSWORD%
echo.

echo       Uploading erp_deploy.zip...
scp -o StrictHostKeyChecking=no C:\Users\DELL\DED\erp_deploy.zip %USER%@%SERVER%:/root/

echo       Uploading deploy_erp_improved.sh...
scp -o StrictHostKeyChecking=no C:\Users\DELL\DED\deploy_erp_improved.sh %USER%@%SERVER%:/root/

echo       Uploading .env.production...
scp -o StrictHostKeyChecking=no C:\Users\DELL\DED\.env.production %USER%@%SERVER%:/root/

echo.
echo       All files uploaded!
echo.

echo [3/4] Preparing deployment...
ssh -o StrictHostKeyChecking=no %USER%@%SERVER% "cd /root && unzip -o erp_deploy.zip -d erp && cp /root/.env.production /root/erp/.env.production && chmod +x deploy_erp_improved.sh && echo READY"

echo.
echo [4/4] Executing deployment (10-15 minutes)...
echo       Please wait...
echo.

ssh -o StrictHostKeyChecking=no %USER%@%SERVER% "cd /root && ./deploy_erp_improved.sh"

echo.
echo ========================================
echo   DEPLOYMENT COMPLETED!
echo ========================================
echo.
echo Your application is live at:
echo   https://srv1392516.hstgr.cloud
echo.
echo Login credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo IMPORTANT: Change admin password immediately!
echo.
pause

