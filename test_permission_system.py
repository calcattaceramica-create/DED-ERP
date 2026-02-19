#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test permission system"""

from app import create_app, db
from app.models import User, Role, Permission, RolePermission

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("اختبار نظام الصلاحيات")
    print("="*60)
    
    # Get ali user
    ali = User.query.filter_by(username='ali').first()
    
    if not ali:
        print("❌ المستخدم ali غير موجود!")
        exit(1)
    
    print(f"\n👤 المستخدم: {ali.username}")
    print(f"   الاسم: {ali.full_name}")
    print(f"   is_admin: {ali.is_admin}")
    print(f"   الدور: {ali.role.name_ar if ali.role else 'لا يوجد'}")
    
    # Test specific permissions
    test_permissions = [
        'accounting.accounts.add',
        'accounting.accounts.edit',
        'accounting.accounts.delete',
        'inventory.products.add',
        'inventory.products.delete',
        'sales.invoices.add',
        'sales.invoices.delete',
    ]
    
    print(f"\n🔍 اختبار الصلاحيات:")
    for perm_name in test_permissions:
        has_perm = ali.has_permission(perm_name)
        status = "✅" if has_perm else "❌"
        print(f"   {status} {perm_name}: {has_perm}")
    
    # Check if permission exists in role
    if ali.role:
        print(f"\n📋 صلاحيات الدور ({len(ali.role.permissions)}):")
        
        # Group by module
        modules = {}
        for perm in ali.role.permissions:
            module = perm.module or 'general'
            if module not in modules:
                modules[module] = []
            modules[module].append(perm.name)
        
        for module, perms in sorted(modules.items()):
            print(f"\n   {module} ({len(perms)}):")
            for perm in sorted(perms):
                print(f"      - {perm}")
    
    print("\n" + "="*60)
    print("💡 الخلاصة:")
    print("="*60)
    
    if ali.is_admin:
        print("⚠️ المستخدم هو admin - سيتجاوز جميع فحوصات الصلاحيات!")
        print("   الحل: تغيير is_admin إلى False")
    elif ali.role and len(ali.role.permissions) > 0:
        print(f"✅ المستخدم لديه دور مع {len(ali.role.permissions)} صلاحية")
        print("   نظام الصلاحيات يعمل بشكل صحيح")
    else:
        print("❌ المستخدم ليس لديه صلاحيات!")
        print("   الحل: إضافة صلاحيات للدور")
    
    print("\n" + "="*60)

