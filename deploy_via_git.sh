#!/bin/bash

# Deployment Script via Git
# This script will be run on the server after pulling from Git

set -e

echo "========================================="
echo "  ERP System Deployment via Git"
echo "========================================="
echo ""

# Configuration
DOMAIN="srv1392516.hstgr.cloud"
DB_NAME="erp_db"
DB_USER="erp_user"
DB_PASSWORD="ErpSecure2024!"
SECRET_KEY="django-insecure-$(openssl rand -base64 32)"

echo "[1/8] Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

echo ""
echo "[2/8] Installing required packages..."
apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    nginx \
    certbot \
    python3-certbot-nginx \
    git

echo ""
echo "[3/8] Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo ""
echo "[4/8] Creating .env file..."
cat > /root/DED/.env << EOF
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$DOMAIN,147.79.102.91,localhost,127.0.0.1

DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASSWORD
DATABASE_HOST=localhost
DATABASE_PORT=5432

STATIC_URL=/static/
STATIC_ROOT=/root/DED/staticfiles/
MEDIA_URL=/media/
MEDIA_ROOT=/root/DED/media/
EOF

echo ""
echo "[5/8] Setting up Python virtual environment..."
cd /root/DED
python3 -m venv venv
source venv/bin/activate

echo ""
echo "[6/8] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "[7/8] Running Django migrations and collecting static files..."
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell

echo ""
echo "[8/8] Setting up Gunicorn and Nginx..."

# Create Gunicorn systemd service
cat > /etc/systemd/system/erp.service << EOF
[Unit]
Description=ERP Gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/DED
Environment="PATH=/root/DED/venv/bin"
ExecStart=/root/DED/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 core.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
cat > /etc/nginx/sites-available/erp << EOF
server {
    listen 80;
    server_name $DOMAIN 147.79.102.91;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /root/DED/staticfiles/;
    }
    
    location /media/ {
        alias /root/DED/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/erp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart services
nginx -t
systemctl restart nginx
systemctl enable nginx

systemctl daemon-reload
systemctl start erp
systemctl enable erp

echo ""
echo "========================================="
echo "  DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "========================================="
echo ""
echo "Your application is now live at:"
echo "  http://$DOMAIN"
echo "  http://147.79.102.91"
echo ""
echo "Login credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "IMPORTANT: Change the admin password immediately!"
echo ""
echo "To enable HTTPS, run:"
echo "  certbot --nginx -d $DOMAIN"
echo ""

