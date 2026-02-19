"""
Add Delete Bank Account Permission
إضافة صلاحية حذف الحساب البنكي
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Permission, Role

app = create_app()

with app.app_context():
    print('='*70)
    print('🔍 فحص صلاحية حذف الحساب البنكي')
    print('='*70)
    print()
    
    # Check if permission exists
    perm = Permission.query.filter_by(name='accounting.accounts.delete').first()
    
    if perm:
        print('✅ الصلاحية accounting.accounts.delete موجودة')
        print(f'   ID: {perm.id}')
        print(f'   الاسم بالعربي: {perm.name_ar}')
        print()
        
        # Check which roles have this permission
        print('📋 الأدوار التي لديها هذه الصلاحية:')
        for role in Role.query.all():
            if perm in role.permissions:
                print(f'   ✅ {role.name_ar} ({role.name})')
        print()
    else:
        print('❌ الصلاحية accounting.accounts.delete غير موجودة!')
        print()
        print('💡 سأقوم بإضافتها الآن...')
        print()
        
        # Create the permission
        new_perm = Permission(
            name='accounting.accounts.delete',
            name_ar='حذف الحسابات البنكية',
            description='Permission to delete bank accounts',
            category='accounting'
        )
        db.session.add(new_perm)
        db.session.commit()
        
        print('✅ تم إضافة الصلاحية بنجاح!')
        print(f'   ID: {new_perm.id}')
        print()
        
        # Add to admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            admin_role.permissions.append(new_perm)
            db.session.commit()
            print('✅ تم إضافة الصلاحية لدور المدير (admin)')
        
        print()
    
    print('='*70)
    print('✅ تم الانتهاء!')
    print('='*70)

