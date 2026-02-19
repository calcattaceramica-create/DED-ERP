#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check POS permissions for users"""

from app import create_app, db
from app.models import User, Role, Permission, RolePermission

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("فحص صلاحيات نقطة البيع (POS)")
    print("="*60)
    
    # Get all POS permissions
    pos_permissions = Permission.query.filter(Permission.name.like('pos.%')).all()
    print(f"\n📋 صلاحيات POS المتوفرة في النظام ({len(pos_permissions)}):")
    for perm in pos_permissions:
        print(f"  - {perm.name} (ID: {perm.id}) - {perm.name_ar}")
    
    # Check manager role
    manager_role = Role.query.filter_by(name='manager').first()
    if manager_role:
        print(f"\n👤 دور المدير: {manager_role.name_ar}")
        print(f"   إجمالي الصلاحيات: {len(manager_role.permissions)}")
        
        manager_pos_perms = [p for p in manager_role.permissions if p.name.startswith('pos.')]
        print(f"\n   صلاحيات POS للمدير ({len(manager_pos_perms)}):")
        if manager_pos_perms:
            for perm in manager_pos_perms:
                print(f"     ✅ {perm.name}")
        else:
            print("     ❌ لا توجد صلاحيات POS")
        
        # Check which POS permissions are missing
        missing_perms = [p for p in pos_permissions if p not in manager_role.permissions]
        if missing_perms:
            print(f"\n   ⚠️ صلاحيات POS المفقودة ({len(missing_perms)}):")
            for perm in missing_perms:
                print(f"     ❌ {perm.name} (ID: {perm.id})")
    
    # Check ali user
    ali = User.query.filter_by(username='ali').first()
    if ali:
        print(f"\n👤 المستخدم: {ali.username}")
        print(f"   الدور: {ali.role.name_ar if ali.role else 'لا يوجد'}")
        print(f"   Admin: {ali.is_admin}")
        
        if ali.role:
            ali_pos_perms = [p for p in ali.role.permissions if p.name.startswith('pos.')]
            print(f"\n   صلاحيات POS ({len(ali_pos_perms)}):")
            if ali_pos_perms:
                for perm in ali_pos_perms:
                    print(f"     ✅ {perm.name}")
            else:
                print("     ❌ لا توجد صلاحيات POS")
    
    print("\n" + "="*60)

