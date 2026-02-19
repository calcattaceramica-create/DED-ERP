#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
إضافة صلاحيات الحسابات البنكية للمدير
Add Bank Account Permissions to Manager
"""

from app import create_app, db
from app.models import Role, Permission, RolePermission

def add_bank_permissions():
    """إضافة صلاحيات الحسابات البنكية"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("🔧 إضافة صلاحيات الحسابات البنكية للمدير")
        print("="*80 + "\n")
        
        # البحث عن دور المدير
        manager_role = Role.query.filter_by(name='manager').first()
        
        if not manager_role:
            print("❌ دور manager غير موجود!")
            return
        
        print(f"✅ الدور: {manager_role.name}")
        print(f"✅ عدد الصلاحيات الحالية: {len(manager_role.permissions)}")
        print()
        
        # الصلاحيات المطلوبة للحسابات البنكية
        required_permissions = [
            'accounting.accounts.add',
            'accounting.accounts.edit',
            'accounting.accounts.delete',
        ]
        
        added_count = 0
        
        for perm_name in required_permissions:
            # البحث عن الصلاحية
            permission = Permission.query.filter_by(name=perm_name).first()
            
            if not permission:
                print(f"⚠️ الصلاحية {perm_name} غير موجودة في قاعدة البيانات!")
                continue
            
            # التحقق إذا كانت موجودة بالفعل
            existing = RolePermission.query.filter_by(
                role_id=manager_role.id,
                permission_id=permission.id
            ).first()
            
            if existing:
                print(f"✅ الصلاحية {perm_name} موجودة بالفعل")
            else:
                # إضافة الصلاحية
                role_perm = RolePermission(
                    role_id=manager_role.id,
                    permission_id=permission.id
                )
                db.session.add(role_perm)
                added_count += 1
                print(f"✅ تمت إضافة الصلاحية: {perm_name}")
        
        if added_count > 0:
            db.session.commit()
            print()
            print(f"✅ تمت إضافة {added_count} صلاحية جديدة")
        else:
            print()
            print("ℹ️ جميع الصلاحيات موجودة بالفعل")
        
        # عرض العدد النهائي
        db.session.refresh(manager_role)
        print(f"✅ عدد الصلاحيات النهائي: {len(manager_role.permissions)}")
        
        print()
        print("="*80)
        print("✅ تم الانتهاء!")
        print("="*80 + "\n")
        
        # عرض جميع الصلاحيات المتعلقة بالمحاسبة
        print("="*80)
        print("📋 جميع الصلاحيات المحاسبية للمدير:")
        print("="*80)
        
        accounting_perms = sorted([p.name for p in manager_role.permissions if 'accounting' in p.name])
        for i, perm in enumerate(accounting_perms, 1):
            print(f"{i:2d}. {perm}")
        
        print()
        print("="*80)
        print(f"📊 الإجمالي: {len(accounting_perms)} صلاحية محاسبية")
        print("="*80 + "\n")

if __name__ == '__main__':
    add_bank_permissions()

