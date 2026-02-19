# 🏢 Multi-Tenant System - نظام متعدد المستأجرين

## 📋 Overview | نظرة عامة

تم تحويل نظام DED ERP إلى نظام **Multi-Tenant** يسمح بإدارة عدة شركات/منظمات في نفس التطبيق مع عزل كامل للبيانات.

The DED ERP system has been converted to a **Multi-Tenant** system that allows managing multiple companies/organizations in the same application with complete data isolation.

---

## 🎯 Multi-Tenancy Strategy | استراتيجية التعدد

### **Row-Level Multi-Tenancy** (Shared Database, Shared Schema)

**المميزات:**
- ✅ سهولة الصيانة - Easy maintenance
- ✅ توفير الموارد - Resource efficiency
- ✅ سهولة النسخ الاحتياطي - Easy backup
- ✅ مناسب لعدد كبير من الشركات - Suitable for many tenants

**الآلية:**
1. إضافة `tenant_id` لجميع الجداول
2. فلترة تلقائية لجميع الاستعلامات
3. عزل كامل للبيانات بين الشركات

---

## 📁 Files Structure | هيكل الملفات

```
app/
├── models_tenant.py          # Tenant model
├── tenant_mixin.py           # Mixin for adding tenant_id to models
├── tenant_middleware.py      # Middleware for tenant identification
└── models.py                 # Updated with tenant support
```

---

## 🗄️ Database Changes | تغييرات قاعدة البيانات

### New Table: `tenants`

```sql
CREATE TABLE tenants (
    id INTEGER PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    subdomain VARCHAR(63) UNIQUE NOT NULL,
    name VARCHAR(128) NOT NULL,
    name_en VARCHAR(128),
    tax_number VARCHAR(64),
    email VARCHAR(120),
    phone VARCHAR(20),
    currency VARCHAR(3) DEFAULT 'SAR',
    tax_rate FLOAT DEFAULT 15.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Updated Tables:

All main tables now have:
- `tenant_id INTEGER FOREIGN KEY REFERENCES tenants(id)`
- Unique constraints updated to include `tenant_id`

**Examples:**
- `users`: `UNIQUE(username, tenant_id)`, `UNIQUE(email, tenant_id)`
- `branches`: `UNIQUE(code, tenant_id)`
- `products`: `UNIQUE(code, tenant_id)`
- `customers`: `UNIQUE(code, tenant_id)`

---

## 🔧 How It Works | كيف يعمل

### 1. Tenant Identification | تحديد المستأجر

The system identifies the current tenant from:

1. **Subdomain** (Recommended)
   - `company1.localhost:5000` → tenant with subdomain='company1'
   - `company2.example.com` → tenant with subdomain='company2'

2. **Session** (For logged-in users)
   - Stored in `session['tenant_id']`

3. **HTTP Header** (For API requests)
   - `X-Tenant-ID: 5`
   - `X-Tenant-Code: COMP001`

4. **User** (From logged-in user)
   - `current_user.tenant_id`

### 2. Automatic Filtering | الفلترة التلقائية

All database queries are automatically filtered by `tenant_id`:

```python
# Before (returns all products)
products = Product.query.all()

# After (returns only current tenant's products)
products = Product.query.all()  # Automatically filtered!
```

### 3. Data Isolation | عزل البيانات

- Each tenant can only see and modify their own data
- Complete isolation between tenants
- No cross-tenant data access

---

## 🚀 Usage | الاستخدام

### Creating a New Tenant | إنشاء مستأجر جديد

```python
from app.models_tenant import Tenant
from app import db

# Create new tenant
tenant = Tenant(
    code='COMP001',
    subdomain='company1',
    name='شركة المثال',
    name_en='Example Company',
    email='info@company1.com',
    phone='+966501234567',
    currency='SAR',
    tax_rate=15.0,
    plan='professional',
    max_users=20,
    max_branches=5
)

db.session.add(tenant)
db.session.commit()
```

### Creating Users for a Tenant | إنشاء مستخدمين للمستأجر

```python
from app.models import User

# Create admin user for tenant
user = User(
    tenant_id=tenant.id,
    username='admin',
    email='admin@company1.com',
    full_name='مدير النظام',
    is_admin=True
)
user.set_password('secure_password')

db.session.add(user)
db.session.commit()
```

### Accessing Tenant Data | الوصول لبيانات المستأجر

```python
from app.tenant_mixin import set_current_tenant, with_tenant

# Set current tenant
set_current_tenant(tenant.id)

# Now all queries are filtered by this tenant
products = Product.query.all()  # Only this tenant's products

# Or use context manager
with with_tenant(5):
    # All queries here use tenant_id=5
    users = User.query.all()
```

---

## 🌐 Subdomain-Based Access | الوصول عبر النطاقات الفرعية

### Local Development:

1. Edit `hosts` file:
   ```
   127.0.0.1  company1.localhost
   127.0.0.1  company2.localhost
   ```

2. Access:
   - `https://company1.localhost:5000` → Company 1
   - `https://company2.localhost:5000` → Company 2

### Production:

1. Configure DNS:
   ```
   *.example.com → Your Server IP
   ```

2. Access:
   - `https://company1.example.com` → Company 1
   - `https://company2.example.com` → Company 2

---

## 📊 Tenant Plans | خطط الاشتراك

### Basic Plan (مجاني)
- ✅ 5 users
- ✅ 1 branch
- ✅ 100 products
- ✅ 50 invoices/month

### Professional Plan (احترافي)
- ✅ 20 users
- ✅ 5 branches
- ✅ 1000 products
- ✅ Unlimited invoices

### Enterprise Plan (مؤسسات)
- ✅ Unlimited users
- ✅ Unlimited branches
- ✅ Unlimited products
- ✅ Unlimited invoices
- ✅ Custom features

---

## 🔒 Security | الأمان

### Data Isolation:
- ✅ Complete separation between tenants
- ✅ No cross-tenant queries
- ✅ Automatic filtering on all operations

### Access Control:
- ✅ Users belong to specific tenant
- ✅ Cannot access other tenants' data
- ✅ Super admin can manage all tenants

---

## 🛠️ Migration | الترحيل

To migrate existing data to multi-tenant:

```bash
python migrate_to_multitenant.py
```

This will:
1. Create `tenants` table
2. Create default tenant from existing company
3. Update all records with `tenant_id`
4. Update unique constraints

---

## 📝 Next Steps | الخطوات التالية

1. ✅ Create tenant registration page
2. ✅ Update login to support tenant selection
3. ✅ Add tenant management dashboard
4. ✅ Implement subscription management
5. ✅ Add tenant-specific settings

---

## 🎯 Benefits | الفوائد

### For Business:
- 💰 Serve multiple clients with one installation
- 📈 Scale easily
- 💾 Centralized management
- 🔄 Easy updates for all tenants

### For Users:
- 🏢 Each company has isolated data
- 🎨 Custom branding per tenant
- ⚙️ Tenant-specific settings
- 🔒 Complete data privacy

---

**🎉 Your ERP is now Multi-Tenant ready!**

