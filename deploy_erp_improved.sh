#!/bin/bash

# ==============================================
# سكريبت النشر المحسّن لنظام ERP
# Improved ERP Deployment Script
# ==============================================

set -e  # Exit on error

echo "=========================================="
echo "🚀 بدء نشر نظام ERP"
echo "🚀 Starting ERP Deployment"
echo "=========================================="

# ==============================================
# 1. إنشاء ملف الإعدادات
# ==============================================
cat > deploy_config.json <<EOL
{
  "SERVER_HOST": "srv1392516.hstgr.cloud",
  "SERVER_IP": "147.79.102.91",
  "SERVER_USER": "root",
  "PROJECT_LOCAL": "$(pwd)",
  "PROJECT_REMOTE": "/root/erp",
  "NGINX_SERVER_NAME": "srv1392516.hstgr.cloud",
  "EMAIL_FOR_SSL": "Modoluxeprojects@gmail.com",
  "GIT_REPO": "https://github.com/YourUsername/YourRepo.git",
  "GIT_BRANCH": "main",
  "DB_NAME": "erp_db",
  "DB_USER": "erp_user",
  "DB_PASSWORD": "$(openssl rand -base64 32)"
}
EOL

echo "✅ تم إنشاء ملف الإعدادات"

# ==============================================
# 2. قراءة الإعدادات
# ==============================================
CONFIG_FILE="deploy_config.json"
SERVER_HOST=$(jq -r '.SERVER_HOST' $CONFIG_FILE)
SERVER_IP=$(jq -r '.SERVER_IP' $CONFIG_FILE)
SERVER_USER=$(jq -r '.SERVER_USER' $CONFIG_FILE)
PROJECT_LOCAL=$(jq -r '.PROJECT_LOCAL' $CONFIG_FILE)
PROJECT_REMOTE=$(jq -r '.PROJECT_REMOTE' $CONFIG_FILE)
NGINX_NAME=$(jq -r '.NGINX_SERVER_NAME' $CONFIG_FILE)
EMAIL_SSL=$(jq -r '.EMAIL_FOR_SSL' $CONFIG_FILE)
GIT_REPO=$(jq -r '.GIT_REPO' $CONFIG_FILE)
GIT_BRANCH=$(jq -r '.GIT_BRANCH' $CONFIG_FILE)
DB_NAME=$(jq -r '.DB_NAME' $CONFIG_FILE)
DB_USER=$(jq -r '.DB_USER' $CONFIG_FILE)
DB_PASSWORD=$(jq -r '.DB_PASSWORD' $CONFIG_FILE)

echo "✅ تم قراءة الإعدادات"

# ==============================================
# 3. تحضير المشروع محلياً
# ==============================================
echo "📦 تحضير المشروع..."
cd $PROJECT_LOCAL

# Update from Git (optional - comment out if not using Git)
# git fetch origin $GIT_BRANCH
# git reset --hard origin/$GIT_BRANCH

# Create zip file
zip -r erp.zip . -x "*.git*" -x "*__pycache__*" -x "*.pyc" -x "flask_session/*" -x "*.db"

echo "✅ تم تحضير المشروع"

# ==============================================
# 4. رفع المشروع للسيرفر
# ==============================================
echo "📤 رفع المشروع للسيرفر..."
scp erp.zip $SERVER_USER@$SERVER_IP:/root/
scp .env.production.example $SERVER_USER@$SERVER_IP:/root/.env.production.example

echo "✅ تم رفع المشروع"

# ==============================================
# 5. تنفيذ الأوامر على السيرفر
# ==============================================
echo "⚙️ تنفيذ الإعدادات على السيرفر..."

ssh $SERVER_USER@$SERVER_IP "bash -s" <<ENDSSH
set -e

echo "=========================================="
echo "🔧 بدء الإعداد على السيرفر"
echo "=========================================="

# 1. تحديث النظام
echo "📦 تحديث النظام..."
apt update -y && apt upgrade -y

# 2. تثبيت المتطلبات الأساسية
echo "📦 تثبيت المتطلبات..."
apt install -y python3 python3-pip python3-venv nginx unzip jq certbot python3-certbot-nginx git postgresql postgresql-contrib

# 3. إعداد PostgreSQL
echo "🗄️ إعداد قاعدة البيانات PostgreSQL..."
sudo -u postgres psql <<EOF
-- Create database user
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Create database
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Connect to database and grant schema privileges
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
EOF

echo "✅ تم إعداد PostgreSQL"

# 4. فك ضغط المشروع
echo "📂 فك ضغط المشروع..."
rm -rf $PROJECT_REMOTE && mkdir -p $PROJECT_REMOTE
unzip /root/erp.zip -d $PROJECT_REMOTE
cd $PROJECT_REMOTE

# 5. إنشاء ملف .env.production
echo "📝 إنشاء ملف البيئة..."
cat > .env.production <<ENV
FLASK_ENV=production
FLASK_APP=run.py
SECRET_KEY=\$(openssl rand -base64 32)
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
WORKERS=3
DOMAIN_NAME=$NGINX_NAME
EMAIL_FOR_SSL=$EMAIL_SSL
ENV

echo "✅ تم إنشاء ملف البيئة"

# 6. إنشاء البيئة الافتراضية وتثبيت المتطلبات
echo "🐍 إنشاء البيئة الافتراضية..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ تم تثبيت المتطلبات"

# 7. إنشاء خدمة systemd للتطبيق
echo "⚙️ إنشاء خدمة systemd..."
cat > /etc/systemd/system/erp.service <<SERVICE
[Unit]
Description=ERP Flask Application
After=network.target postgresql.service
Wants=postgresql.service

[Service]
User=root
WorkingDirectory=$PROJECT_REMOTE
Environment="PATH=$PROJECT_REMOTE/venv/bin"
EnvironmentFile=$PROJECT_REMOTE/.env.production
ExecStart=$PROJECT_REMOTE/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 --timeout 120 wsgi:app
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable erp
systemctl start erp

echo "✅ تم إنشاء وتشغيل خدمة ERP"

ENDSSH

# 8. إعداد Nginx
echo "🌐 إعداد Nginx..."
cat > /etc/nginx/sites-available/erp <<NGINX
server {
    listen 80;
    server_name $NGINX_NAME;

    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    location /static {
        alias $PROJECT_REMOTE/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /uploads {
        alias $PROJECT_REMOTE/uploads;
        expires 30d;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/erp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo "✅ تم إعداد Nginx"

# 9. تفعيل HTTPS مع Let's Encrypt
echo "🔒 تفعيل HTTPS..."
certbot --nginx -d $NGINX_NAME --non-interactive --agree-tos -m $EMAIL_SSL --redirect

echo "✅ تم تفعيل HTTPS"

# 10. إنشاء مجلدات السجلات والنسخ الاحتياطي
echo "📁 إنشاء المجلدات..."
mkdir -p $PROJECT_REMOTE/logs
mkdir -p $PROJECT_REMOTE/backups
mkdir -p $PROJECT_REMOTE/uploads

echo "✅ تم إنشاء المجلدات"

# 11. إعداد Health Check
echo "🏥 إعداد Health Check..."
cat > /usr/local/bin/erp_health_check.sh <<HEALTH
#!/bin/bash
if ! systemctl is-active --quiet erp; then
  echo "\$(date): ERP service is down, restarting..." >> $PROJECT_REMOTE/logs/health_check.log
  systemctl restart erp
fi
HEALTH

chmod +x /usr/local/bin/erp_health_check.sh

# Add to crontab (every 5 minutes)
(crontab -l 2>/dev/null | grep -v erp_health_check; echo "*/5 * * * * /usr/local/bin/erp_health_check.sh") | crontab -

echo "✅ تم إعداد Health Check"

# 12. إعداد النسخ الاحتياطي التلقائي
echo "💾 إعداد النسخ الاحتياطي..."
cat > /usr/local/bin/erp_backup.sh <<BACKUP
#!/bin/bash
BACKUP_DIR=$PROJECT_REMOTE/backups
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE=\$BACKUP_DIR/backup_\$DATE.sql

# Backup database
pg_dump -U $DB_USER -h localhost $DB_NAME > \$BACKUP_FILE

# Compress backup
gzip \$BACKUP_FILE

# Delete backups older than 30 days
find \$BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "\$(date): Backup completed: \$BACKUP_FILE.gz" >> $PROJECT_REMOTE/logs/backup.log
BACKUP

chmod +x /usr/local/bin/erp_backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null | grep -v erp_backup; echo "0 2 * * * /usr/local/bin/erp_backup.sh") | crontab -

echo "✅ تم إعداد النسخ الاحتياطي"

# 13. عرض معلومات النشر
echo ""
echo "=========================================="
echo "✅ تم النشر بنجاح!"
echo "✅ Deployment Successful!"
echo "=========================================="
echo ""
echo "📊 معلومات النشر:"
echo "   🌐 URL: https://$NGINX_NAME"
echo "   🗄️ Database: $DB_NAME"
echo "   👤 DB User: $DB_USER"
echo "   📁 Project Path: $PROJECT_REMOTE"
echo ""
echo "🔧 الأوامر المفيدة:"
echo "   systemctl status erp       # حالة التطبيق"
echo "   systemctl restart erp      # إعادة تشغيل التطبيق"
echo "   systemctl status nginx     # حالة Nginx"
echo "   tail -f $PROJECT_REMOTE/logs/erp.log  # عرض السجلات"
echo ""
echo "👤 المستخدم الافتراضي:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   ⚠️ يرجى تغيير كلمة المرور بعد تسجيل الدخول!"
echo ""
echo "=========================================="

ENDSSH

echo "✅ تم تنفيذ الإعدادات على السيرفر"

# ==============================================
# 6. التنظيف المحلي
# ==============================================
echo "🧹 تنظيف الملفات المؤقتة..."
rm -f erp.zip

echo ""
echo "=========================================="
echo "🎉 اكتمل النشر بنجاح!"
echo "🎉 Deployment Completed Successfully!"
echo "=========================================="
echo ""
echo "🌐 يمكنك الآن زيارة: https://$NGINX_NAME"
echo ""

