"""
Add all missing permissions to the database
إضافة جميع الصلاحيات الناقصة إلى قاعدة البيانات
"""
from run import app, db
from app.models import Permission, Role, RolePermission

print("=" * 80)
print("🔧 إضافة جميع الصلاحيات الناقصة")
print("🔧 Adding all missing permissions")
print("=" * 80)

with app.app_context():
    # Get current permissions count
    current_count = Permission.query.count()
    print(f"\n📊 عدد الصلاحيات الحالية: {current_count}")
    print(f"📊 Current permissions count: {current_count}\n")
    
    # Complete list of all permissions
    all_permissions = [
        # Main / Dashboard
        ('dashboard.view', 'عرض لوحة التحكم', 'main'),
        
        # Inventory - Products
        ('inventory.products.view', 'عرض المنتجات', 'inventory'),
        ('inventory.products.add', 'إضافة منتج', 'inventory'),
        ('inventory.products.edit', 'تعديل منتج', 'inventory'),
        ('inventory.products.delete', 'حذف منتج', 'inventory'),
        
        # Inventory - Categories
        ('inventory.categories.view', 'عرض الفئات', 'inventory'),
        ('inventory.categories.add', 'إضافة فئة', 'inventory'),
        ('inventory.categories.edit', 'تعديل فئة', 'inventory'),
        ('inventory.categories.delete', 'حذف فئة', 'inventory'),
        
        # Inventory - Stock
        ('inventory.stock.view', 'عرض المخزون', 'inventory'),
        ('inventory.stock.add', 'إضافة مخزون', 'inventory'),
        ('inventory.stock.edit', 'تعديل مخزون', 'inventory'),
        ('inventory.stock.transfer', 'نقل مخزون', 'inventory'),
        
        # Inventory - Warehouses
        ('inventory.warehouses.view', 'عرض المستودعات', 'inventory'),
        ('inventory.warehouses.add', 'إضافة مستودع', 'inventory'),
        ('inventory.warehouses.edit', 'تعديل مستودع', 'inventory'),
        ('inventory.warehouses.delete', 'حذف مستودع', 'inventory'),
        
        # Inventory - Damaged
        ('inventory.damaged.view', 'عرض المخزون التالف', 'inventory'),
        ('inventory.damaged.add', 'إضافة مخزون تالف', 'inventory'),
        ('inventory.damaged.edit', 'تعديل مخزون تالف', 'inventory'),
        ('inventory.damaged.delete', 'حذف مخزون تالف', 'inventory'),
        
        # Sales - Invoices
        ('sales.invoices.view', 'عرض فواتير المبيعات', 'sales'),
        ('sales.invoices.add', 'إضافة فاتورة مبيعات', 'sales'),
        ('sales.invoices.edit', 'تعديل فاتورة مبيعات', 'sales'),
        ('sales.invoices.delete', 'حذف فاتورة مبيعات', 'sales'),
        ('sales.invoices.cancel', 'إلغاء فاتورة مبيعات', 'sales'),
        
        # Sales - Quotations
        ('sales.quotations', 'عروض الأسعار', 'sales'),
        ('sales.quotations.view', 'عرض عروض الأسعار', 'sales'),
        ('sales.quotations.add', 'إضافة عرض سعر', 'sales'),
        ('sales.quotations.edit', 'تعديل عرض سعر', 'sales'),
        ('sales.quotations.delete', 'حذف عرض سعر', 'sales'),
        
        # Sales - Customers
        ('sales.customers.view', 'عرض العملاء', 'sales'),
        ('sales.customers.add', 'إضافة عميل', 'sales'),
        ('sales.customers.edit', 'تعديل عميل', 'sales'),
        ('sales.customers.delete', 'حذف عميل', 'sales'),
        
        # Purchases - Invoices
        ('purchases.view', 'عرض المشتريات', 'purchases'),
        ('purchases.add', 'إضافة فاتورة مشتريات', 'purchases'),
        ('purchases.edit', 'تعديل فاتورة مشتريات', 'purchases'),
        ('purchases.delete', 'حذف فاتورة مشتريات', 'purchases'),
        ('purchases.cancel', 'إلغاء فاتورة مشتريات', 'purchases'),
        
        # Purchases - Suppliers
        ('purchases.suppliers.view', 'عرض الموردين', 'purchases'),
        ('purchases.suppliers.add', 'إضافة مورد', 'purchases'),
        ('purchases.suppliers.edit', 'تعديل مورد', 'purchases'),
        ('purchases.suppliers.delete', 'حذف مورد', 'purchases'),
        
        # Accounting - Accounts
        ('accounting.view', 'عرض المحاسبة', 'accounting'),
        ('accounting.accounts.view', 'عرض دليل الحسابات', 'accounting'),
        ('accounting.accounts.add', 'إضافة حساب', 'accounting'),
        ('accounting.accounts.edit', 'تعديل حساب', 'accounting'),
        ('accounting.accounts.delete', 'حذف حساب', 'accounting'),
        
        # Accounting - Transactions
        ('accounting.transactions.view', 'عرض القيود اليومية', 'accounting'),
        ('accounting.transactions.create', 'إنشاء قيد يومي', 'accounting'),
        ('accounting.transactions.edit', 'تعديل قيد يومي', 'accounting'),
        ('accounting.transactions.delete', 'حذف قيد يومي', 'accounting'),
        
        # Accounting - Payments
        ('accounting.payments.view', 'عرض المدفوعات', 'accounting'),
        ('accounting.payments.add', 'إضافة مدفوعات', 'accounting'),
        ('accounting.payments.edit', 'تعديل مدفوعات', 'accounting'),
        ('accounting.payments.delete', 'حذف مدفوعات', 'accounting'),
        
        # Accounting - Expenses
        ('accounting.expenses.view', 'عرض المصروفات', 'accounting'),
        ('accounting.expenses.add', 'إضافة مصروف', 'accounting'),
        ('accounting.expenses.create', 'إنشاء مصروف', 'accounting'),
        ('accounting.expenses.edit', 'تعديل مصروف', 'accounting'),
        ('accounting.expenses.delete', 'حذف مصروف', 'accounting'),
        
        # Accounting - Bank Accounts
        ('accounting.bank_accounts.view', 'عرض الحسابات البنكية', 'accounting'),
        ('accounting.bank_accounts.add', 'إضافة حساب بنكي', 'accounting'),
        ('accounting.bank_accounts.edit', 'تعديل حساب بنكي', 'accounting'),
        ('accounting.bank_accounts.delete', 'حذف حساب بنكي', 'accounting'),
        
        # Accounting - Cost Centers
        ('accounting.cost_centers.view', 'عرض مراكز التكلفة', 'accounting'),
        ('accounting.cost_centers.add', 'إضافة مركز تكلفة', 'accounting'),
        ('accounting.cost_centers.edit', 'تعديل مركز تكلفة', 'accounting'),
        ('accounting.cost_centers.delete', 'حذف مركز تكلفة', 'accounting'),
        
        # Accounting - Reports
        ('accounting.reports.view', 'عرض التقارير المحاسبية', 'accounting'),
        ('accounting.reports.trial_balance', 'ميزان المراجعة', 'accounting'),
        ('accounting.reports.income_statement', 'قائمة الدخل', 'accounting'),
        ('accounting.reports.balance_sheet', 'الميزانية العمومية', 'accounting'),
        ('accounting.reports.cash_flow', 'قائمة التدفقات النقدية', 'accounting'),

        # POS - Point of Sale
        ('pos.view', 'عرض نقاط البيع', 'pos'),
        ('pos.sessions.view', 'عرض جلسات البيع', 'pos'),
        ('pos.sessions.open', 'فتح جلسة بيع', 'pos'),
        ('pos.sessions.close', 'إغلاق جلسة بيع', 'pos'),
        ('pos.orders.view', 'عرض طلبات البيع', 'pos'),
        ('pos.orders.create', 'إنشاء طلب بيع', 'pos'),

        # HR - Human Resources
        ('hr.view', 'عرض الموارد البشرية', 'hr'),
        ('hr.employees.view', 'عرض الموظفين', 'hr'),
        ('hr.employees.add', 'إضافة موظف', 'hr'),
        ('hr.employees.edit', 'تعديل موظف', 'hr'),
        ('hr.employees.delete', 'حذف موظف', 'hr'),
        ('hr.departments.view', 'عرض الأقسام', 'hr'),
        ('hr.departments.add', 'إضافة قسم', 'hr'),
        ('hr.departments.edit', 'تعديل قسم', 'hr'),
        ('hr.departments.delete', 'حذف قسم', 'hr'),
        ('hr.attendance.view', 'عرض الحضور', 'hr'),
        ('hr.attendance.add', 'إضافة حضور', 'hr'),
        ('hr.payroll.view', 'عرض الرواتب', 'hr'),
        ('hr.payroll.process', 'معالجة الرواتب', 'hr'),

        # Reports
        ('reports.view', 'عرض التقارير', 'reports'),
        ('reports.sales', 'تقارير المبيعات', 'reports'),
        ('reports.purchases', 'تقارير المشتريات', 'reports'),
        ('reports.inventory', 'تقارير المخزون', 'reports'),
        ('reports.financial', 'التقارير المالية', 'reports'),

        # Settings - Users
        ('settings.view', 'عرض الإعدادات', 'settings'),
        ('settings.users.view', 'عرض المستخدمين', 'settings'),
        ('settings.users.add', 'إضافة مستخدم', 'settings'),
        ('settings.users.edit', 'تعديل مستخدم', 'settings'),
        ('settings.users.delete', 'حذف مستخدم', 'settings'),

        # Settings - Roles
        ('settings.roles.view', 'عرض الأدوار', 'settings'),
        ('settings.roles.add', 'إضافة دور', 'settings'),
        ('settings.roles.edit', 'تعديل دور', 'settings'),
        ('settings.roles.delete', 'حذف دور', 'settings'),
        ('settings.roles.manage', 'إدارة الأدوار', 'settings'),

        # Settings - Permissions
        ('settings.permissions.view', 'عرض الصلاحيات', 'settings'),
        ('settings.permissions.manage', 'إدارة الصلاحيات', 'settings'),

        # Settings - Company
        ('settings.company.view', 'عرض بيانات الشركة', 'settings'),
        ('settings.company.edit', 'تعديل بيانات الشركة', 'settings'),

        # Settings - Branches
        ('settings.branches.view', 'عرض الفروع', 'settings'),
        ('settings.branches.add', 'إضافة فرع', 'settings'),
        ('settings.branches.edit', 'تعديل فرع', 'settings'),
        ('settings.branches.delete', 'حذف فرع', 'settings'),
    ]

    print("⏳ جاري إضافة الصلاحيات...")
    print("⏳ Adding permissions...\n")

    added_count = 0
    existing_count = 0

    for perm_name, perm_name_ar, perm_module in all_permissions:
        # Check if permission already exists
        existing = Permission.query.filter_by(name=perm_name).first()

        if existing:
            existing_count += 1
        else:
            # Add new permission
            new_perm = Permission(
                name=perm_name,
                name_ar=perm_name_ar,
                module=perm_module
            )
            db.session.add(new_perm)
            added_count += 1
            print(f"  ✅ {perm_name_ar} ({perm_name})")

    # Commit all new permissions
    db.session.commit()

    print(f"\n{'=' * 80}")
    print(f"📊 النتائج:")
    print(f"📊 Results:")
    print(f"  ✅ صلاحيات جديدة: {added_count}")
    print(f"  ✅ New permissions: {added_count}")
    print(f"  ℹ️  صلاحيات موجودة مسبقاً: {existing_count}")
    print(f"  ℹ️  Already existing: {existing_count}")
    print(f"  📊 إجمالي الصلاحيات: {Permission.query.count()}")
    print(f"  📊 Total permissions: {Permission.query.count()}")

    # Assign all permissions to admin role
    print(f"\n{'=' * 80}")
    print("🔧 ربط جميع الصلاحيات بدور admin...")
    print("🔧 Assigning all permissions to admin role...")

    admin_role = Role.query.filter_by(name='admin').first()

    if admin_role:
        all_perms = Permission.query.all()
        admin_role.permissions = all_perms
        db.session.commit()

        print(f"  ✅ تم ربط {len(all_perms)} صلاحية بدور admin")
        print(f"  ✅ Assigned {len(all_perms)} permissions to admin role")
    else:
        print("  ❌ دور admin غير موجود!")
        print("  ❌ Admin role not found!")

    print(f"\n{'=' * 80}")
    print("✅ تم الانتهاء بنجاح!")
    print("✅ Completed successfully!")
    print(f"{'=' * 80}\n")

