"""
Test route permissions - اختبار صلاحيات الـ routes
تأكد من أن جميع الـ routes محمية بالصلاحيات الصحيحة
"""
from run import app, db
from app.models import User, Role, Permission, RolePermission

print("=" * 80)
print("🔍 اختبار صلاحيات الـ Routes")
print("🔍 Testing Route Permissions")
print("=" * 80)

with app.app_context():
    # Create a test user with limited permissions
    print("\n📋 الخطوة 1: إنشاء مستخدم تجريبي محدود الصلاحيات...")
    print("📋 Step 1: Creating test user with limited permissions...")
    
    # Check if test_limited user exists
    test_user = User.query.filter_by(username='test_limited').first()
    
    if test_user:
        print("   ℹ️  المستخدم test_limited موجود بالفعل")
        print("   ℹ️  User test_limited already exists")
    else:
        # Create test role with only view permissions
        test_role = Role(
            name='test_limited',
            name_ar='مستخدم محدود',
            description='Limited user for testing',
            description_en='Limited user for testing'
        )
        db.session.add(test_role)
        db.session.commit()
        
        # Add only view permissions (no add, edit, delete)
        view_permissions = Permission.query.filter(
            Permission.name.like('%.view')
        ).all()
        
        for perm in view_permissions:
            role_perm = RolePermission(
                role_id=test_role.id,
                permission_id=perm.id
            )
            db.session.add(role_perm)
        
        db.session.commit()
        
        # Create test user
        test_user = User(
            username='test_limited',
            email='test_limited@example.com',
            role_id=test_role.id,
            is_active=True,
            is_admin=False
        )
        test_user.set_password('123456')
        db.session.add(test_user)
        db.session.commit()
        
        print(f"   ✅ تم إنشاء المستخدم test_limited مع {len(view_permissions)} صلاحية عرض فقط")
        print(f"   ✅ Created user test_limited with {len(view_permissions)} view permissions only")
    
    print("\n📋 الخطوة 2: التحقق من الصلاحيات...")
    print("📋 Step 2: Checking permissions...")
    
    # Test permissions
    test_cases = [
        ('accounting.accounts.add', 'إضافة حساب'),
        ('accounting.accounts.edit', 'تعديل حساب'),
        ('accounting.accounts.delete', 'حذف حساب'),
        ('accounting.transactions.delete', 'حذف قيد يومي'),
        ('accounting.payments.add', 'إضافة مدفوعة'),
        ('accounting.payments.delete', 'حذف مدفوعة'),
        ('inventory.products.add', 'إضافة منتج'),
        ('inventory.products.edit', 'تعديل منتج'),
        ('inventory.products.delete', 'حذف منتج'),
        ('sales.invoices.add', 'إضافة فاتورة مبيعات'),
        ('sales.invoices.delete', 'حذف فاتورة مبيعات'),
        ('purchases.invoices.add', 'إضافة فاتورة مشتريات'),
        ('purchases.invoices.delete', 'حذف فاتورة مشتريات'),
    ]
    
    print("\n   المستخدم test_limited يجب ألا يملك هذه الصلاحيات:")
    print("   User test_limited should NOT have these permissions:")
    print()
    
    all_correct = True
    for perm_name, perm_ar in test_cases:
        has_perm = test_user.has_permission(perm_name)
        if has_perm:
            print(f"   ❌ {perm_ar} ({perm_name}) - يملكها! (خطأ)")
            all_correct = False
        else:
            print(f"   ✅ {perm_ar} ({perm_name}) - لا يملكها (صحيح)")
    
    print("\n" + "=" * 80)
    if all_correct:
        print("✅ جميع الاختبارات نجحت!")
        print("✅ All tests passed!")
        print("\n💡 الآن يمكنك اختبار النظام:")
        print("💡 Now you can test the system:")
        print("   1. سجل الدخول بالمستخدم: test_limited")
        print("   1. Login with user: test_limited")
        print("   2. كلمة المرور: 123456")
        print("   2. Password: 123456")
        print("   3. حاول الوصول إلى:")
        print("   3. Try to access:")
        print("      - http://localhost:5000/accounting/accounts/add")
        print("      - http://localhost:5000/inventory/products/add")
        print("   4. يجب أن ترى رسالة: 403 Forbidden")
        print("   4. You should see: 403 Forbidden")
    else:
        print("❌ بعض الاختبارات فشلت!")
        print("❌ Some tests failed!")
        print("   المستخدم test_limited لديه صلاحيات لا يجب أن يملكها!")
        print("   User test_limited has permissions they shouldn't have!")
    print("=" * 80)

