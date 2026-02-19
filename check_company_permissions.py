#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
فحص صلاحيات بيانات الشركة
"""

from app import create_app, db
from app.models import User, Permission, Role

app = create_app()

with app.app_context():
    print("=" * 100)
    print("🔍 فحص صلاحيات بيانات الشركة")
    print("=" * 100)
    
    # الحصول على المستخدم ali
    user = User.query.filter_by(username='ali').first()
    
    if not user:
        print("❌ المستخدم ali غير موجود!")
        exit(1)
    
    print(f"\n👤 المستخدم: {user.username}")
    print(f"   الاسم: {user.full_name}")
    print(f"   الدور: {user.role.name_ar if user.role else 'None'}")
    
    # الصلاحيات المتعلقة بالشركة
    company_permissions = [
        'settings.company.view',
        'settings.company.edit'
    ]
    
    print(f"\n🔍 صلاحيات بيانات الشركة:")
    print("-" * 100)
    
    for perm_name in company_permissions:
        has_perm = user.has_permission(perm_name)
        status = "✅" if has_perm else "❌"
        print(f"   {status} {perm_name}: {has_perm}")
    
    # التحقق من وجود الصلاحيات في قاعدة البيانات
    print(f"\n📋 التحقق من وجود الصلاحيات في قاعدة البيانات:")
    print("-" * 100)
    
    for perm_name in company_permissions:
        perm = Permission.query.filter_by(name=perm_name).first()
        if perm:
            print(f"   ✅ {perm_name} - موجودة في DB (ID: {perm.id})")
            
            # التحقق من وجودها في دور المدير
            if user.role:
                in_role = perm in user.role.permissions
                status = "✅" if in_role else "❌"
                print(f"      {status} في دور المدير: {in_role}")
        else:
            print(f"   ❌ {perm_name} - غير موجودة في DB")
    
    # عرض جميع صلاحيات settings
    print(f"\n📋 جميع صلاحيات settings للمستخدم ali:")
    print("-" * 100)
    
    if user.role:
        settings_perms = [p.name for p in user.role.permissions if p.module == 'settings']
        if settings_perms:
            for perm in sorted(settings_perms):
                print(f"   ✅ {perm}")
        else:
            print("   ❌ لا توجد صلاحيات في وحدة settings")
    
    print("\n" + "=" * 100)

