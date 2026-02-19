# إصلاح مشكلة JSON Serialization في المدفوعات والمقبوضات
# Fix Payments and Receipts JSON Serialization Issue

## 🔍 المشكلة | Problem

عند محاولة فتح صفحة إضافة مدفوعة/مقبوضات (`/accounting/payments/add`)، كان يظهر خطأ:

```
TypeError: Object of type Customer is not JSON serializable
```

When trying to open the add payment/receipt page, the following error appeared:

```
TypeError: Object of type Customer is not JSON serializable
```

---

## 🎯 السبب | Root Cause

في ملف `app/accounting/routes.py`، كان يتم تمرير كائنات SQLAlchemy (`Customer` و `Supplier`) مباشرة إلى القالب:

```python
customers = Customer.query.filter_by(is_active=True).all()
suppliers = Supplier.query.filter_by(is_active=True).all()

return render_template('accounting/add_payment.html',
                     customers=customers,
                     suppliers=suppliers,
                     bank_accounts=bank_accounts)
```

في القالب `add_payment.html`، كان يتم محاولة تحويل هذه الكائنات إلى JSON:

```javascript
const customers = {{ customers|tojson }};
const suppliers = {{ suppliers|tojson }};
```

**المشكلة:** كائنات SQLAlchemy لا يمكن تحويلها مباشرة إلى JSON!

---

## ✅ الحل | Solution

تم تحويل كائنات SQLAlchemy إلى قواميس (dictionaries) قبل تمريرها للقالب:

**الملف:** `app/accounting/routes.py` - السطور 345-357

```python
# Get data for dropdowns
customers = Customer.query.filter_by(is_active=True).all()
suppliers = Supplier.query.filter_by(is_active=True).all()
bank_accounts = BankAccount.query.filter_by(is_active=True).all()

# Convert to dictionaries for JSON serialization
customers_dict = [{'id': c.id, 'name': c.name} for c in customers]
suppliers_dict = [{'id': s.id, 'name': s.name} for s in suppliers]

return render_template('accounting/add_payment.html',
                     customers=customers_dict,
                     suppliers=suppliers_dict,
                     bank_accounts=bank_accounts)
```

---

## 📋 التغييرات | Changes Made

### ✅ ملف واحد تم تعديله | One File Modified

**1. `app/accounting/routes.py`** - Route: `add_payment()`
- ✅ تحويل `customers` إلى قائمة من القواميس
- ✅ تحويل `suppliers` إلى قائمة من القواميس
- ✅ الآن يمكن تحويلها إلى JSON بدون أخطاء

---

## 🎯 النتيجة | Result

الآن عند فتح صفحة إضافة مدفوعة/مقبوضات:

✅ الصفحة تفتح بدون أخطاء
✅ قائمة العملاء تظهر بشكل صحيح
✅ قائمة الموردين تظهر بشكل صحيح
✅ يمكن اختيار العميل/المورد من القائمة المنسدلة
✅ JavaScript يعمل بشكل صحيح

---

## 🧪 كيفية الاختبار | How to Test

1. **افتح صفحة المدفوعات:**
   ```
   اذهب إلى: المحاسبة > المدفوعات والمقبوضات
   ```

2. **اضغط على "إضافة مدفوعة جديدة"**
   ```
   يجب أن تفتح الصفحة بدون أخطاء ✅
   ```

3. **اختر نوع العملية:**
   - مقبوضات (استلام نقدية)
   - مدفوعات (دفع نقدية)

4. **اختر نوع الجهة:**
   - عميل → يجب أن تظهر قائمة العملاء ✅
   - مورد → يجب أن تظهر قائمة الموردين ✅

5. **أكمل البيانات واحفظ:**
   - يجب أن يتم الحفظ بنجاح ✅

---

## 📊 ملخص | Summary

| العنصر | قبل | بعد |
|--------|-----|-----|
| **نوع البيانات** | SQLAlchemy Objects | Python Dictionaries |
| **JSON Serialization** | ❌ فشل | ✅ نجح |
| **صفحة المدفوعات** | ❌ خطأ | ✅ تعمل |
| **قائمة العملاء** | ❌ لا تظهر | ✅ تظهر |
| **قائمة الموردين** | ❌ لا تظهر | ✅ تظهر |

---

**تاريخ الإصلاح:** 2026-02-13
**الحالة:** ✅ تم الإصلاح بنجاح

