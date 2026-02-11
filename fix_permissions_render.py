"""
Fix permissions on Render deployment
إصلاح الصلاحيات على Render
"""
import os
os.environ['FLASK_ENV'] = 'production'

from run import app, db
from app.models import User, Role, Permission

print("=" * 80)
print("🔧 إصلاح الصلاحيات على Render")
print("🔧 Fixing permissions on Render")
print("=" * 80)

with app.app_context():
    # Check if permissions exist
    perm_count = Permission.query.count()
    print(f"\n📋 عدد الصلاحيات الحالية: {perm_count}")
    print(f"📋 Current permissions count: {perm_count}")
    
    if perm_count == 0:
        print("\n⚠️ لا توجد صلاحيات! سيتم إنشاؤها الآن...")
        print("⚠️ No permissions found! Creating them now...")
        
        # Create all permissions
        permissions = [
            # Dashboard
            Permission(name='dashboard.view', name_ar='عرض لوحة التحكم', module='main'),
            
            # Inventory
            Permission(name='inventory.view', name_ar='عرض المخزون', module='inventory'),
            Permission(name='inventory.stock.view', name_ar='عرض المخزون', module='inventory'),
            Permission(name='inventory.stock.add', name_ar='إضافة مخزون', module='inventory'),
            Permission(name='inventory.stock.edit', name_ar='تعديل مخزون', module='inventory'),
            Permission(name='inventory.stock.delete', name_ar='حذف مخزون', module='inventory'),
            Permission(name='inventory.products.view', name_ar='عرض المنتجات', module='inventory'),
            Permission(name='inventory.products.add', name_ar='إضافة منتج', module='inventory'),
            Permission(name='inventory.products.edit', name_ar='تعديل منتج', module='inventory'),
            Permission(name='inventory.products.delete', name_ar='حذف منتج', module='inventory'),
            Permission(name='inventory.damaged.view', name_ar='عرض المخزون التالف', module='inventory'),
            Permission(name='inventory.damaged.add', name_ar='إضافة مخزون تالف', module='inventory'),
            Permission(name='inventory.damaged.edit', name_ar='تعديل مخزون تالف', module='inventory'),
            Permission(name='inventory.damaged.delete', name_ar='حذف مخزون تالف', module='inventory'),
            
            # Sales
            Permission(name='sales.view', name_ar='عرض المبيعات', module='sales'),
            Permission(name='sales.invoices.view', name_ar='عرض فواتير المبيعات', module='sales'),
            Permission(name='sales.invoices.add', name_ar='إضافة فاتورة مبيعات', module='sales'),
            Permission(name='sales.invoices.edit', name_ar='تعديل فاتورة مبيعات', module='sales'),
            Permission(name='sales.invoices.delete', name_ar='حذف فاتورة مبيعات', module='sales'),
            Permission(name='sales.customers.view', name_ar='عرض العملاء', module='sales'),
            Permission(name='sales.customers.add', name_ar='إضافة عميل', module='sales'),
            Permission(name='sales.customers.edit', name_ar='تعديل عميل', module='sales'),
            Permission(name='sales.customers.delete', name_ar='حذف عميل', module='sales'),
            
            # Purchases
            Permission(name='purchases.view', name_ar='عرض المشتريات', module='purchases'),
            Permission(name='purchases.invoices.view', name_ar='عرض فواتير المشتريات', module='purchases'),
            Permission(name='purchases.invoices.add', name_ar='إضافة فاتورة مشتريات', module='purchases'),
            Permission(name='purchases.invoices.edit', name_ar='تعديل فاتورة مشتريات', module='purchases'),
            Permission(name='purchases.invoices.delete', name_ar='حذف فاتورة مشتريات', module='purchases'),
            Permission(name='purchases.suppliers.view', name_ar='عرض الموردين', module='purchases'),
            Permission(name='purchases.suppliers.add', name_ar='إضافة مورد', module='purchases'),
            Permission(name='purchases.suppliers.edit', name_ar='تعديل مورد', module='purchases'),
            Permission(name='purchases.suppliers.delete', name_ar='حذف مورد', module='purchases'),
            
            # Accounting
            Permission(name='accounting.view', name_ar='عرض المحاسبة', module='accounting'),
            Permission(name='accounting.accounts.view', name_ar='عرض الحسابات', module='accounting'),
            Permission(name='accounting.accounts.add', name_ar='إضافة حساب', module='accounting'),
            Permission(name='accounting.accounts.edit', name_ar='تعديل حساب', module='accounting'),
            Permission(name='accounting.accounts.delete', name_ar='حذف حساب', module='accounting'),
            Permission(name='accounting.entries.view', name_ar='عرض القيود', module='accounting'),
            Permission(name='accounting.entries.add', name_ar='إضافة قيد', module='accounting'),
            Permission(name='accounting.entries.edit', name_ar='تعديل قيد', module='accounting'),
            Permission(name='accounting.entries.delete', name_ar='حذف قيد', module='accounting'),
            
            # Reports
            Permission(name='reports.view', name_ar='عرض التقارير', module='reports'),
            Permission(name='reports.sales', name_ar='تقارير المبيعات', module='reports'),
            Permission(name='reports.purchases', name_ar='تقارير المشتريات', module='reports'),
            Permission(name='reports.inventory', name_ar='تقارير المخزون', module='reports'),
            Permission(name='reports.accounting', name_ar='تقارير المحاسبة', module='reports'),
            
            # Settings
            Permission(name='settings.view', name_ar='عرض الإعدادات', module='settings'),
            Permission(name='settings.company.edit', name_ar='تعديل بيانات الشركة', module='settings'),
            Permission(name='settings.branches.manage', name_ar='إدارة الفروع', module='settings'),
            Permission(name='settings.users.manage', name_ar='إدارة المستخدمين', module='settings'),
            Permission(name='settings.roles.manage', name_ar='إدارة الأدوار', module='settings'),
            Permission(name='settings.permissions.manage', name_ar='إدارة الصلاحيات', module='settings'),
        ]
        
        db.session.add_all(permissions)
        db.session.commit()
        print(f"✅ تم إنشاء {len(permissions)} صلاحية")
        print(f"✅ Created {len(permissions)} permissions")
        
        # Assign all permissions to admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            admin_role.permissions = permissions
            db.session.commit()
            print("✅ تم ربط جميع الصلاحيات بدور المدير")
            print("✅ Assigned all permissions to admin role")
    else:
        print("✅ الصلاحيات موجودة بالفعل")
        print("✅ Permissions already exist")
    
    # Check admin user
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"\n👤 المستخدم admin:")
        print(f"   - is_admin: {admin.is_admin}")
        print(f"   - role_id: {admin.role_id}")
        print(f"   - role: {admin.role.name if admin.role else 'None'}")
        
        if admin.role:
            print(f"   - عدد الصلاحيات: {len(admin.role.permissions)}")
            print(f"   - permissions count: {len(admin.role.permissions)}")
        
        # Test permission
        has_dashboard = admin.has_permission('dashboard.view')
        print(f"\n🔍 اختبار الصلاحية:")
        print(f"   - has_permission('dashboard.view'): {has_dashboard}")
        
        if not has_dashboard and not admin.is_admin:
            print("\n⚠️ المستخدم admin ليس لديه صلاحيات!")
            print("⚠️ Admin user doesn't have permissions!")
            print("🔧 سيتم تفعيل is_admin...")
            admin.is_admin = True
            db.session.commit()
            print("✅ تم تفعيل is_admin للمستخدم admin")
    else:
        print("\n❌ المستخدم admin غير موجود!")

print("\n" + "=" * 80)
print("✅ تم الانتهاء!")
print("✅ Done!")
print("=" * 80)

