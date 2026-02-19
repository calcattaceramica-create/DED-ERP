"""
Check bank account delete permission
"""
from app import create_app, db
from app.models import Permission, Role, User

app = create_app()

with app.app_context():
    print("=" * 80)
    print("🔍 التحقق من صلاحية حذف الحساب البنكي")
    print("🔍 Checking bank account delete permission")
    print("=" * 80)
    print()
    
    # Check if permission exists
    perm = Permission.query.filter_by(name='accounting.accounts.delete').first()
    
    if perm:
        print(f"✅ الصلاحية موجودة:")
        print(f"   ID: {perm.id}")
        print(f"   Name: {perm.name}")
        print(f"   Name AR: {perm.name_ar}")
        print()
        
        # Check which roles have this permission
        print("✅ الأدوار التي لديها هذه الصلاحية: ")
        roles = Role.query.all()
        for role in roles:
            if perm in role.permissions:
                print(f"   - {role.name_ar} ({role.name})")
        print()
        
        # Check admin user
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"👤 المستخدم admin:")
            print(f"   ID: {admin.id}")
            print(f"   Username: {admin.username}")
            print(f"   Role ID: {admin.role_id}")
            if admin.role:
                print(f"   Role Name: {admin.role.name}")
                if perm in admin.role.permissions:
                    print(f"   ✅ المستخدم admin لديه صلاحية حذف الحساب البنكي")
                else:
                    print(f"   ❌ المستخدم admin ليس لديه صلاحية حذف الحساب البنكي")
            print()
    else:
        print("❌ الصلاحية غير موجودة!")
        print("   سيتم إنشاؤها الآن...")
        print()
        
        # Create the permission
        perm = Permission(
            name='accounting.accounts.delete',
            name_ar='حذف حساب',
            module='accounting'
        )
        db.session.add(perm)
        db.session.flush()
        
        # Add to admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            admin_role.permissions.append(perm)
            db.session.commit()
            print("✅ تم إنشاء الصلاحية وإضافتها لدور المدير!")
        else:
            db.session.commit()
            print("✅ تم إنشاء الصلاحية!")
    
    print()
    print("=" * 80)
    print("✅ تم الانتهاء!")
    print("=" * 80)

