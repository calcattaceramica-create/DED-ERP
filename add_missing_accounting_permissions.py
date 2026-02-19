#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Add missing accounting permissions to manager role"""

from app import create_app, db
from app.models import Role, Permission, RolePermission

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("إضافة صلاحيات المحاسبة المفقودة لدور المدير")
    print("="*60)
    
    # Get manager role
    manager_role = Role.query.filter_by(name='manager').first()
    
    if not manager_role:
        print("❌ دور manager غير موجود!")
        exit(1)
    
    print(f"\n👤 الدور: {manager_role.name_ar}")
    print(f"   عدد الصلاحيات الحالية: {len(manager_role.permissions)}")
    
    # Missing permissions
    missing_perms = [
        'accounting.accounts.add',
        'accounting.accounts.delete',
    ]
    
    print(f"\n🔍 البحث عن الصلاحيات المفقودة:")
    
    added_count = 0
    for perm_name in missing_perms:
        # Check if permission exists in database
        perm = Permission.query.filter_by(name=perm_name).first()
        
        if not perm:
            print(f"   ❌ الصلاحية {perm_name} غير موجودة في قاعدة البيانات!")
            continue
        
        # Check if role already has this permission
        if perm in manager_role.permissions:
            print(f"   ✅ {perm_name} - موجودة بالفعل")
            continue
        
        # Add permission to role
        role_perm = RolePermission(
            role_id=manager_role.id,
            permission_id=perm.id
        )
        db.session.add(role_perm)
        added_count += 1
        print(f"   ➕ {perm_name} (ID: {perm.id}) - تمت الإضافة")
    
    if added_count > 0:
        db.session.commit()
        print(f"\n✅ تم إضافة {added_count} صلاحية بنجاح!")
        
        # Refresh role
        db.session.refresh(manager_role)
        print(f"   عدد الصلاحيات الجديد: {len(manager_role.permissions)}")
    else:
        print(f"\n✅ جميع الصلاحيات موجودة بالفعل!")
    
    print("\n" + "="*60)

