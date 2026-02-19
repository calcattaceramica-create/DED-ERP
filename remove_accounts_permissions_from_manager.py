#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
إزالة صلاحيات accounting.accounts.add و accounting.accounts.delete من دور المدير
"""

from app import create_app, db
from app.models import Role, Permission

app = create_app()

with app.app_context():
    print("=" * 100)
    print("🔧 إزالة صلاحيات accounting.accounts.add و accounting.accounts.delete من دور المدير")
    print("=" * 100)
    
    # الحصول على دور المدير
    manager_role = Role.query.filter_by(name='manager').first()
    
    if not manager_role:
        print("❌ دور المدير غير موجود!")
        exit(1)
    
    print(f"\n📋 دور: {manager_role.name_ar}")
    print(f"   عدد الصلاحيات الحالية: {len(manager_role.permissions)}")
    
    # الصلاحيات المطلوب إزالتها
    permissions_to_remove = [
        'accounting.accounts.add',
        'accounting.accounts.delete'
    ]
    
    print(f"\n🔍 إزالة الصلاحيات:")
    print("-" * 100)
    
    removed_count = 0
    
    for perm_name in permissions_to_remove:
        perm = Permission.query.filter_by(name=perm_name).first()
        
        if not perm:
            print(f"   ❌ {perm_name} - غير موجودة في قاعدة البيانات!")
            continue
        
        # التحقق إذا كانت الصلاحية موجودة
        if perm in manager_role.permissions:
            # إزالة الصلاحية
            manager_role.permissions.remove(perm)
            removed_count += 1
            print(f"   ➖ {perm_name} - تمت الإزالة")
        else:
            print(f"   ⚠️  {perm_name} - غير موجودة في دور المدير")
    
    if removed_count > 0:
        db.session.commit()
        print(f"\n✅ تم إزالة {removed_count} صلاحية")
    else:
        print(f"\n⚠️  لم يتم إزالة أي صلاحية")
    
    # التحقق النهائي
    print(f"\n📊 عدد الصلاحيات بعد التحديث: {len(manager_role.permissions)}")
    
    # اختبار المستخدم ali
    from app.models import User
    user = User.query.filter_by(username='ali').first()
    
    if user:
        print(f"\n🧪 اختبار المستخدم ali:")
        print("-" * 100)
        
        test_perms = [
            'accounting.accounts.view',
            'accounting.accounts.add',
            'accounting.accounts.edit',
            'accounting.accounts.delete'
        ]
        
        for perm_name in test_perms:
            has_perm = user.has_permission(perm_name)
            status = "✅" if has_perm else "❌"
            print(f"   {status} {perm_name}: {has_perm}")
    
    print("\n" + "=" * 100)
    print("✅ تم الانتهاء!")
    print("=" * 100)
    print("\n⚠️  الآن المستخدم ali لا يستطيع إضافة أو حذف الحسابات البنكية")
    print("⚠️  لكنه يستطيع عرضها وتعديلها فقط")
    print("=" * 100)

