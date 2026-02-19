# إصلاح خطأ حفظ بيانات الحساب البنكي
# Bank Account Save Error Fix

## المشكلة - Problem
كان هناك خطأ عند حفظ بيانات الحساب البنكي:
```
Error: 'branch_name' is an invalid keyword argument for BankAccount
```

## السبب - Root Cause
1. النموذج `BankAccount` كان يحتوي على حقل `branch` لكن الكود كان يستخدم `branch_name`
2. النموذج كان يفتقد حقول `account_type`, `opening_balance`, و `notes` التي كانت مستخدمة في القوالب

## الإصلاحات - Fixes Applied

### 1. تحديث نموذج BankAccount (app/models_accounting.py)
تمت إضافة الحقول التالية:
- `account_type` - نوع الحساب (جاري، توفير، استثماري)
- `opening_balance` - الرصيد الافتتاحي
- `notes` - ملاحظات

### 2. تحديث routes (app/banking/routes.py)
- تم تصحيح استخدام `branch_name` إلى `branch`
- تمت إضافة جميع الحقول المفقودة

### 3. تحديث القوالب (app/templates/banking/bank_details.html)
- تم تصحيح `bank.branch_name` إلى `bank.branch`

## تطبيق التغييرات على قاعدة البيانات
## Apply Database Changes

### الطريقة 1: استخدام Flask-Migrate (الموصى بها)
```bash
flask db upgrade
```

### الطريقة 2: تطبيق SQL مباشرة
قم بتشغيل الملف `migrations/add_bank_account_fields.sql` على قاعدة البيانات:

```bash
# For SQLite
sqlite3 instance/erp.db < migrations/add_bank_account_fields.sql

# For MySQL
mysql -u username -p database_name < migrations/add_bank_account_fields.sql

# For PostgreSQL
psql -U username -d database_name -f migrations/add_bank_account_fields.sql
```

### الطريقة 3: من داخل Python
```python
from app import create_app, db
app = create_app()
with app.app_context():
    db.engine.execute(open('migrations/add_bank_account_fields.sql').read())
```

## التحقق من الإصلاح - Verify Fix
بعد تطبيق التغييرات:
1. قم بتشغيل التطبيق
2. انتقل إلى صفحة إضافة حساب بنكي
3. قم بملء النموذج وحفظه
4. يجب أن يتم الحفظ بنجاح دون أخطاء

## الملفات المعدلة - Modified Files
- `app/models_accounting.py` - تحديث نموذج BankAccount
- `app/banking/routes.py` - تصحيح استخدام الحقول
- `app/templates/banking/bank_details.html` - تصحيح اسم الحقل
- `migrations/versions/add_fields_to_bank_accounts.py` - ملف migration
- `migrations/add_bank_account_fields.sql` - ملف SQL للتطبيق المباشر

