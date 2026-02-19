"""
Test Permissions System
اختبار نظام الصلاحيات
"""
import os
os.environ['FLASK_ENV'] = 'development'

from run import app, db
from app.models import User, Role, Permission, RolePermission

print("=" * 80)
print("🧪 Testing Permissions System")
print("🧪 اختبار نظام الصلاحيات")
print("=" * 80)

with app.app_context():
    # Test 1: Check permissions count
    print("\n📋 Test 1: Checking permissions...")
    perm_count = Permission.query.count()
    print(f"   Total permissions: {perm_count}")
    
    if perm_count > 0:
        print("   ✅ Permissions exist")
        
        # Show permissions by module
        modules = db.session.query(Permission.module).distinct().all()
        print(f"\n   Permissions by module:")
        for (module,) in modules:
            count = Permission.query.filter_by(module=module).count()
            print(f"      - {module}: {count} permissions")
    else:
        print("   ❌ No permissions found!")
    
    # Test 2: Check roles
    print("\n📋 Test 2: Checking roles...")
    roles = Role.query.all()
    print(f"   Total roles: {len(roles)}")
    
    for role in roles:
        perm_count = len(role.permissions)
        user_count = len(role.users)
        print(f"\n   Role: {role.name} ({role.name_ar})")
        print(f"      - Permissions: {perm_count}")
        print(f"      - Users: {user_count}")
    
    # Test 3: Check users
    print("\n📋 Test 3: Checking users...")
    users = User.query.all()
    print(f"   Total users: {len(users)}")
    
    for user in users:
        print(f"\n   User: {user.username}")
        print(f"      - Full Name: {user.full_name or 'N/A'}")
        print(f"      - Email: {user.email}")
        print(f"      - Is Admin: {user.is_admin}")
        print(f"      - Is Active: {user.is_active}")
        print(f"      - Role: {user.role.name if user.role else 'None'}")
        
        # Test specific permissions
        test_perms = [
            'dashboard.view',
            'sales.invoices.view',
            'sales.invoices.add',
            'purchases.confirm',
            'settings.users.manage'
        ]
        
        print(f"      - Permission Tests:")
        for perm in test_perms:
            has_perm = user.has_permission(perm)
            status = "✅" if has_perm else "❌"
            print(f"         {status} {perm}")
    
    # Test 4: Create a test role
    print("\n📋 Test 4: Creating test role...")
    test_role = Role.query.filter_by(name='test_cashier').first()
    
    if test_role:
        print("   ⚠️ Test role already exists, deleting...")
        RolePermission.query.filter_by(role_id=test_role.id).delete()
        db.session.delete(test_role)
        db.session.commit()
    
    # Create new test role
    test_role = Role(
        name='test_cashier',
        name_ar='كاشير تجريبي',
        description='Test cashier role with limited permissions',
        description_en='Test cashier role with limited permissions'
    )
    db.session.add(test_role)
    db.session.commit()
    print(f"   ✅ Created test role: {test_role.name}")
    
    # Assign limited permissions
    cashier_perms = [
        'dashboard.view',
        'pos.access',
        'pos.sell',
        'sales.invoices.view',
        'sales.customers.view'
    ]
    
    assigned_count = 0
    for perm_name in cashier_perms:
        perm = Permission.query.filter_by(name=perm_name).first()
        if perm:
            role_perm = RolePermission(
                role_id=test_role.id,
                permission_id=perm.id
            )
            db.session.add(role_perm)
            assigned_count += 1
    
    db.session.commit()
    print(f"   ✅ Assigned {assigned_count} permissions to test role")
    
    # Test 5: Create a test user
    print("\n📋 Test 5: Creating test user...")
    test_user = User.query.filter_by(username='test_cashier').first()
    
    if test_user:
        print("   ⚠️ Test user already exists, deleting...")
        db.session.delete(test_user)
        db.session.commit()
    
    # Create new test user
    test_user = User(
        username='test_cashier',
        email='cashier@test.com',
        full_name='Test Cashier',
        is_active=True,
        is_admin=False,
        role_id=test_role.id
    )
    test_user.set_password('123456')
    db.session.add(test_user)
    db.session.commit()
    print(f"   ✅ Created test user: {test_user.username}")
    print(f"      - Password: 123456")
    print(f"      - Role: {test_user.role.name}")
    
    # Test permissions
    print(f"\n   Testing permissions for test_cashier:")
    for perm in cashier_perms:
        has_perm = test_user.has_permission(perm)
        status = "✅" if has_perm else "❌"
        print(f"      {status} {perm}")
    
    # Test denied permissions
    denied_perms = [
        'sales.invoices.add',
        'sales.invoices.delete',
        'inventory.products.edit',
        'settings.users.manage'
    ]
    
    print(f"\n   Testing DENIED permissions (should all be ❌):")
    for perm in denied_perms:
        has_perm = test_user.has_permission(perm)
        status = "❌" if not has_perm else "⚠️ SHOULD BE DENIED!"
        print(f"      {status} {perm}")

print("\n" + "=" * 80)
print("✅ Permissions System Test Complete!")
print("✅ اكتمل اختبار نظام الصلاحيات!")
print("=" * 80)
print("\n📝 Test Results:")
print("   ✅ Created test role: 'test_cashier'")
print("   ✅ Created test user: 'test_cashier' (password: 123456)")
print("   ✅ Assigned 5 permissions to the role")
print("\n🎯 Next Steps:")
print("   1. Login as 'test_cashier' with password '123456'")
print("   2. Try to access different pages")
print("   3. Verify that only allowed pages are accessible")
print("   4. Go to Settings → Users to manage users")
print("   5. Go to Settings → Roles to manage roles and permissions")
print("=" * 80)

