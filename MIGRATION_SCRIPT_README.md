# 🔄 Database Migration Script - README
# سكريبت ترحيل قاعدة البيانات - دليل الاستخدام

**File:** `migrate_to_multitenant.py`  
**Purpose:** Migrate DED ERP from single-tenant to multi-tenant database structure  
**الغرض:** ترحيل نظام DED ERP من قاعدة بيانات أحادية المستأجر إلى متعددة المستأجرين

---

## ⚠️ IMPORTANT - مهم جداً

### Before Running | قبل التشغيل

1. **BACKUP YOUR DATABASE!** | **احفظ نسخة احتياطية من قاعدة البيانات!**
   ```bash
   # PostgreSQL backup
   pg_dump -U postgres -d ded_erp > backup_$(date +%Y%m%d_%H%M%S).sql
   
   # Or using pgAdmin - right-click database → Backup
   ```

2. **Close all application instances** | **أغلق جميع نوافذ التطبيق**
   - Stop the Flask server
   - Close any database connections

3. **Test on a copy first** | **جرب على نسخة تجريبية أولاً**
   - Recommended to test on a database copy before production

---

## 📋 What This Script Does | ما يقوم به السكريبت

### Step 1: Create Tenants Table
- Creates the `tenants` table with all necessary columns
- Adds indexes for performance
- Sets up unique constraints

### Step 2: Add tenant_id Columns
- Adds `tenant_id` column to all 49 tables
- Creates foreign key constraints
- Creates indexes on tenant_id

### Step 3: Create Default Tenant
- Creates a default tenant from existing company data
- Uses company name, email, phone from the `companies` table
- Sets plan to 'enterprise' with unlimited limits

### Step 4: Migrate Existing Data
- Updates all existing records with the default tenant_id
- Ensures no data is lost
- Maintains all relationships

### Step 5: Update Unique Constraints
- Updates unique constraints to include tenant_id
- Ensures data uniqueness per tenant
- Handles 30+ constraints across all tables

### Step 6: Make tenant_id NOT NULL
- Changes tenant_id from nullable to NOT NULL
- Ensures data integrity
- Only after all data is migrated

### Step 7: Verify Migration
- Checks that tenants table exists
- Verifies all tables have tenant_id
- Checks for NULL values
- Provides migration report

---

## 🚀 How to Run | كيفية التشغيل

### Method 1: Direct Execution | التشغيل المباشر

```bash
# Navigate to project directory
cd C:\Users\DELL\DED

# Run the migration script
python migrate_to_multitenant.py
```

### Method 2: From Python Shell | من Python Shell

```python
import sys
sys.path.insert(0, r'C:\Users\DELL\DED')

from migrate_to_multitenant import main
main()
```

---

## 📊 Expected Output | النتيجة المتوقعة

```
======================================================================
        🚀 DED ERP Multi-Tenant Migration 🚀
======================================================================

ℹ Started at: 2026-02-17 14:30:00

======================================================================
        ⚠️  IMPORTANT: DATABASE BACKUP REQUIRED  ⚠️
======================================================================

⚠ This script will modify your database structure!
⚠ Make sure you have a backup before proceeding.

Have you backed up your database? (yes/no): yes
✓ Proceeding with migration...

ℹ Checking database connection...
✓ Database connection successful

ℹ Total tables to migrate: 49

======================================================================
        Step 1: Creating Tenants Table
======================================================================

ℹ Creating tenants table...
✓ Tenants table created successfully

======================================================================
        Step 2: Adding tenant_id Columns
======================================================================

ℹ Adding tenant_id to 'users'...
✓ Added tenant_id to 'users'
...
ℹ Summary: 49 added, 0 skipped, 0 errors

======================================================================
        Step 3: Creating Default Tenant
======================================================================

ℹ Creating default tenant: شركتك
✓ Default tenant created with ID: 1

======================================================================
        Step 4: Migrating Existing Data
======================================================================

ℹ Migrating 5 records in 'users'...
✓ Migrated 5 records in 'users'
...
ℹ Summary: 49 migrated, 0 skipped, 0 errors

======================================================================
        Step 5: Updating Unique Constraints
======================================================================

ℹ Updating constraint 'uq_branch_code' on 'branches'...
✓ Updated constraint on 'branches'
...
ℹ Summary: 30 updated, 0 skipped, 0 errors

======================================================================
        Step 6: Making tenant_id NOT NULL
======================================================================

ℹ Making tenant_id NOT NULL in 'users'...
✓ Made tenant_id NOT NULL in 'users'
...
ℹ Summary: 49 updated, 0 skipped, 0 errors

======================================================================
        Step 7: Verifying Migration
======================================================================

ℹ Checking tenants table...
✓ Tenants table exists with 1 tenant(s)
ℹ Checking tenant_id columns...
✓ All 49 tables have tenant_id column
ℹ Checking for NULL tenant_id values...
✓ No NULL tenant_id values found

✓ ✅ Migration verification PASSED!

======================================================================
        🎉 Migration Complete! 🎉
======================================================================

✓ Multi-tenant migration completed successfully!

ℹ Next steps:
  1. Initialize TenantMiddleware in app/__init__.py
  2. Register tenant events using init_tenant_support(app)
  3. Test tenant isolation
  4. Create tenant management UI

ℹ Completed at: 2026-02-17 14:35:00
```

---

## 🔍 Troubleshooting | حل المشاكل

### Problem: "Database connection failed"
**Solution:**
- Make sure PostgreSQL is running
- Check database credentials in `config.py`
- Verify database name is correct

### Problem: "Table already has tenant_id"
**Solution:**
- This is normal if you run the script twice
- The script will skip already migrated tables
- Safe to continue

### Problem: "Failed to create tenants table"
**Solution:**
- Check if table already exists
- Verify database user has CREATE TABLE permission
- Check PostgreSQL logs for details

### Problem: "Some tables have NULL tenant_id"
**Solution:**
- Check which tables have NULL values
- Manually update those records
- Re-run Step 6 to make NOT NULL

---

## 📁 Files Modified | الملفات المعدلة

This script will modify:
- **Database structure** (adds tables and columns)
- **Existing data** (adds tenant_id to all records)

This script will NOT modify:
- Python code files
- Configuration files
- Templates or static files

---

## ⏱️ Estimated Time | الوقت المتوقع

- Small database (<1000 records): 2-5 minutes
- Medium database (1000-10000 records): 5-15 minutes
- Large database (>10000 records): 15-30 minutes

---

## ✅ Post-Migration Checklist | قائمة ما بعد الترحيل

- [ ] Verify migration completed successfully
- [ ] Check that default tenant was created
- [ ] Test application login
- [ ] Verify data is visible
- [ ] Initialize middleware (see MULTI_TENANT_MIGRATION_GUIDE.md)
- [ ] Test creating new records
- [ ] Test tenant isolation

---

## 🆘 Need Help? | تحتاج مساعدة؟

If you encounter any issues:
1. Check the error message carefully
2. Review the PostgreSQL logs
3. Check that you have a database backup
4. You can restore from backup if needed:
   ```bash
   psql -U postgres -d ded_erp < backup_file.sql
   ```

---

**Created by:** Augment Agent  
**Date:** 2026-02-17  
**Version:** 1.0

