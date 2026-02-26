import sys
sys.path.insert(0, 'C:/Users/DELL/DED')

from app import create_app, db
from app.models import Permission, Role, User

app = create_app()
with app.app_context():
    print("="*60)
    print("فحص صلاحية reports.financial")
    print("="*60)
    
    # Check if reports.financial permission exists
    perm = Permission.query.filter_by(name='reports.financial').first()
    if perm:
        print(f"✅ الصلاحية موجودة: {perm.name} (ID={perm.id})")
        print("   الأدوار التي تملكها:")
        for role in Role.query.all():
            if perm in role.permissions:
                print(f"   ✅ {role.name}")
    else:
        print("❌ الصلاحية غير موجودة: reports.financial")
        print("\nالصلاحيات المتعلقة بـ reports:")
        perms = Permission.query.filter(Permission.name.like('reports%')).all()
        for p in perms:
            print(f"   - {p.name}")
    
    print()
    print("="*60)
    print("فحص المستخدم admin")
    print("="*60)
    
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"✅ is_admin={admin.is_admin}, role={admin.role.name if admin.role else 'None'}")
        print(f"   يمكنه الوصول للميزانية: {admin.has_permission('reports.financial')}")
    else:
        print("❌ المستخدم admin غير موجود")

