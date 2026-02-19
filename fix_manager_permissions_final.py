#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix Manager Permissions - Final Fix
إصلاح صلاحيات المدير - الإصلاح النهائي
"""

from app import create_app, db
from app.models import Role, Permission, RolePermission

app = create_app()

with app.app_context():
    print("=" * 80)
    print("🔧 FIXING MANAGER PERMISSIONS - إصلاح صلاحيات المدير")
    print("=" * 80)
    
    # Get manager role
    manager_role = Role.query.filter_by(name='manager').first()
    if not manager_role:
        print("❌ Manager role not found!")
        exit(1)
    
    print(f"\n✅ Found manager role: {manager_role.name} ({manager_role.name_ar})")
    print(f"   Current permissions: {len(manager_role.permissions)}")
    
    # Permissions to add
    missing_permissions = [
        'accounting.accounts.add',
        'accounting.accounts.delete'
    ]
    
    print(f"\n📌 Adding missing permissions:")
    added_count = 0
    
    for perm_name in missing_permissions:
        # Check if permission exists in database
        perm = Permission.query.filter_by(name=perm_name).first()
        if not perm:
            print(f"   ❌ {perm_name} - NOT FOUND IN DATABASE!")
            continue
        
        # Check if already assigned
        existing = RolePermission.query.filter_by(
            role_id=manager_role.id,
            permission_id=perm.id
        ).first()
        
        if existing:
            print(f"   ⚠️  {perm_name} - ALREADY ASSIGNED")
            continue
        
        # Add permission
        role_perm = RolePermission(
            role_id=manager_role.id,
            permission_id=perm.id
        )
        db.session.add(role_perm)
        added_count += 1
        print(f"   ✅ {perm_name} (ID: {perm.id}) - ADDED")
    
    # Commit changes
    if added_count > 0:
        try:
            db.session.commit()
            print(f"\n✅ Successfully added {added_count} permissions!")
            
            # Verify
            manager_role = Role.query.filter_by(name='manager').first()
            print(f"   New total permissions: {len(manager_role.permissions)}")
            
            # List all accounting permissions
            print(f"\n📊 All accounting permissions for manager:")
            accounting_perms = [p for p in manager_role.permissions if p.module == 'accounting']
            for perm in sorted(accounting_perms, key=lambda x: x.name):
                print(f"   • {perm.name} - {perm.name_ar}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {str(e)}")
    else:
        print(f"\n⚠️  No permissions were added (all already exist)")
    
    print("\n" + "=" * 80)
    print("✅ DONE")
    print("=" * 80)

