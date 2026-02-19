#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار شامل لصلاحيات المحاسبة والبنوك
"""

from app import create_app, db
from app.models import User, Permission, Role

app = create_app()

with app.app_context():
    print("=" * 100)
    print("🔍 اختبار شامل لصلاحيات المحاسبة والبنوك")
    print("=" * 100)
    
    # الحصول على المستخدم ali
    user = User.query.filter_by(username='ali').first()
    
    if not user:
        print("❌ المستخدم ali غير موجود!")
        exit(1)
    
    print(f"\n👤 المستخدم: {user.username}")
    print(f"   الاسم: {user.full_name}")
    print(f"   is_admin: {user.is_admin}")
    print(f"   الدور: {user.role.name_ar if user.role else 'None'}")
    print(f"   عدد الصلاحيات: {len(user.role.permissions) if user.role else 0}")
    
    # جميع صلاحيات المحاسبة
    accounting_permissions = [
        'accounting.view',
        'accounting.accounts.view',
        'accounting.accounts.add',
        'accounting.accounts.edit',
        'accounting.accounts.delete',
        'accounting.transactions.view',
        'accounting.transactions.add',
        'accounting.transactions.edit',
        'accounting.transactions.delete',
        'accounting.journal.view',
        'accounting.journal.add',
        'accounting.reports.view',
    ]
    
    print(f"\n📊 صلاحيات المحاسبة:")
    print("-" * 100)
    
    has_perms = 0
    missing_perms = 0
    
    for perm_name in accounting_permissions:
        has_perm = user.has_permission(perm_name)
        status = "✅" if has_perm else "❌"
        print(f"   {status} {perm_name}: {has_perm}")
        
        if has_perm:
            has_perms += 1
        else:
            missing_perms += 1
            # التحقق من وجودها في DB
            perm = Permission.query.filter_by(name=perm_name).first()
            if perm:
                print(f"      ⚠️  الصلاحية موجودة في DB (ID: {perm.id}) لكن غير مضافة لدور المدير!")
            else:
                print(f"      ❌ الصلاحية غير موجودة في DB!")
    
    print(f"\n📈 الإحصائيات:")
    print(f"   ✅ صلاحيات موجودة: {has_perms}")
    print(f"   ❌ صلاحيات مفقودة: {missing_perms}")
    
    # التحقق من جميع صلاحيات accounting في دور المدير
    if user.role:
        print(f"\n📋 جميع صلاحيات accounting في دور المدير:")
        print("-" * 100)
        acct_perms = [p.name for p in user.role.permissions if 'accounting' in p.name.lower()]
        if acct_perms:
            for perm in sorted(acct_perms):
                print(f"   ✅ {perm}")
        else:
            print("   ❌ لا توجد صلاحيات accounting في دور المدير!")
    
    print("\n" + "=" * 100)

