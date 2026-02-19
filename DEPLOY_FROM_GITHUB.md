# 🚀 نشر المشروع من GitHub إلى السيرفر

---

## 📋 **الخطوات الكاملة:**

---

## **الخطوة 1: الاتصال بالسيرفر**

### **الطريقة 1: Hostinger Browser Terminal** ⭐ (الأسهل)

1. افتح: https://hpanel.hostinger.com/
2. اذهب إلى: **VPS**
3. اضغط على: **Browser Terminal** أو **Web Terminal**

### **الطريقة 2: PowerShell**

```powershell
ssh root@147.79.102.91
```
**كلمة المرور:** `l6TkO4puC+WTHYH(-s-`

---

## **الخطوة 2: سحب المشروع من GitHub**

**في Terminal السيرفر، نفّذ الأوامر التالية:**

### **1. تثبيت Git**
```bash
apt-get update
apt-get install -y git
```

### **2. سحب المشروع**

**إذا كان Repository عام (Public):**
```bash
cd /root
git clone https://github.com/calcattaceramica-create/ded-erp-system.git DED
cd DED
```

**إذا كان Repository خاص (Private):**
```bash
cd /root
git clone https://github.com/calcattaceramica-create/ded-erp-system.git DED
```
**سيطلب منك:**
- **Username:** `calcattaceramica-create`
- **Password:** استخدم **Personal Access Token** (ليس كلمة المرور العادية)

---

## **الخطوة 3: إنشاء Personal Access Token (إذا كان Repository خاص)**

1. افتح: https://github.com/settings/tokens
2. اضغط: **Generate new token** → **Generate new token (classic)**
3. املأ:
   - **Note:** `ERP Deployment`
   - **Expiration:** 90 days
   - **Select scopes:** ضع علامة ✓ على `repo`
4. اضغط: **Generate token**
5. **انسخ Token** (لن تراه مرة أخرى!)
6. استخدمه كـ **Password** عند سحب المشروع

---

## **الخطوة 4: تشغيل سكريبت النشر**

```bash
cd /root/DED
chmod +x deploy_via_git.sh
./deploy_via_git.sh
```

**المدة المتوقعة:** 10-15 دقيقة

---

## **الخطوة 5: التحقق من النشر**

**بعد اكتمال السكريبت، افتح المتصفح:**

```
https://srv1392516.hstgr.cloud
```

**أو:**

```
http://147.79.102.91
```

**تسجيل الدخول:**
- **Username:** `admin`
- **Password:** `admin123`

---

## 🔄 **التحديثات المستقبلية**

### **على جهازك (Windows):**

```bash
cd C:\Users\DELL\DED
git add .
git commit -m "وصف التحديث"
git push
```

### **على السيرفر:**

```bash
cd /root/DED
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart erp
```

---

## ⚠️ **حل المشاكل الشائعة**

### **مشكلة: Permission denied (publickey)**
**الحل:** استخدم Personal Access Token بدلاً من كلمة المرور

### **مشكلة: Repository not found**
**الحل:** 
- تأكد من اسم Repository صحيح
- تأكد من أن Repository عام أو لديك صلاحيات الوصول

### **مشكلة: fatal: could not create work tree**
**الحل:** 
```bash
rm -rf /root/DED
git clone https://github.com/calcattaceramica-create/ded-erp-system.git DED
```

---

## 📊 **ملخص الأوامر السريعة**

```bash
# على السيرفر (مرة واحدة)
apt-get update && apt-get install -y git
cd /root
git clone https://github.com/calcattaceramica-create/ded-erp-system.git DED
cd DED
chmod +x deploy_via_git.sh
./deploy_via_git.sh

# للتحديثات المستقبلية
cd /root/DED
git pull
systemctl restart erp
```

---

## ✅ **المزايا:**

- ✅ **سهولة التحديثات** - فقط `git pull`
- ✅ **تتبع التغييرات** - كل التعديلات مسجلة
- ✅ **النسخ الاحتياطي** - المشروع محفوظ على GitHub
- ✅ **الأمان** - Repository خاص
- ✅ **الاحترافية** - طريقة معتمدة عالمياً

---

**🚀 ابدأ الآن! افتح Terminal السيرفر ونفّذ الأوامر!**

