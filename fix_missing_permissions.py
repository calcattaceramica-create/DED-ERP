#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix missing base permissions
Add inventory.view, sales.view, pos.access to all permissions
"""

from app import create_app, db
from app.models import Permission, Role, RolePermission

app = create_app()

with app.app_context():
    print('='*80)
    print('Adding missing base permissions...')
    print('='*80)
    print()
    
    # Check if these permissions exist
    missing_perms = [
        ('inventory.view', 'عرض المخزون', 'inventory'),
        ('sales.view', 'عرض المبيعات', 'sales'),
        ('pos.access', 'الوصول لنقطة البيع', 'pos'),
    ]
    
    added_count = 0
    
    for perm_name, perm_name_ar, module in missing_perms:
        existing = Permission.query.filter_by(name=perm_name).first()
        
        if not existing:
            print(f'Adding permission: {perm_name}')
            perm = Permission(
                name=perm_name,
                name_ar=perm_name_ar,
                module=module
            )
            db.session.add(perm)
            added_count += 1
        else:
            print(f'Permission already exists: {perm_name}')
    
    if added_count > 0:
        db.session.commit()
        print()
        print(f'Added {added_count} new permissions')
    
    print()
    print('='*80)
    print('Adding missing permissions to manager role...')
    print('='*80)
    print()
    
    # Get manager role
    manager_role = Role.query.filter_by(name='manager').first()
    
    if not manager_role:
        print('Manager role not found!')
        exit(1)
    
    print(f'Manager role has {len(manager_role.permissions)} permissions')
    
    # Get the missing permissions
    perms_to_add = []
    for perm_name, _, _ in missing_perms:
        perm = Permission.query.filter_by(name=perm_name).first()
        if perm and perm not in manager_role.permissions:
            perms_to_add.append(perm)
    
    if perms_to_add:
        print(f'Adding {len(perms_to_add)} permissions to manager role:')
        for perm in perms_to_add:
            print(f'  - {perm.name}')
            role_perm = RolePermission(
                role_id=manager_role.id,
                permission_id=perm.id
            )
            db.session.add(role_perm)
        
        db.session.commit()
        print()
        print('Permissions added successfully!')
    else:
        print('All permissions already exist in manager role')
    
    print()
    print('='*80)
    print('Verifying ali user permissions...')
    print('='*80)
    print()
    
    from app.models import User
    ali = User.query.filter_by(username='ali').first()
    
    if ali:
        print(f'User: {ali.username}')
        print(f'Role: {ali.role.name if ali.role else "No role"}')
        print(f'Total permissions: {len(ali.role.permissions) if ali.role else 0}')
        print()
        
        test_perms = [
            'dashboard.view',
            'inventory.view',
            'sales.view',
            'purchases.view',
            'accounting.view',
            'hr.view',
            'reports.view',
            'settings.view',
            'pos.access'
        ]
        
        print('Testing permissions:')
        for perm in test_perms:
            has_it = ali.has_permission(perm)
            status = 'YES' if has_it else 'NO '
            print(f'  {status} - {perm}')
    
    print()
    print('='*80)
    print('Done!')
    print('='*80)

