# 🚀 دليل النشر عبر Git

---

## 📋 **الخطوات الكاملة:**

---

## **الجزء 1: رفع المشروع إلى GitHub**

### **الخطوة 1: إنشاء Repository على GitHub**

1. **افتح:** https://github.com/new

2. **املأ المعلومات:**
   - **Repository name:** `erp-system`
   - **Description:** `ERP Management System`
   - **Visibility:** Private (موصى به) أو Public
   - **لا تضع علامة** على "Add README"

3. **اضغط:** "Create repository"

---

### **الخطوة 2: رفع المشروع من جهازك**

**افتح PowerShell في مجلد المشروع:**

```powershell
cd C:\Users\DELL\DED
```

**نفّذ الأوامر التالية:**

```bash
# تهيئة Git
git init

# إضافة جميع الملفات
git add .

# عمل Commit
git commit -m "Initial commit - ERP System"

# ربط المشروع بـ GitHub (استبدل USERNAME باسم المستخدم الخاص بك)
git remote add origin https://github.com/USERNAME/erp-system.git

# رفع المشروع
git branch -M main
git push -u origin main
```

**ملاحظة:** سيطلب منك اسم المستخدم وكلمة المرور (أو Personal Access Token)

---

## **الجزء 2: سحب المشروع على السيرفر**

### **الخطوة 1: الاتصال بالسيرفر**

**استخدم أحد الطرق:**

#### **الطريقة 1: Hostinger Browser Terminal**
- افتح: https://hpanel.hostinger.com/
- اذهب إلى: VPS → Browser Terminal

#### **الطريقة 2: PowerShell**
```powershell
ssh root@147.79.102.91
```
(كلمة المرور: `l6TkO4puC+WTHYH(-s-`)

---

### **الخطوة 2: سحب المشروع من GitHub**

**في Terminal السيرفر، نفّذ:**

```bash
# الانتقال إلى مجلد root
cd /root

# تثبيت Git (إذا لم يكن مثبت)
apt-get update
apt-get install -y git

# سحب المشروع (استبدل USERNAME باسم المستخدم)
git clone https://github.com/USERNAME/erp-system.git DED

# الدخول إلى المجلد
cd DED
```

**إذا كان Repository خاص (Private):**
```bash
# سيطلب منك اسم المستخدم وكلمة المرور
# استخدم Personal Access Token بدلاً من كلمة المرور
```

---

### **الخطوة 3: تشغيل سكريبت النشر**

```bash
# إعطاء صلاحيات التنفيذ
chmod +x deploy_via_git.sh

# تشغيل السكريبت
./deploy_via_git.sh
```

**المدة المتوقعة:** 10-15 دقيقة

---

## **الجزء 3: التحديثات المستقبلية**

### **عند تعديل المشروع:**

**على جهازك:**
```bash
cd C:\Users\DELL\DED
git add .
git commit -m "وصف التعديلات"
git push
```

**على السيرفر:**
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

## 🔑 **إنشاء Personal Access Token (إذا كان Repository خاص)**

1. **افتح:** https://github.com/settings/tokens

2. **اضغط:** "Generate new token" → "Generate new token (classic)"

3. **املأ:**
   - **Note:** `ERP Deployment`
   - **Expiration:** 90 days (أو حسب الحاجة)
   - **Select scopes:** ضع علامة على `repo`

4. **اضغط:** "Generate token"

5. **انسخ Token** (لن تراه مرة أخرى!)

6. **استخدمه بدلاً من كلمة المرور** عند سحب المشروع

---

## ✅ **المزايا:**

- ✅ **سهولة التحديثات** - فقط `git pull`
- ✅ **تتبع التغييرات** - كل التعديلات مسجلة
- ✅ **النسخ الاحتياطي** - المشروع محفوظ على GitHub
- ✅ **التعاون** - يمكن لعدة مطورين العمل
- ✅ **الرجوع للإصدارات السابقة** - إذا حدثت مشكلة

---

## 🎯 **الخلاصة:**

### **على جهازك (مرة واحدة):**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/erp-system.git
git push -u origin main
```

### **على السيرفر (مرة واحدة):**
```bash
cd /root
git clone https://github.com/USERNAME/erp-system.git DED
cd DED
chmod +x deploy_via_git.sh
./deploy_via_git.sh
```

### **للتحديثات المستقبلية:**
```bash
# على جهازك
git add .
git commit -m "تحديث"
git push

# على السيرفر
cd /root/DED
git pull
systemctl restart erp
```

---

## 📞 **إذا واجهت مشكلة:**

### **مشكلة: Git يطلب اسم المستخدم وكلمة المرور كل مرة**
**الحل:** استخدم SSH key بدلاً من HTTPS

### **مشكلة: Permission denied**
**الحل:** تأكد من صلاحيات الملفات: `chmod +x deploy_via_git.sh`

### **مشكلة: Repository not found**
**الحل:** تأكد من اسم المستخدم واسم Repository صحيح

---

**🚀 ابدأ الآن! اتبع الخطوات بالترتيب!**

