# 🔐 User Permissions System Guide
# دليل نظام صلاحيات المستخدمين

## 📋 System Overview / نظرة عامة على النظام

The system has **3 main components**:
النظام يحتوي على **3 مكونات رئيسية**:

1. **Users (المستخدمون)** - Individual user accounts
2. **Roles (الأدوار)** - Groups of permissions
3. **Permissions (الصلاحيات)** - Individual access rights

---

## 🔗 How It Works / كيف يعمل

```
User (المستخدم)
    ↓
Has ONE Role (له دور واحد)
    ↓
Role has MANY Permissions (الدور يحتوي على عدة صلاحيات)
```

**Example:**
```
User: ali
    ↓
Role: manager
    ↓
Permissions: 
    - dashboard.view
    - sales.invoices.view
    - sales.invoices.add
    - inventory.products.view
    - reports.view
```

---

## 📊 Current System Status / حالة النظام الحالية

✅ **Permissions:** 117 permissions created
✅ **Roles:** admin, manager, and others
✅ **Users:** 2 users (admin, ali)

---

## 🎯 How to Manage Users / كيفية إدارة المستخدمين

### Step 1: Access User Management / الوصول لإدارة المستخدمين

1. Login as admin
2. Go to: **Settings → Users**
3. Or visit: `http://localhost:5000/settings/users`

### Step 2: Create New User / إنشاء مستخدم جديد

1. Click **"Add New User"** button
2. Fill in the form:
   - **Username** (اسم المستخدم): Unique username
   - **Email** (البريد الإلكتروني): User's email
   - **Full Name** (الاسم الكامل): User's full name
   - **Password** (كلمة المرور): Initial password
   - **Phone** (الهاتف): Optional
   - **Role** (الدور): Select from dropdown
   - **Is Active** (نشط): Check to activate user
   - **Is Admin** (مدير): Check for full admin access
3. Click **"Save"**

### Step 3: Edit Existing User / تعديل مستخدم موجود

1. Find the user in the list
2. Click **"Edit"** button
3. Modify the fields
4. Click **"Save"**

### Step 4: Assign Role to User / تعيين دور للمستخدم

1. Edit the user
2. Select a role from the **"Role"** dropdown
3. Save

**Important Notes:**
- ⚠️ If user has `is_admin = True`, they have ALL permissions regardless of role
- ⚠️ If user has no role, they have NO permissions (except admins)

---

## 🎭 How to Manage Roles / كيفية إدارة الأدوار

### Step 1: Access Role Management / الوصول لإدارة الأدوار

1. Go to: **Settings → Roles**
2. Or visit: `http://localhost:5000/settings/roles`

### Step 2: Create New Role / إنشاء دور جديد

1. Click **"Add New Role"** button
2. Fill in:
   - **Name** (الاسم): English name (e.g., "accountant")
   - **Name (Arabic)** (الاسم بالعربية): Arabic name (e.g., "محاسب")
   - **Description** (الوصف): Optional description
3. Click **"Save"**

### Step 3: Assign Permissions to Role / تعيين صلاحيات للدور

1. Find the role in the list
2. Click **"Edit Permissions"** button
3. Check the permissions you want to assign
4. Click **"Save Permissions"**

**Permissions are organized by module:**
- **Dashboard** - لوحة التحكم
- **Inventory** - المخزون
- **Sales** - المبيعات
- **Purchases** - المشتريات
- **Accounting** - المحاسبة
- **Reports** - التقارير
- **POS** - نقطة البيع
- **Settings** - الإعدادات

---

## 📝 Common Role Examples / أمثلة على الأدوار الشائعة

### 1. Accountant Role (دور المحاسب)

**Permissions:**
- ✅ dashboard.view
- ✅ accounting.view
- ✅ accounting.manage
- ✅ accounting.payments.view
- ✅ accounting.payments.manage
- ✅ reports.view
- ✅ reports.financial
- ❌ inventory.products.delete
- ❌ settings.users.manage

### 2. Sales Manager (مدير المبيعات)

**Permissions:**
- ✅ dashboard.view
- ✅ sales.invoices.view
- ✅ sales.invoices.add
- ✅ sales.invoices.edit
- ✅ sales.customers.view
- ✅ sales.customers.manage
- ✅ pos.access
- ✅ pos.sell
- ✅ reports.view
- ✅ reports.sales
- ❌ purchases.*
- ❌ settings.users.manage

### 3. Warehouse Manager (مدير المخزن)

**Permissions:**
- ✅ dashboard.view
- ✅ inventory.products.view
- ✅ inventory.products.add
- ✅ inventory.products.edit
- ✅ inventory.stock.view
- ✅ inventory.stock.manage
- ✅ purchases.invoices.view
- ✅ purchases.confirm
- ✅ reports.view
- ✅ reports.inventory
- ❌ sales.invoices.delete
- ❌ accounting.*

### 4. Cashier (أمين الصندوق)

**Permissions:**
- ✅ pos.access
- ✅ pos.sell
- ✅ sales.invoices.view
- ✅ sales.customers.view
- ❌ sales.invoices.delete
- ❌ inventory.products.edit
- ❌ settings.*

---

## 🔒 Permission Naming Convention / تسمية الصلاحيات

Permissions follow this pattern:
```
module.resource.action
```

**Examples:**
- `dashboard.view` - View dashboard
- `inventory.products.add` - Add products
- `sales.invoices.edit` - Edit sales invoices
- `purchases.confirm` - Confirm purchase invoices
- `settings.users.manage` - Manage users

---

## ⚙️ Testing Permissions / اختبار الصلاحيات

### Test 1: Create a Limited User

1. Create a new role called "test_role"
2. Assign only these permissions:
   - dashboard.view
   - sales.invoices.view
3. Create a new user "test_user"
4. Assign "test_role" to "test_user"
5. Logout and login as "test_user"
6. Try to access different pages:
   - ✅ Dashboard - Should work
   - ✅ Sales → Invoices (view only) - Should work
   - ❌ Sales → Add Invoice - Should be blocked
   - ❌ Inventory - Should be blocked
   - ❌ Settings - Should be blocked

### Test 2: Modify Permissions

1. Login as admin
2. Go to Settings → Roles
3. Edit "test_role"
4. Add permission: `sales.invoices.add`
5. Save
6. Login as "test_user" again
7. Now you should be able to add invoices

---

## 🚨 Important Security Notes / ملاحظات أمنية مهمة

1. **Admin Users:**
   - Users with `is_admin = True` bypass ALL permission checks
   - Use admin status sparingly
   - Only give to trusted users

2. **Role Assignment:**
   - Each user should have exactly ONE role
   - Users without roles have NO access (except admins)

3. **Permission Changes:**
   - Changes to role permissions take effect immediately
   - Users don't need to logout/login

4. **Default Roles:**
   - Don't delete the "admin" role
   - It's used by admin users

---

## 📞 Quick Reference / مرجع سريع

| Task | URL |
|------|-----|
| Manage Users | `/settings/users` |
| Manage Roles | `/settings/roles` |
| Manage Permissions | `/settings/permissions` |

---

**System is ready to use! / النظام جاهز للاستخدام! 🚀**

