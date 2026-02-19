#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive System Check - فحص شامل للنظام
This script checks the entire permissions system
"""

from app import create_app, db
from app.models import User, Role, Permission, RolePermission

app = create_app()

with app.app_context():
    print("=" * 80)
    print("🔍 COMPREHENSIVE PERMISSIONS SYSTEM CHECK - فحص شامل لنظام الصلاحيات")
    print("=" * 80)
    
    # 1. Check Manager User
    print("\n📌 1. CHECKING MANAGER USER (ali)")
    print("-" * 80)
    manager = User.query.filter_by(username='ali').first()
    if manager:
        print(f"✅ User found: {manager.username}")
        print(f"   - Email: {manager.email}")
        print(f"   - Is Admin: {manager.is_admin}")
        print(f"   - Is Active: {manager.is_active}")
        print(f"   - Role: {manager.role.name if manager.role else 'NO ROLE'}")
        print(f"   - Role ID: {manager.role_id}")
        
        if manager.role:
            print(f"\n   📊 Role Details:")
            print(f"   - Role Name: {manager.role.name}")
            print(f"   - Role Name (AR): {manager.role.name_ar}")
            print(f"   - Total Permissions: {len(manager.role.permissions)}")
            
            # Check specific bank account permissions
            bank_perms = ['accounting.accounts.add', 'accounting.accounts.edit', 'accounting.accounts.delete']
            print(f"\n   🏦 Bank Account Permissions:")
            for perm_name in bank_perms:
                has_perm = manager.has_permission(perm_name)
                status = "✅ HAS" if has_perm else "❌ MISSING"
                print(f"   - {perm_name}: {status}")
                
                # Check if permission exists in database
                perm_in_db = Permission.query.filter_by(name=perm_name).first()
                if perm_in_db:
                    in_role = perm_in_db in manager.role.permissions
                    print(f"     └─ In Database: ✅ | In Role: {'✅' if in_role else '❌'}")
                else:
                    print(f"     └─ In Database: ❌ PERMISSION NOT FOUND IN DATABASE!")
    else:
        print("❌ Manager user 'ali' not found!")
    
    # 2. Check Manager Role
    print("\n\n📌 2. CHECKING MANAGER ROLE")
    print("-" * 80)
    manager_role = Role.query.filter_by(name='manager').first()
    if manager_role:
        print(f"✅ Role found: {manager_role.name} ({manager_role.name_ar})")
        print(f"   - Total Permissions: {len(manager_role.permissions)}")
        
        # Group permissions by module
        modules = {}
        for perm in manager_role.permissions:
            if perm.module not in modules:
                modules[perm.module] = []
            modules[perm.module].append(perm.name)
        
        print(f"\n   📊 Permissions by Module:")
        for module, perms in sorted(modules.items()):
            print(f"   - {module}: {len(perms)} permissions")
            for perm in sorted(perms):
                print(f"     • {perm}")
    else:
        print("❌ Manager role not found!")
    
    # 3. Check RolePermission table
    print("\n\n📌 3. CHECKING ROLE_PERMISSION TABLE")
    print("-" * 80)
    if manager_role:
        role_perms = RolePermission.query.filter_by(role_id=manager_role.id).all()
        print(f"✅ Found {len(role_perms)} entries in role_permission table for manager role")
        
        # Check specific bank permissions
        bank_perm_ids = []
        for perm_name in ['accounting.accounts.add', 'accounting.accounts.edit', 'accounting.accounts.delete']:
            perm = Permission.query.filter_by(name=perm_name).first()
            if perm:
                bank_perm_ids.append(perm.id)
                rp = RolePermission.query.filter_by(role_id=manager_role.id, permission_id=perm.id).first()
                status = "✅ EXISTS" if rp else "❌ MISSING"
                print(f"   - {perm_name} (ID: {perm.id}): {status}")
    
    # 4. Test has_permission method
    print("\n\n📌 4. TESTING has_permission() METHOD")
    print("-" * 80)
    if manager:
        test_permissions = [
            'accounting.accounts.add',
            'accounting.accounts.edit',
            'accounting.accounts.delete',
            'accounting.view',
            'inventory.products.add',
            'sales.invoices.add'
        ]
        
        print("Testing permissions:")
        for perm_name in test_permissions:
            result = manager.has_permission(perm_name)
            status = "✅ TRUE" if result else "❌ FALSE"
            print(f"   - {perm_name}: {status}")
    
    # 5. Check if permissions exist in database
    print("\n\n📌 5. CHECKING PERMISSIONS IN DATABASE")
    print("-" * 80)
    critical_perms = [
        'accounting.accounts.add',
        'accounting.accounts.edit',
        'accounting.accounts.delete',
        'accounting.accounts.view'
    ]
    
    for perm_name in critical_perms:
        perm = Permission.query.filter_by(name=perm_name).first()
        if perm:
            print(f"✅ {perm_name}")
            print(f"   - ID: {perm.id}")
            print(f"   - Module: {perm.module}")
            print(f"   - Name (AR): {perm.name_ar}")
            
            # Count how many roles have this permission
            roles_with_perm = Role.query.join(Role.permissions).filter(Permission.id == perm.id).all()
            print(f"   - Used by {len(roles_with_perm)} roles: {', '.join([r.name for r in roles_with_perm])}")
        else:
            print(f"❌ {perm_name} - NOT FOUND IN DATABASE!")
    
    print("\n" + "=" * 80)
    print("✅ COMPREHENSIVE CHECK COMPLETE")
    print("=" * 80)

