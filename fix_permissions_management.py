#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix permissions management - Add settings.permissions.manage to manager role
"""

from app import create_app, db
from app.models import User, Role, Permission

app = create_app()

with app.app_context():
    print('='*80)
    print('🔧 إصلاح صلاحيات إدارة الأدوار')
    print('='*80)
    print()
    
    # Get manager role
    manager_role = Role.query.filter_by(name='manager').first()
    
    if not manager_role:
        print('❌ دور manager غير موجود!')
        exit(1)
    
    print(f'✅ تم العثور على دور: {manager_role.name_ar}')
    print(f'   عدد الصلاحيات الحالية: {len(manager_role.permissions)}')
    print()
    
    # Check for settings.permissions.manage
    perm = Permission.query.filter_by(name='settings.permissions.manage').first()
    
    if not perm:
        print('❌ الصلاحية settings.permissions.manage غير موجودة!')
        exit(1)
    
    print(f'✅ تم العثور على الصلاحية: {perm.name_ar}')
    print()
    
    # Check if manager already has this permission
    if perm in manager_role.permissions:
        print('✅ دور manager لديه بالفعل صلاحية settings.permissions.manage')
    else:
        print('📝 إضافة صلاحية settings.permissions.manage لدور manager...')
        manager_role.permissions.append(perm)
        db.session.commit()
        print('✅ تم إضافة الصلاحية بنجاح!')
    
    print()
    print('='*80)
    print('📊 ملخص الصلاحيات المهمة لدور manager:')
    print('='*80)
    
    important_perms = [
        'settings.roles.edit',
        'settings.permissions.manage',
        'settings.roles.manage',
        'settings.roles.delete'
    ]
    
    for perm_name in important_perms:
        p = Permission.query.filter_by(name=perm_name).first()
        if p and p in manager_role.permissions:
            print(f'   ✅ {perm_name}')
        else:
            print(f'   ❌ {perm_name}')
    
    print()
    print('='*80)
    print('🎯 النتيجة:')
    print('='*80)
    print(f'إجمالي الصلاحيات لدور manager: {len(manager_role.permissions)}')
    print()
    print('الآن يمكن لمستخدمي دور manager:')
    print('  ✅ تعديل الأدوار')
    print('  ✅ إدارة الصلاحيات')
    print('  ✅ حذف الأدوار')
    print()
    
    # Check ali user
    ali = User.query.filter_by(username='ali').first()
    if ali and ali.role:
        print(f'👤 المستخدم ali:')
        print(f'   الدور: {ali.role.name_ar}')
        print(f'   عدد الصلاحيات: {len(ali.role.permissions)}')
        print()
        
        # Check if ali can manage permissions now
        can_manage = ali.has_permission('settings.permissions.manage')
        can_edit_roles = ali.has_permission('settings.roles.edit')
        
        print('   الصلاحيات المهمة:')
        print(f'   {"✅" if can_edit_roles else "❌"} settings.roles.edit')
        print(f'   {"✅" if can_manage else "❌"} settings.permissions.manage')
        print()
    
    print('='*80)
    print('✅ تم الإصلاح بنجاح!')
    print('='*80)
    print()
    print('💡 الخطوات التالية:')
    print('1. سجل الدخول بالمستخدم ali')
    print('2. اذهب إلى الإعدادات → إدارة الأدوار')
    print('3. اختر أي دور وقم بتعديل الصلاحيات')
    print('4. اضغط على "حفظ الصلاحيات"')
    print('5. يجب أن ترى رسالة نجاح مع عدد الصلاحيات المحفوظة')
    print()

