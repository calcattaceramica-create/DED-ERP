#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار صلاحيات المستخدم ali
"""

from app import create_app, db
from app.models import User, Permission, RolePermission

app = create_app()

with app.app_context():
    # الحصول على المستخدم ali
    user = User.query.filter_by(username='ali').first()
    
    if not user:
        print("❌ المستخدم ali غير موجود!")
        exit(1)
    
    print("=" * 100)
    print(f"👤 المستخدم: {user.username}")
    print(f"   الاسم: {user.full_name}")
    print(f"   is_admin: {user.is_admin}")
    print(f"   الدور: {user.role.name if user.role else 'None'}")
    print("=" * 100)
    
    # اختبار الصلاحيات المتعلقة بالحسابات البنكية
    print("\n🔍 الصلاحيات المتعلقة بالحسابات البنكية:")
    print("-" * 100)
    
    bank_permissions = [
        'accounting.accounts.add',
        'accounting.accounts.edit',
        'accounting.accounts.delete',
        'accounting.accounts.view'
    ]
    
    for perm_name in bank_permissions:
        has_perm = user.has_permission(perm_name)
        status = "✅" if has_perm else "❌"
        print(f"   {status} {perm_name}: {has_perm}")
    
    # عرض جميع الصلاحيات التي تحتوي على 'accounts'
    print("\n📋 جميع الصلاحيات التي تحتوي على 'accounts':")
    print("-" * 100)
    
    if user.role:
        accounts_perms = [p.name for p in user.role.permissions if 'accounts' in p.name]
        if accounts_perms:
            for perm in sorted(accounts_perms):
                print(f"   ✅ {perm}")
        else:
            print("   ❌ لا توجد صلاحيات تحتوي على 'accounts'")
    
    print("\n" + "=" * 100)
    print(f"📊 إجمالي الصلاحيات: {len(user.role.permissions) if user.role else 0}")
    print("=" * 100)

