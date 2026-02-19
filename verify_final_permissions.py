#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
التحقق النهائي من صلاحيات المدير
Final Verification of Manager Permissions
"""

from app import create_app, db
from app.models import User, Role

def verify_permissions():
    """التحقق النهائي من الصلاحيات"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("🎯 التحقق النهائي من صلاحيات المدير")
        print("🎯 Final Verification of Manager Permissions")
        print("="*80 + "\n")
        
        # البحث عن المدير
        manager = User.query.filter_by(username='ali').first()
        
        if not manager:
            print("❌ المستخدم ali غير موجود!")
            return
        
        print(f"✅ المستخدم: {manager.username}")
        print(f"✅ الدور: {manager.role.name if manager.role else 'لا يوجد'}")
        print(f"✅ هل هو admin: {manager.is_admin}")
        print(f"✅ عدد الصلاحيات الإجمالي: {len(manager.role.permissions)}")
        print()
        
        # اختبار الصلاحيات المطلوبة
        print("="*80)
        print("🧪 اختبار الصلاحيات المطلوبة للحسابات البنكية:")
        print("="*80)
        
        required_permissions = [
            ('accounting.view', 'عرض المحاسبة'),
            ('accounting.accounts.view', 'عرض الحسابات'),
            ('accounting.accounts.add', 'إضافة حسابات بنكية'),
            ('accounting.accounts.edit', 'تعديل حسابات بنكية'),
            ('accounting.accounts.delete', 'حذف حسابات بنكية'),
        ]
        
        all_passed = True
        for perm_name, description in required_permissions:
            has_it = manager.has_permission(perm_name)
            status = "✅ نعم" if has_it else "❌ لا"
            print(f"{status} | {perm_name:30s} | {description}")
            if not has_it:
                all_passed = False
        
        print()
        print("="*80)
        if all_passed:
            print("🎉 النتيجة: جميع الصلاحيات المطلوبة موجودة!")
            print("🎉 Result: All required permissions are present!")
            print()
            print("✅ المدير الآن يستطيع:")
            print("   1. عرض الحسابات البنكية")
            print("   2. إضافة حسابات بنكية جديدة")
            print("   3. تعديل الحسابات البنكية")
            print("   4. حذف الحسابات البنكية")
        else:
            print("❌ النتيجة: بعض الصلاحيات مفقودة!")
            print("❌ Result: Some permissions are missing!")
        print("="*80 + "\n")
        
        # عرض ملخص الصلاحيات المحاسبية
        print("="*80)
        print("📊 ملخص الصلاحيات المحاسبية:")
        print("="*80)
        
        accounting_perms = sorted([p.name for p in manager.role.permissions if 'accounting' in p.name])
        for i, perm in enumerate(accounting_perms, 1):
            marker = "🔹"
            if 'accounts.add' in perm or 'accounts.edit' in perm or 'accounts.delete' in perm:
                marker = "⭐"  # تمييز الصلاحيات المضافة حديثاً
            print(f"{marker} {i:2d}. {perm}")
        
        print()
        print(f"📊 الإجمالي: {len(accounting_perms)} صلاحية محاسبية")
        print("="*80 + "\n")

if __name__ == '__main__':
    verify_permissions()

