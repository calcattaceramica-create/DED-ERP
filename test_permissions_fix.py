#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Permission System - Create test user with limited permissions
"""

from app import create_app, db
from app.models import User, Role, Permission

app = create_app()

with app.app_context():
    print('='*80)
    print('🔧 Testing Permission System')
    print('='*80)
    print()
    
    # Create a test role with limited permissions
    test_role = Role.query.filter_by(name='test_viewer').first()
    
    if not test_role:
        print('📝 Creating test role: test_viewer')
        test_role = Role(
            name='test_viewer',
            name_ar='مشاهد تجريبي',
            description='Test role with view-only permissions',
            description_en='Test role with view-only permissions'
        )
        db.session.add(test_role)
        db.session.commit()
        print('✅ Test role created')
    else:
        print('✅ Test role already exists')
    
    # Add only view permissions (no edit, no delete)
    view_permissions = [
        'dashboard.view',
        'inventory.view',
        'inventory.products.view',
        'inventory.stock.view',
        'sales.view',
        'sales.invoices.view',
    ]
    
    print()
    print('📋 Adding view-only permissions to test role...')
    
    for perm_name in view_permissions:
        perm = Permission.query.filter_by(name=perm_name).first()
        if perm and perm not in test_role.permissions:
            test_role.permissions.append(perm)
            print(f'  ✅ Added: {perm_name}')
    
    db.session.commit()
    
    # Create test user
    test_user = User.query.filter_by(username='test_viewer').first()
    
    if not test_user:
        print()
        print('👤 Creating test user: test_viewer')
        test_user = User(
            username='test_viewer',
            email='test@test.com',
            full_name='Test Viewer',
            role_id=test_role.id,
            is_active=True,
            is_admin=False
        )
        test_user.set_password('123456')
        db.session.add(test_user)
        db.session.commit()
        print('✅ Test user created')
        print()
        print('📝 Login credentials:')
        print('   Username: test_viewer')
        print('   Password: 123456')
    else:
        print()
        print('✅ Test user already exists')
        test_user.role_id = test_role.id
        db.session.commit()
    
    print()
    print('='*80)
    print('✅ Test Setup Complete!')
    print('='*80)
    print()
    print('🧪 Test Instructions:')
    print()
    print('1. Logout from current user')
    print('2. Login with:')
    print('   Username: test_viewer')
    print('   Password: 123456')
    print()
    print('3. Expected Behavior:')
    print('   ✅ Can see: Dashboard, Inventory, Sales menus')
    print('   ✅ Can view: Products, Stock, Invoices')
    print('   ❌ Cannot see: Edit buttons')
    print('   ❌ Cannot see: Delete buttons')
    print('   ❌ Cannot see: Add buttons')
    print('   ❌ Cannot access: Purchases, HR, Settings')
    print()
    print('4. Test Cases:')
    print('   a) Go to Inventory → Products')
    print('      - Should see products list')
    print('      - Should NOT see Edit/Delete buttons')
    print()
    print('   b) Go to Sales → Invoices')
    print('      - Should see invoices list')
    print('      - Should NOT see Delete buttons')
    print()
    print('   c) Try to access Settings')
    print('      - Should NOT see Settings menu')
    print()
    print('='*80)
    print()
    
    # Display test user permissions
    print('📊 Test User Permissions:')
    print(f'   Role: {test_role.name_ar} ({test_role.name})')
    print(f'   Total Permissions: {len(test_role.permissions)}')
    print()
    print('   Permissions List:')
    for perm in sorted(test_role.permissions, key=lambda p: p.name):
        print(f'   ✅ {perm.name}')
    
    print()
    print('='*80)
    print('🎯 Ready for testing!')
    print('='*80)

