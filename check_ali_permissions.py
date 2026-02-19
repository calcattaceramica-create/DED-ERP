#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check ali user permissions
"""

from app import create_app, db
from app.models import User, Role, Permission

app = create_app()

with app.app_context():
    # Get user ali
    ali = User.query.filter_by(username='ali').first()
    
    if not ali:
        print('User ali not found!')
        exit(1)
    
    print('='*80)
    print(f'User: {ali.username}')
    print(f'is_admin: {ali.is_admin}')
    print(f'Role: {ali.role.name if ali.role else "No role"}')
    print('='*80)
    print()
    
    if ali.role:
        print(f'Role has {len(ali.role.permissions)} permissions:')
        print()
        
        # Group by module
        modules = {}
        for perm in ali.role.permissions:
            if perm.module not in modules:
                modules[perm.module] = []
            modules[perm.module].append(perm.name)
        
        for module, perms in sorted(modules.items()):
            print(f'{module}: {len(perms)} permissions')
            for perm in sorted(perms):
                print(f'  - {perm}')
            print()
    else:
        print('User has no role!')
    
    print('='*80)
    print('Testing specific permissions:')
    print('='*80)
    
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
    
    for perm in test_perms:
        has_it = ali.has_permission(perm)
        status = 'YES' if has_it else 'NO'
        print(f'{status:5} - {perm}')

