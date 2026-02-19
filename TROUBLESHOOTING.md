# 🔧 حل المشاكل الشائعة

---

## ❓ **الأسئلة الشائعة:**

---

### **س1: لا أجد File Manager في Hostinger؟**

**الحل:**
1. تأكد من أنك في قسم **VPS** (وليس Hosting)
2. ابحث عن **Files** بدلاً من File Manager
3. أو ابحث عن **FTP** واستخدمه
4. أو استخدم **SFTP** مع FileZilla

---

### **س2: لا أجد Browser Terminal؟**

**الحل:**
1. ابحث عن **SSH** في القائمة
2. أو ابحث عن **Console**
3. أو ابحث عن **Terminal** في قسم Overview
4. أو استخدم PuTTY من جهازك

---

### **س3: الملف .env.production لا يظهر عند الرفع؟**

**الحل:**
1. الملفات التي تبدأ بنقطة (.) مخفية
2. في File Manager، فعّل **Show hidden files**
3. أو أعد تسمية الملف مؤقتاً إلى `env.production` (بدون نقطة)
4. بعد الرفع، أعد تسميته في Terminal:
```bash
mv /root/env.production /root/.env.production
```

---

### **س4: ظهر خطأ "unzip: command not found"؟**

**الحل:**
```bash
# ثبّت unzip أولاً
apt update
apt install -y unzip

# ثم أعد المحاولة
unzip -o erp_deploy.zip -d erp
```

---

### **س5: ظهر خطأ "Permission denied"؟**

**الحل:**
```bash
# تأكد من أنك في مجلد root
cd /root

# أعط صلاحيات التنفيذ
chmod +x deploy_erp_improved.sh

# أعد المحاولة
./deploy_erp_improved.sh
```

---

### **س6: السكريبت توقف أثناء التنفيذ؟**

**الحل:**
```bash
# تحقق من السجلات
tail -f /var/log/syslog

# أو تحقق من حالة الخدمات
systemctl status erp
systemctl status nginx
systemctl status postgresql

# إذا كانت إحداها failed، أعد تشغيلها
systemctl restart erp
```

---

### **س7: الموقع لا يفتح بعد النشر؟**

**الحل:**

**1. تحقق من حالة الخدمات:**
```bash
systemctl status erp
systemctl status nginx
```

**2. تحقق من المنافذ:**
```bash
netstat -tulpn | grep LISTEN
```

**يجب أن ترى:**
```
tcp  0.0.0.0:80    LISTEN  nginx
tcp  0.0.0.0:443   LISTEN  nginx
tcp  127.0.0.1:8000 LISTEN  gunicorn
```

**3. تحقق من السجلات:**
```bash
journalctl -u erp -n 50
tail -f /var/log/nginx/error.log
```

**4. أعد تشغيل الخدمات:**
```bash
systemctl restart erp
systemctl restart nginx
```

---

### **س8: ظهر خطأ "Database connection failed"؟**

**الحل:**

**1. تحقق من PostgreSQL:**
```bash
systemctl status postgresql
```

**2. تحقق من قاعدة البيانات:**
```bash
sudo -u postgres psql -l
```

**يجب أن ترى `erp_db` في القائمة**

**3. تحقق من ملف .env.production:**
```bash
cat /root/erp/.env.production | grep DATABASE_URL
```

**4. إذا لم تكن موجودة، أنشئها يدوياً:**
```bash
sudo -u postgres psql
CREATE DATABASE erp_db;
CREATE USER erp_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE erp_db TO erp_user;
\q
```

---

### **س9: SSL لا يعمل (HTTPS)؟**

**الحل:**

**1. تحقق من الشهادة:**
```bash
certbot certificates
```

**2. إذا لم تكن موجودة، أنشئها:**
```bash
certbot --nginx -d srv1392516.hstgr.cloud --non-interactive --agree-tos -m your@email.com
```

**3. أعد تحميل Nginx:**
```bash
systemctl reload nginx
```

**4. إذا فشل Certbot:**
- تأكد من أن Domain يشير للسيرفر
- تأكد من أن المنفذ 80 و 443 مفتوحان
- استخدم IP بدلاً من Domain (HTTP فقط)

---

### **س10: كيف أعرف أن النشر نجح؟**

**الحل:**

**1. تحقق من الخدمات:**
```bash
systemctl is-active erp nginx postgresql
```

**يجب أن تكون جميعها:** `active`

**2. تحقق من الموقع:**
```bash
curl -I http://localhost
```

**يجب أن ترى:** `HTTP/1.1 200 OK`

**3. افتح المتصفح:**
```
https://srv1392516.hstgr.cloud
```

**يجب أن ترى صفحة تسجيل الدخول**

---

## 🆘 **مشاكل شائعة أخرى:**

---

### **المشكلة: "502 Bad Gateway"**

**السبب:** التطبيق لا يعمل

**الحل:**
```bash
# تحقق من حالة التطبيق
systemctl status erp

# عرض السجلات
journalctl -u erp -n 100

# إعادة تشغيل
systemctl restart erp
```

---

### **المشكلة: "504 Gateway Timeout"**

**السبب:** التطبيق بطيء جداً

**الحل:**
```bash
# زيادة timeout في Nginx
nano /etc/nginx/sites-available/erp

# أضف هذه الأسطر في قسم location:
proxy_read_timeout 300;
proxy_connect_timeout 300;
proxy_send_timeout 300;

# احفظ وأعد تحميل
systemctl reload nginx
```

---

### **المشكلة: "Connection refused"**

**السبب:** Gunicorn لا يعمل

**الحل:**
```bash
# تحقق من Gunicorn
ps aux | grep gunicorn

# إذا لم يكن يعمل، أعد تشغيل الخدمة
systemctl restart erp

# تحقق من السجلات
journalctl -u erp -f
```

---

### **المشكلة: "Static files not loading"**

**السبب:** ملفات CSS/JS لا تُحمّل

**الحل:**
```bash
# جمع الملفات الثابتة
cd /root/erp
source venv/bin/activate
python -c "from app import create_app; app = create_app(); app.config['STATIC_FOLDER']"

# تحقق من إعدادات Nginx
nano /etc/nginx/sites-available/erp

# تأكد من وجود:
location /static/ {
    alias /root/erp/app/static/;
}
```

---

## 📞 **الحصول على مساعدة:**

**إذا لم تحل المشكلة:**

1. **اجمع المعلومات:**
```bash
# حالة الخدمات
systemctl status erp nginx postgresql > /root/status.txt

# السجلات
journalctl -u erp -n 200 > /root/logs.txt

# معلومات النظام
df -h > /root/disk.txt
free -h >> /root/disk.txt
```

2. **أرسل الملفات:**
- `/root/status.txt`
- `/root/logs.txt`
- `/root/disk.txt`

---

## ✅ **نصائح للوقاية:**

1. **راقب المساحة:**
```bash
df -h
```

2. **راقب الذاكرة:**
```bash
free -h
```

3. **راقب السجلات:**
```bash
journalctl -u erp -f
```

4. **نسخ احتياطي منتظم:**
```bash
/root/erp/backup_database.sh
```

---

**🔧 معظم المشاكل تُحل بإعادة تشغيل الخدمات!**

```bash
systemctl restart erp nginx postgresql
```

