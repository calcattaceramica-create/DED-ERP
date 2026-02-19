# 🏢 Multi-Tenant Migration Guide
# دليل الترحيل إلى نظام متعدد المستأجرين

---

## 📋 Overview | نظرة عامة

This guide explains how to migrate the DED ERP system to a multi-tenant architecture.

يشرح هذا الدليل كيفية ترحيل نظام DED ERP إلى بنية متعددة المستأجرين.

---

## 🎯 Strategy | الاستراتيجية

**Type:** Row-Level Multi-Tenancy (Shared Database, Shared Schema)

**النوع:** تعدد المستأجرين على مستوى الصف (قاعدة بيانات مشتركة، مخطط مشترك)

### Advantages | المميزات:
- ✅ Easy maintenance | سهولة الصيانة
- ✅ Resource efficient | كفاءة الموارد
- ✅ Easy backup | سهولة النسخ الاحتياطي
- ✅ Scalable for many tenants | قابل للتوسع لعدد كبير من المستأجرين

---

## 📁 Files Created | الملفات المنشأة

### 1. `app/models_tenant.py`
- **Tenant** model - Main tenant/company model
- نموذج المستأجر - النموذج الرئيسي للشركات

### 2. `app/tenant_mixin.py`
- **TenantMixin** - Mixin to add tenant_id to models
- **TenantQuery** - Custom query class with automatic filtering
- Helper functions for tenant management

### 3. `app/tenant_middleware.py`
- **TenantMiddleware** - Identifies current tenant from:
  - Subdomain (e.g., company1.localhost)
  - Session (logged-in user)
  - HTTP Header (API requests)
  - User object

---

## 🔄 Models Updated | النماذج المحدثة

### ✅ Already Updated:

1. **User** (`app/models.py`)
   - Added `tenant_id`
   - Added `is_super_admin` field
   - Changed unique constraints to include `tenant_id`
   - Added relationship to `Tenant`

2. **Company** (`app/models.py`)
   - Added `tenant_id`
   - Added relationship to `Tenant`

3. **Branch** (`app/models.py`)
   - Added `tenant_id`
   - Changed unique constraint on `code` to include `tenant_id`
   - Added relationship to `Tenant`

---

## 📝 Models That Need Update | النماذج التي تحتاج تحديث

### Inventory Models (`app/models_inventory.py`):
- [ ] Category
- [ ] Unit
- [ ] Product
- [ ] Warehouse
- [ ] Stock
- [ ] StockMovement
- [ ] DamagedInventory

### Sales Models (`app/models_sales.py`):
- [ ] Customer
- [ ] SalesInvoice
- [ ] SalesInvoiceItem
- [ ] Quotation
- [ ] QuotationItem
- [ ] SalesOrder

### Purchase Models (`app/models_purchases.py`):
- [ ] Supplier
- [ ] PurchaseOrder
- [ ] PurchaseOrderItem
- [ ] PurchaseInvoice
- [ ] PurchaseInvoiceItem
- [ ] PurchaseReturn
- [ ] PurchaseReturnItem

### Accounting Models (`app/models_accounting.py`):
- [ ] Account
- [ ] JournalEntry
- [ ] JournalEntryItem
- [ ] Payment
- [ ] BankAccount
- [ ] CostCenter
- [ ] BankTransaction
- [ ] Expense

### HR Models (`app/models_hr.py`):
- [ ] Employee
- [ ] Department
- [ ] Position
- [ ] Attendance
- [ ] Leave
- [ ] LeaveType
- [ ] Payroll

### POS Models (`app/models_pos.py`):
- [ ] POSSession
- [ ] POSOrder
- [ ] POSOrderItem

### Settings Models (`app/models_settings.py`):
- [ ] SystemSettings
- [ ] AccountingSettings

### CRM Models (`app/models_crm.py`):
- [ ] Lead
- [ ] Interaction
- [ ] Opportunity
- [ ] Task
- [ ] Campaign
- [ ] Contact

---

## 🛠️ How to Update Each Model | كيفية تحديث كل نموذج

For each model, add the following:

### 1. Add tenant_id field:
```python
tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)
```

### 2. Add relationship (optional but recommended):
```python
tenant = db.relationship('Tenant', foreign_keys=[tenant_id], backref='model_name_plural')
```

### 3. Update unique constraints:
If the model has unique fields (like `code`, `name`, etc.), update them to include `tenant_id`:

```python
__table_args__ = (
    db.UniqueConstraint('code', 'tenant_id', name='uq_modelname_code_tenant'),
)
```

---

## 🔧 Next Steps | الخطوات التالية

1. ✅ Create Tenant model
2. ✅ Create TenantMixin
3. ✅ Create TenantMiddleware
4. ✅ Update User, Company, Branch models
5. ⏳ Update all other models (in progress)
6. ⏳ Create migration script
7. ⏳ Update routes and views
8. ⏳ Create tenant registration page
9. ⏳ Test tenant isolation

---

## 📊 Database Migration | ترحيل قاعدة البيانات

After updating all models, you'll need to:

1. Create migration script to add `tenant_id` column to all tables
2. Create default tenant for existing data
3. Update all existing records with default tenant_id
4. Make `tenant_id` NOT NULL after data migration

---

## 🔒 Security Considerations | اعتبارات الأمان

1. **Data Isolation**: Ensure all queries filter by tenant_id
2. **Super Admin**: Only super admins can access multiple tenants
3. **Tenant Validation**: Always validate tenant_id in requests
4. **Cross-Tenant Access**: Prevent users from accessing other tenants' data

---

## 🚀 Features to Implement | الميزات المطلوب تنفيذها

- [ ] Tenant registration page
- [ ] Tenant selection for super admins
- [ ] Subdomain-based access
- [ ] Tenant dashboard
- [ ] Subscription management
- [ ] Usage limits enforcement
- [ ] Tenant-specific branding
- [ ] Multi-tenant reporting

---

**Status:** 🟡 In Progress | قيد التنفيذ

**Last Updated:** 2026-02-17

