"""
Setup and verify permissions system
إعداد والتحقق من نظام الصلاحيات
"""
import os
os.environ['FLASK_ENV'] = 'development'

from run import app, db
from app.models import User, Role, Permission, RolePermission

print("=" * 80)
print("🔧 Setting Up Permissions System")
print("🔧 إعداد نظام الصلاحيات")
print("=" * 80)

with app.app_context():
    # Step 1: Check existing permissions
    print("\n📋 Step 1: Checking existing permissions...")
    perm_count = Permission.query.count()
    print(f"   Current permissions count: {perm_count}")
    
    if perm_count == 0:
        print("   ⚠️ No permissions found! Creating default permissions...")
        
        # Create default permissions
        default_permissions = [
            # Dashboard
            ('dashboard.view', 'View Dashboard', 'عرض لوحة التحكم', 'main'),
            
            # Inventory
            ('inventory.products.view', 'View Products', 'عرض المنتجات', 'inventory'),
            ('inventory.products.add', 'Add Products', 'إضافة منتجات', 'inventory'),
            ('inventory.products.edit', 'Edit Products', 'تعديل منتجات', 'inventory'),
            ('inventory.products.delete', 'Delete Products', 'حذف منتجات', 'inventory'),
            ('inventory.stock.view', 'View Stock', 'عرض المخزون', 'inventory'),
            ('inventory.stock.manage', 'Manage Stock', 'إدارة المخزون', 'inventory'),
            
            # Sales
            ('sales.invoices.view', 'View Sales Invoices', 'عرض فواتير المبيعات', 'sales'),
            ('sales.invoices.add', 'Add Sales Invoices', 'إضافة فواتير مبيعات', 'sales'),
            ('sales.invoices.edit', 'Edit Sales Invoices', 'تعديل فواتير مبيعات', 'sales'),
            ('sales.invoices.delete', 'Delete Sales Invoices', 'حذف فواتير مبيعات', 'sales'),
            ('sales.customers.view', 'View Customers', 'عرض العملاء', 'sales'),
            ('sales.customers.manage', 'Manage Customers', 'إدارة العملاء', 'sales'),
            
            # Purchases
            ('purchases.invoices.view', 'View Purchase Invoices', 'عرض فواتير المشتريات', 'purchases'),
            ('purchases.invoices.add', 'Add Purchase Invoices', 'إضافة فواتير مشتريات', 'purchases'),
            ('purchases.invoices.edit', 'Edit Purchase Invoices', 'تعديل فواتير مشتريات', 'purchases'),
            ('purchases.invoices.delete', 'Delete Purchase Invoices', 'حذف فواتير مشتريات', 'purchases'),
            ('purchases.suppliers.view', 'View Suppliers', 'عرض الموردين', 'purchases'),
            ('purchases.suppliers.manage', 'Manage Suppliers', 'إدارة الموردين', 'purchases'),
            ('purchases.confirm', 'Confirm Purchase Invoices', 'تأكيد فواتير المشتريات', 'purchases'),
            ('purchases.cancel', 'Cancel Purchase Invoices', 'إلغاء فواتير المشتريات', 'purchases'),
            
            # Accounting
            ('accounting.view', 'View Accounting', 'عرض المحاسبة', 'accounting'),
            ('accounting.manage', 'Manage Accounting', 'إدارة المحاسبة', 'accounting'),
            ('accounting.payments.view', 'View Payments', 'عرض المدفوعات', 'accounting'),
            ('accounting.payments.manage', 'Manage Payments', 'إدارة المدفوعات', 'accounting'),
            
            # Reports
            ('reports.view', 'View Reports', 'عرض التقارير', 'reports'),
            ('reports.inventory', 'Inventory Reports', 'تقارير المخزون', 'reports'),
            ('reports.sales', 'Sales Reports', 'تقارير المبيعات', 'reports'),
            ('reports.purchases', 'Purchase Reports', 'تقارير المشتريات', 'reports'),
            ('reports.financial', 'Financial Reports', 'التقارير المالية', 'reports'),
            
            # POS
            ('pos.access', 'Access POS', 'الوصول لنقطة البيع', 'pos'),
            ('pos.sell', 'Sell Products', 'بيع المنتجات', 'pos'),
            
            # Settings
            ('settings.view', 'View Settings', 'عرض الإعدادات', 'settings'),
            ('settings.company', 'Manage Company Settings', 'إدارة إعدادات الشركة', 'settings'),
            ('settings.users.view', 'View Users', 'عرض المستخدمين', 'settings'),
            ('settings.users.manage', 'Manage Users', 'إدارة المستخدمين', 'settings'),
            ('settings.roles.view', 'View Roles', 'عرض الأدوار', 'settings'),
            ('settings.roles.manage', 'Manage Roles', 'إدارة الأدوار', 'settings'),
            ('settings.permissions.manage', 'Manage Permissions', 'إدارة الصلاحيات', 'settings'),
        ]
        
        for perm_data in default_permissions:
            perm = Permission(
                name=perm_data[0],
                name_ar=perm_data[2],
                module=perm_data[3]
            )
            db.session.add(perm)
        
        db.session.commit()
        print(f"   ✅ Created {len(default_permissions)} permissions")
    else:
        print(f"   ✅ Found {perm_count} existing permissions")
    
    # Step 2: Check/Create admin role
    print("\n📋 Step 2: Checking admin role...")
    admin_role = Role.query.filter_by(name='admin').first()
    
    if not admin_role:
        print("   ⚠️ Admin role not found! Creating...")
        admin_role = Role(
            name='admin',
            name_ar='مدير النظام',
            description='Full system access',
            description_en='Full system access'
        )
        db.session.add(admin_role)
        db.session.commit()
        print("   ✅ Created admin role")
    else:
        print(f"   ✅ Found admin role (ID: {admin_role.id})")
    
    # Step 3: Assign all permissions to admin role
    print("\n📋 Step 3: Assigning permissions to admin role...")
    all_permissions = Permission.query.all()
    current_perms = len(admin_role.permissions)
    
    if current_perms < len(all_permissions):
        print(f"   ⚠️ Admin role has only {current_perms}/{len(all_permissions)} permissions")
        print("   🔧 Assigning all permissions...")
        
        # Clear existing
        RolePermission.query.filter_by(role_id=admin_role.id).delete()
        
        # Add all permissions
        for perm in all_permissions:
            role_perm = RolePermission(
                role_id=admin_role.id,
                permission_id=perm.id
            )
            db.session.add(role_perm)
        
        db.session.commit()
        print(f"   ✅ Assigned all {len(all_permissions)} permissions to admin role")
    else:
        print(f"   ✅ Admin role already has all {current_perms} permissions")
    
    # Step 4: Check users
    print("\n📋 Step 4: Checking users...")
    users = User.query.all()
    print(f"   Found {len(users)} users:")
    
    for user in users:
        print(f"\n   User: {user.username}")
        print(f"      - is_admin: {user.is_admin}")
        print(f"      - role: {user.role.name if user.role else 'None'}")
        print(f"      - is_active: {user.is_active}")
        
        # Make sure admin users have admin role
        if user.is_admin and (not user.role or user.role.name != 'admin'):
            print(f"      ⚠️ Admin user doesn't have admin role! Fixing...")
            user.role_id = admin_role.id
            db.session.commit()
            print(f"      ✅ Assigned admin role")

print("\n" + "=" * 80)
print("✅ Permissions System Setup Complete!")
print("✅ اكتمل إعداد نظام الصلاحيات!")
print("=" * 80)
print("\n📝 Next Steps:")
print("   1. Go to: Settings → Users")
print("   2. Create/Edit users and assign roles")
print("   3. Go to: Settings → Roles")
print("   4. Create custom roles with specific permissions")
print("\n   1. اذهب إلى: الإعدادات → المستخدمين")
print("   2. أنشئ/عدل المستخدمين وعين الأدوار")
print("   3. اذهب إلى: الإعدادات → الأدوار")
print("   4. أنشئ أدوار مخصصة بصلاحيات محددة")
print("=" * 80)

