#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
إضافة صلاحيات accounting.accounts.* لدور المدير
"""

from app import create_app, db
from app.models import Role, Permission, RolePermission

app = create_app()

with app.app_context():
    print("=" * 100)
    print("🔧 إضافة صلاحيات accounting.accounts.* لدور المدير")
    print("=" * 100)
    
    # الحصول على دور المدير
    manager_role = Role.query.filter_by(name='manager').first()
    
    if not manager_role:
        print("❌ دور المدير غير موجود!")
        exit(1)
    
    print(f"\n📋 دور: {manager_role.name_ar}")
    print(f"   عدد الصلاحيات الحالية: {len(manager_role.permissions)}")
    
    # الصلاحيات المطلوبة
    required_permissions = [
        'accounting.accounts.view',
        'accounting.accounts.add',
        'accounting.accounts.edit',
        'accounting.accounts.delete'
    ]
    
    print(f"\n🔍 التحقق من الصلاحيات المطلوبة:")
    print("-" * 100)
    
    added_count = 0
    
    for perm_name in required_permissions:
        perm = Permission.query.filter_by(name=perm_name).first()
        
        if not perm:
            print(f"   ❌ {perm_name} - غير موجودة في قاعدة البيانات!")
            continue
        
        # التحقق إذا كانت الصلاحية موجودة بالفعل
        if perm in manager_role.permissions:
            print(f"   ✅ {perm_name} - موجودة بالفعل")
        else:
            # إضافة الصلاحية
            manager_role.permissions.append(perm)
            added_count += 1
            print(f"   ➕ {perm_name} - تمت الإضافة")
    
    if added_count > 0:
        db.session.commit()
        print(f"\n✅ تم إضافة {added_count} صلاحية جديدة")
    else:
        print(f"\n✅ جميع الصلاحيات موجودة بالفعل")
    
    # التحقق النهائي
    print(f"\n📊 عدد الصلاحيات بعد التحديث: {len(manager_role.permissions)}")
    
    # اختبار المستخدم ali
    from app.models import User
    user = User.query.filter_by(username='ali').first()
    
    if user:
        print(f"\n🧪 اختبار المستخدم ali:")
        print("-" * 100)
        for perm_name in required_permissions:
            has_perm = user.has_permission(perm_name)
            status = "✅" if has_perm else "❌"
            print(f"   {status} {perm_name}: {has_perm}")
    
    print("\n" + "=" * 100)
    print("✅ تم الانتهاء!")
    print("=" * 100)

