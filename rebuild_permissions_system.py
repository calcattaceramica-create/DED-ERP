#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
إعادة بناء نظام الصلاحيات بالكامل
Rebuild permissions system from scratch
"""

from app import create_app, db
from app.models import Permission, Role, RolePermission, User

app = create_app()

# قائمة شاملة بجميع الصلاحيات في النظام
ALL_PERMISSIONS = [
    # Dashboard - لوحة التحكم
    ('dashboard.view', 'عرض لوحة التحكم', 'main'),
    
    # Accounting - المحاسبة
    ('accounting.view', 'عرض المحاسبة', 'accounting'),
    ('accounting.accounts.view', 'عرض الحسابات', 'accounting'),
    ('accounting.accounts.add', 'إضافة حساب', 'accounting'),
    ('accounting.accounts.edit', 'تعديل حساب', 'accounting'),
    ('accounting.accounts.delete', 'حذف حساب', 'accounting'),
    ('accounting.bank_accounts.view', 'عرض الحسابات البنكية', 'accounting'),
    ('accounting.transactions.view', 'عرض القيود اليومية', 'accounting'),
    ('accounting.transactions.create', 'إنشاء قيد يومي', 'accounting'),
    ('accounting.transactions.edit', 'تعديل قيد يومي', 'accounting'),
    ('accounting.transactions.delete', 'حذف قيد يومي', 'accounting'),
    ('accounting.payments.view', 'عرض المدفوعات', 'accounting'),
    ('accounting.payments.add', 'إضافة مدفوعة', 'accounting'),
    ('accounting.payments.edit', 'تعديل مدفوعة', 'accounting'),
    ('accounting.payments.delete', 'حذف مدفوعة', 'accounting'),
    ('accounting.expenses.view', 'عرض المصروفات', 'accounting'),
    ('accounting.expenses.add', 'إضافة مصروف', 'accounting'),
    ('accounting.expenses.create', 'إنشاء مصروف', 'accounting'),
    ('accounting.expenses.edit', 'تعديل مصروف', 'accounting'),
    ('accounting.expenses.delete', 'حذف مصروف', 'accounting'),
    ('accounting.cost_centers.view', 'عرض مراكز التكلفة', 'accounting'),
    ('accounting.cost_centers.add', 'إضافة مركز تكلفة', 'accounting'),
    ('accounting.cost_centers.edit', 'تعديل مركز تكلفة', 'accounting'),
    ('accounting.cost_centers.delete', 'حذف مركز تكلفة', 'accounting'),
    ('accounting.reports.view', 'عرض التقارير المحاسبية', 'accounting'),
    ('accounting.reports.trial_balance', 'ميزان المراجعة', 'accounting'),
    ('accounting.reports.income_statement', 'قائمة الدخل', 'accounting'),
    ('accounting.reports.balance_sheet', 'الميزانية العمومية', 'accounting'),
    ('accounting.reports.cash_flow', 'قائمة التدفقات النقدية', 'accounting'),
    
    # Inventory - المخزون
    ('inventory.view', 'عرض المخزون', 'inventory'),
    ('inventory.products.view', 'عرض المنتجات', 'inventory'),
    ('inventory.products.add', 'إضافة منتج', 'inventory'),
    ('inventory.products.edit', 'تعديل منتج', 'inventory'),
    ('inventory.products.delete', 'حذف منتج', 'inventory'),
    ('inventory.categories.view', 'عرض الفئات', 'inventory'),
    ('inventory.categories.add', 'إضافة فئة', 'inventory'),
    ('inventory.categories.edit', 'تعديل فئة', 'inventory'),
    ('inventory.categories.delete', 'حذف فئة', 'inventory'),
    ('inventory.categories.manage', 'إدارة الفئات', 'inventory'),
    ('inventory.warehouses.view', 'عرض المستودعات', 'inventory'),
    ('inventory.warehouses.add', 'إضافة مستودع', 'inventory'),
    ('inventory.warehouses.edit', 'تعديل مستودع', 'inventory'),
    ('inventory.warehouses.delete', 'حذف مستودع', 'inventory'),
    ('inventory.stock.view', 'عرض المخزون', 'inventory'),
    ('inventory.stock.add', 'إضافة مخزون', 'inventory'),
    ('inventory.stock.edit', 'تعديل مخزون', 'inventory'),
    ('inventory.stock.transfer', 'نقل مخزون', 'inventory'),
    ('inventory.damaged.view', 'عرض التالف', 'inventory'),
    ('inventory.damaged.add', 'إضافة تالف', 'inventory'),
    ('inventory.damaged.edit', 'تعديل تالف', 'inventory'),
    ('inventory.damaged.delete', 'حذف تالف', 'inventory'),
    
    # Sales - المبيعات
    ('sales.view', 'عرض المبيعات', 'sales'),
    ('sales.invoices.view', 'عرض الفواتير', 'sales'),
    ('sales.invoices.add', 'إضافة فاتورة', 'sales'),
    ('sales.invoices.edit', 'تعديل فاتورة', 'sales'),
    ('sales.invoices.delete', 'حذف فاتورة', 'sales'),
    ('sales.invoices.cancel', 'إلغاء فاتورة', 'sales'),
    ('sales.invoices.confirm', 'تأكيد فاتورة', 'sales'),
    ('sales.invoices.complete', 'إكمال فاتورة', 'sales'),
    ('sales.quotations.view', 'عرض عروض الأسعار', 'sales'),
    ('sales.quotations', 'عروض الأسعار', 'sales'),
    ('sales.quotations.add', 'إضافة عرض سعر', 'sales'),
    ('sales.quotations.edit', 'تعديل عرض سعر', 'sales'),
    ('sales.quotations.delete', 'حذف عرض سعر', 'sales'),
    ('sales.quotations.convert', 'تحويل عرض سعر لفاتورة', 'sales'),
    ('sales.customers.view', 'عرض العملاء', 'sales'),
    ('sales.customers.add', 'إضافة عميل', 'sales'),
    ('sales.customers.edit', 'تعديل عميل', 'sales'),
    ('sales.customers.delete', 'حذف عميل', 'sales'),
    
    # Purchases - المشتريات
    ('purchases.view', 'عرض المشتريات', 'purchases'),
    ('purchases.orders.view', 'عرض طلبات الشراء', 'purchases'),
    ('purchases.orders.add', 'إضافة طلب شراء', 'purchases'),
    ('purchases.orders.edit', 'تعديل طلب شراء', 'purchases'),
    ('purchases.orders.delete', 'حذف طلب شراء', 'purchases'),
    ('purchases.invoices.view', 'عرض فواتير الشراء', 'purchases'),
    ('purchases.invoices.add', 'إضافة فاتورة شراء', 'purchases'),
    ('purchases.invoices.confirm', 'تأكيد فاتورة شراء', 'purchases'),
    ('purchases.invoices.cancel', 'إلغاء فاتورة شراء', 'purchases'),
    ('purchases.invoices.delete', 'حذف فاتورة شراء', 'purchases'),
    ('purchases.suppliers.view', 'عرض الموردين', 'purchases'),
    ('purchases.suppliers.add', 'إضافة مورد', 'purchases'),
    ('purchases.suppliers.edit', 'تعديل مورد', 'purchases'),
    ('purchases.suppliers.delete', 'حذف مورد', 'purchases'),
    
    # POS - نقطة البيع
    ('pos.view', 'عرض نقاط البيع', 'pos'),
    ('pos.access', 'الوصول لنقطة البيع', 'pos'),
    ('pos.sessions.view', 'عرض جلسات البيع', 'pos'),
    ('pos.sessions.open', 'فتح جلسة بيع', 'pos'),
    ('pos.sessions.close', 'إغلاق جلسة بيع', 'pos'),
    ('pos.orders.view', 'عرض طلبات البيع', 'pos'),
    ('pos.orders.create', 'إنشاء طلب بيع', 'pos'),
    
    # HR - الموارد البشرية
    ('hr.view', 'عرض الموارد البشرية', 'hr'),
    ('hr.employees.view', 'عرض الموظفين', 'hr'),
    ('hr.employees.add', 'إضافة موظف', 'hr'),
    ('hr.employees.edit', 'تعديل موظف', 'hr'),
    ('hr.employees.delete', 'حذف موظف', 'hr'),
    ('hr.departments.view', 'عرض الأقسام', 'hr'),
    ('hr.departments.add', 'إضافة قسم', 'hr'),
    ('hr.departments.edit', 'تعديل قسم', 'hr'),
    ('hr.departments.delete', 'حذف قسم', 'hr'),
    ('hr.positions.view', 'عرض الوظائف', 'hr'),
    ('hr.positions.add', 'إضافة وظيفة', 'hr'),
    ('hr.positions.edit', 'تعديل وظيفة', 'hr'),
    ('hr.positions.delete', 'حذف وظيفة', 'hr'),
    ('hr.attendance.view', 'عرض الحضور', 'hr'),
    ('hr.attendance.add', 'إضافة حضور', 'hr'),
    ('hr.leaves.view', 'عرض الإجازات', 'hr'),
    ('hr.leaves.add', 'إضافة إجازة', 'hr'),
    ('hr.leaves.approve', 'الموافقة على إجازة', 'hr'),
    ('hr.leaves.reject', 'رفض إجازة', 'hr'),
    ('hr.leave_types.view', 'عرض أنواع الإجازات', 'hr'),
    ('hr.leave_types.add', 'إضافة نوع إجازة', 'hr'),
    ('hr.payroll.view', 'عرض الرواتب', 'hr'),
    ('hr.payroll.generate', 'إنشاء الرواتب', 'hr'),
    ('hr.payroll.approve', 'الموافقة على الرواتب', 'hr'),
    ('hr.payroll.pay', 'دفع الرواتب', 'hr'),
    ('hr.payroll.process', 'معالجة الرواتب', 'hr'),
    
    # Reports - التقارير
    ('reports.view', 'عرض التقارير', 'reports'),
    ('reports.sales', 'تقارير المبيعات', 'reports'),
    ('reports.purchases', 'تقارير المشتريات', 'reports'),
    ('reports.inventory', 'تقارير المخزون', 'reports'),
    ('reports.financial', 'التقارير المالية', 'reports'),
    
    # Settings - الإعدادات
    ('settings.view', 'عرض الإعدادات', 'settings'),
    ('settings.manage', 'إدارة الإعدادات', 'settings'),
    ('settings.users.view', 'عرض المستخدمين', 'settings'),
    ('settings.users.add', 'إضافة مستخدم', 'settings'),
    ('settings.users.edit', 'تعديل مستخدم', 'settings'),
    ('settings.users.delete', 'حذف مستخدم', 'settings'),
    ('settings.roles.view', 'عرض الأدوار', 'settings'),
    ('settings.roles.add', 'إضافة دور', 'settings'),
    ('settings.roles.edit', 'تعديل دور', 'settings'),
    ('settings.roles.delete', 'حذف دور', 'settings'),
    ('settings.permissions.view', 'عرض الصلاحيات', 'settings'),
    ('settings.permissions.add', 'إضافة صلاحية', 'settings'),
    ('settings.permissions.manage', 'إدارة الصلاحيات', 'settings'),
    ('settings.company.view', 'عرض بيانات الشركة', 'settings'),
    ('settings.company.edit', 'تعديل بيانات الشركة', 'settings'),
    ('settings.branches.view', 'عرض الفروع', 'settings'),
    ('settings.branches.add', 'إضافة فرع', 'settings'),
    ('settings.branches.edit', 'تعديل فرع', 'settings'),
    ('settings.branches.delete', 'حذف فرع', 'settings'),
]

with app.app_context():
    print("\n" + "="*80)
    print("🔄 إعادة بناء نظام الصلاحيات بالكامل")
    print("🔄 Rebuilding Permissions System")
    print("="*80)

    # Step 1: حذف جميع الصلاحيات القديمة
    print("\n📋 الخطوة 1: حذف الصلاحيات القديمة...")
    old_count = Permission.query.count()
    print(f"   عدد الصلاحيات القديمة: {old_count}")

    # حذف العلاقات أولاً
    RolePermission.query.delete()
    db.session.commit()
    print("   ✅ تم حذف جميع علاقات الأدوار والصلاحيات")

    # حذف الصلاحيات
    Permission.query.delete()
    db.session.commit()
    print("   ✅ تم حذف جميع الصلاحيات القديمة")

    # Step 2: إنشاء الصلاحيات الجديدة
    print("\n📋 الخطوة 2: إنشاء الصلاحيات الجديدة...")
    created_count = 0

    for perm_name, perm_name_ar, module in ALL_PERMISSIONS:
        perm = Permission(
            name=perm_name,
            name_ar=perm_name_ar,
            module=module
        )
        db.session.add(perm)
        created_count += 1

    db.session.commit()
    print(f"   ✅ تم إنشاء {created_count} صلاحية جديدة")

    # Step 3: تعيين الصلاحيات للأدوار
    print("\n📋 الخطوة 3: تعيين الصلاحيات للأدوار...")

    # Get all roles
    admin_role = Role.query.filter_by(name='admin').first()
    manager_role = Role.query.filter_by(name='manager').first()

    if not admin_role:
        print("   ⚠️ دور admin غير موجود - سيتم إنشاؤه")
        admin_role = Role(
            name='admin',
            name_ar='مدير النظام',
            description='Full system access',
            description_en='Full system access'
        )
        db.session.add(admin_role)
        db.session.commit()

    if not manager_role:
        print("   ⚠️ دور manager غير موجود - سيتم إنشاؤه")
        manager_role = Role(
            name='manager',
            name_ar='مدير',
            description='Manager with most permissions',
            description_en='Manager with most permissions'
        )
        db.session.add(manager_role)
        db.session.commit()

    # إعطاء جميع الصلاحيات لدور admin
    all_permissions = Permission.query.all()
    print(f"\n   👤 دور admin:")
    for perm in all_permissions:
        role_perm = RolePermission(
            role_id=admin_role.id,
            permission_id=perm.id
        )
        db.session.add(role_perm)
    db.session.commit()
    print(f"      ✅ تم إضافة {len(all_permissions)} صلاحية")

    # إعطاء معظم الصلاحيات لدور manager (ما عدا بعض صلاحيات الإعدادات الحساسة)
    print(f"\n   👤 دور manager:")
    manager_excluded = [
        'settings.users.delete',
        'settings.roles.delete',
    ]

    manager_count = 0
    for perm in all_permissions:
        if perm.name not in manager_excluded:
            role_perm = RolePermission(
                role_id=manager_role.id,
                permission_id=perm.id
            )
            db.session.add(role_perm)
            manager_count += 1

    db.session.commit()
    print(f"      ✅ تم إضافة {manager_count} صلاحية")

    # Step 4: التحقق من المستخدمين
    print("\n📋 الخطوة 4: التحقق من المستخدمين...")

    users = User.query.all()
    for user in users:
        print(f"\n   👤 {user.username}:")
        print(f"      - الاسم: {user.full_name}")
        print(f"      - is_admin: {user.is_admin}")
        print(f"      - الدور: {user.role.name_ar if user.role else 'لا يوجد'}")

        if user.role:
            perm_count = len(user.role.permissions)
            print(f"      - عدد الصلاحيات: {perm_count}")

    print("\n" + "="*80)
    print("✅ تم إعادة بناء نظام الصلاحيات بنجاح!")
    print("✅ Permissions System Rebuilt Successfully!")
    print("="*80)

    print("\n📊 الإحصائيات النهائية:")
    print(f"   - إجمالي الصلاحيات: {Permission.query.count()}")
    print(f"   - إجمالي الأدوار: {Role.query.count()}")
    print(f"   - إجمالي المستخدمين: {User.query.count()}")
    print(f"   - صلاحيات دور admin: {len(admin_role.permissions)}")
    print(f"   - صلاحيات دور manager: {len(manager_role.permissions)}")

    print("\n" + "="*80)

