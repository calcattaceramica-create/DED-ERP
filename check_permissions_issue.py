#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check permissions issue - verify current user permissions
"""

from app import create_app, db
from app.models import User, Role, Permission

app = create_app()

with app.app_context():
    print('='*80)
    print('🔍 فحص مشكلة الصلاحيات')
    print('='*80)
    print()
    
    # Check if settings.permissions.manage exists
    perm = Permission.query.filter_by(name='settings.permissions.manage').first()
    
    if perm:
        print('✅ الصلاحية settings.permissions.manage موجودة')
        print(f'   ID: {perm.id}')
        print(f'   الاسم بالعربي: {perm.name_ar}')
        print()
        
        # Check which roles have this permission
        print('📋 الأدوار التي لديها هذه الصلاحية:')
        for role in Role.query.all():
            if perm in role.permissions:
                print(f'   ✅ {role.name_ar} ({role.name})')
        print()
    else:
        print('❌ الصلاحية settings.permissions.manage غير موجودة!')
        print()
        print('💡 الحل: تغيير الصلاحية المطلوبة في route إلى settings.roles.edit')
        print()
    
    # Check settings.roles.edit permission
    perm2 = Permission.query.filter_by(name='settings.roles.edit').first()
    
    if perm2:
        print('✅ الصلاحية settings.roles.edit موجودة')
        print(f'   ID: {perm2.id}')
        print(f'   الاسم بالعربي: {perm2.name_ar}')
        print()
        
        # Check which roles have this permission
        print('📋 الأدوار التي لديها هذه الصلاحية:')
        for role in Role.query.all():
            if perm2 in role.permissions:
                print(f'   ✅ {role.name_ar} ({role.name})')
        print()
    else:
        print('❌ الصلاحية settings.roles.edit غير موجودة!')
        print()
    
    # Check current admin user
    admin = User.query.filter_by(username='admin').first()
    if admin and admin.role:
        print(f'👤 المستخدم admin لديه دور: {admin.role.name_ar}')
        print(f'   عدد الصلاحيات: {len(admin.role.permissions)}')
        print()
        
        # Check specific permissions
        print('🔍 فحص الصلاحيات المهمة:')
        important_perms = [
            'settings.roles.edit',
            'settings.permissions.manage',
            'settings.roles.manage',
            'settings.roles.delete'
        ]
        
        for perm_name in important_perms:
            has_perm = admin.has_permission(perm_name)
            status = '✅' if has_perm else '❌'
            print(f'   {status} {perm_name}')
    
    print()
    print('='*80)
    print('💡 التوصية:')
    print('='*80)
    print('يجب تغيير الصلاحية المطلوبة في route update_role_permissions')
    print('من: @permission_required("settings.permissions.manage")')
    print('إلى: @permission_required("settings.roles.edit")')
    print()

