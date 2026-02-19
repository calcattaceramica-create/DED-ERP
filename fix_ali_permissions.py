#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix ali user permissions - ensure he has settings.roles.edit
"""

from app import create_app, db
from app.models import User, Role, Permission

app = create_app()

with app.app_context():
    print('='*80)
    print('🔧 إصلاح صلاحيات المستخدم ali')
    print('='*80)
    print()
    
    # Get ali user
    ali = User.query.filter_by(username='ali').first()
    
    if not ali:
        print('❌ المستخدم ali غير موجود!')
        exit(1)
    
    if not ali.role:
        print('❌ المستخدم ali ليس لديه دور!')
        exit(1)
    
    print(f'👤 المستخدم: ali')
    print(f'📋 الدور: {ali.role.name_ar} ({ali.role.name})')
    print(f'📊 عدد الصلاحيات الحالية: {len(ali.role.permissions)}')
    print()
    
    # Check important permissions
    important_perms = [
        'settings.roles.edit',
        'settings.permissions.manage',
        'settings.roles.manage',
        'settings.roles.delete',
        'settings.users.edit',
        'settings.users.delete'
    ]
    
    print('🔍 فحص الصلاحيات المهمة:')
    missing_perms = []
    
    for perm_name in important_perms:
        has_perm = ali.has_permission(perm_name)
        status = '✅' if has_perm else '❌'
        print(f'   {status} {perm_name}')
        
        if not has_perm:
            missing_perms.append(perm_name)
    
    print()
    
    if missing_perms:
        print(f'⚠️  المستخدم ali يفتقد {len(missing_perms)} صلاحية مهمة!')
        print()
        print('💡 إضافة الصلاحيات المفقودة...')
        print()
        
        added_count = 0
        for perm_name in missing_perms:
            perm = Permission.query.filter_by(name=perm_name).first()
            if perm and perm not in ali.role.permissions:
                ali.role.permissions.append(perm)
                print(f'   ✅ تمت إضافة: {perm_name}')
                added_count += 1
        
        if added_count > 0:
            db.session.commit()
            print()
            print(f'✅ تمت إضافة {added_count} صلاحية جديدة!')
            print(f'📊 إجمالي الصلاحيات الآن: {len(ali.role.permissions)}')
        else:
            print()
            print('⚠️  لم يتم إضافة أي صلاحيات (قد تكون غير موجودة في النظام)')
    else:
        print('✅ المستخدم ali لديه جميع الصلاحيات المهمة!')
    
    print()
    print('='*80)
    print('✅ تم الانتهاء!')
    print('='*80)
    print()
    print('📝 الآن يمكن للمستخدم ali:')
    print('   ✅ تعديل الأدوار')
    print('   ✅ إضافة وإلغاء الصلاحيات')
    print('   ✅ إدارة المستخدمين')
    print()

