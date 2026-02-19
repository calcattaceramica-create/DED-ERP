#!/bin/bash

# Flask ERP Deployment Script
set -e

echo "========================================="
echo "  Flask ERP System Deployment"
echo "========================================="
echo ""

# Configuration
DOMAIN="srv1392516.hstgr.cloud"
DB_NAME="erp_db"
DB_USER="erp_user"
DB_PASSWORD="ErpSecure2024!"

echo "[1/7] Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

echo ""
echo "[2/7] Installing required packages..."
apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    sqlite3 \
    nginx \
    git

echo ""
echo "[3/7] Setting up Python virtual environment..."
cd /root/DED
python3 -m venv venv
source venv/bin/activate

echo ""
echo "[4/7] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo ""
echo "[5/7] Setting up database..."
# Initialize database if needed
python3 << EOF
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("Database initialized!")
EOF

echo ""
echo "[6/7] Setting up Gunicorn service..."

# Create Gunicorn systemd service
cat > /etc/systemd/system/erp.service << 'EOF'
[Unit]
Description=ERP Flask Application
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/DED
Environment="PATH=/root/DED/venv/bin"
ExecStart=/root/DED/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 run:app

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "[7/7] Setting up Nginx..."

# Configure Nginx
cat > /etc/nginx/sites-available/erp << EOF
server {
    listen 80;
    server_name $DOMAIN 147.79.102.91;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /root/DED/app/static;
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
echo "To check status:"
echo "  systemctl status erp"
echo "  systemctl status nginx"
echo ""
echo "To view logs:"
echo "  journalctl -u erp -f"
echo ""

