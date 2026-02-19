#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام الصلاحيات
Comprehensive Permissions Test
"""

from app import create_app, db
from app.models import User, Role, Permission, RolePermission
from werkzeug.security import generate_password_hash

def test_permissions():
    """اختبار شامل للصلاحيات"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("🔍 اختبار شامل لنظام الصلاحيات")
        print("🔍 Comprehensive Permissions Test")
        print("="*80 + "\n")
        
        # 1. التحقق من المستخدم test_limited
        user = User.query.filter_by(username='test_limited').first()
        
        if not user:
            print("❌ المستخدم test_limited غير موجود!")
            print("❌ User test_limited not found!")
            return
        
        # الحصول على جميع الصلاحيات
        all_permissions = set()
        if user.role:
            for role_perm in user.role.permissions:
                all_permissions.add(role_perm.name)

        print(f"✅ المستخدم: {user.username}")
        print(f"✅ الدور: {user.role.name if user.role else 'لا يوجد'}")
        print(f"✅ عدد الصلاحيات: {len(all_permissions)}")
        print()
        
        # 2. اختبار الصلاحيات المتوقعة
        test_cases = [
            # صلاحيات يجب أن يملكها (view only)
            ('accounting.view', True, '✅ يملك صلاحية عرض المحاسبة'),
            ('inventory.products.view', True, '✅ يملك صلاحية عرض المنتجات'),
            ('sales.invoices.view', True, '✅ يملك صلاحية عرض فواتير المبيعات'),
            
            # صلاحيات يجب ألا يملكها (add/edit/delete)
            ('accounting.accounts.add', False, '❌ لا يملك صلاحية إضافة حسابات'),
            ('accounting.accounts.delete', False, '❌ لا يملك صلاحية حذف حسابات'),
            ('inventory.products.add', False, '❌ لا يملك صلاحية إضافة منتجات'),
            ('inventory.products.delete', False, '❌ لا يملك صلاحية حذف منتجات'),
            ('sales.invoices.add', False, '❌ لا يملك صلاحية إضافة فواتير'),
            ('sales.invoices.delete', False, '❌ لا يملك صلاحية حذف فواتير'),
            ('purchases.invoices.add', False, '❌ لا يملك صلاحية إضافة فواتير شراء'),
            ('hr.employees.add', False, '❌ لا يملك صلاحية إضافة موظفين'),
            ('hr.employees.delete', False, '❌ لا يملك صلاحية حذف موظفين'),
            ('settings.users.add', False, '❌ لا يملك صلاحية إضافة مستخدمين'),
        ]
        
        print("📋 نتائج الاختبار:")
        print("📋 Test Results:")
        print("-" * 80)
        
        all_passed = True
        for permission_name, should_have, message in test_cases:
            has_permission = user.has_permission(permission_name)
            
            if has_permission == should_have:
                print(f"✅ {message}")
            else:
                print(f"❌ فشل: {message}")
                print(f"   المتوقع: {should_have}, الفعلي: {has_permission}")
                all_passed = False
        
        print("-" * 80)
        
        if all_passed:
            print("\n🎉 جميع الاختبارات نجحت!")
            print("🎉 All tests passed!")
        else:
            print("\n⚠️ بعض الاختبارات فشلت!")
            print("⚠️ Some tests failed!")
        
        # 3. عرض جميع الصلاحيات
        print("\n" + "="*80)
        print("📜 جميع صلاحيات المستخدم test_limited:")
        print("📜 All permissions for user test_limited:")
        print("="*80)

        permissions = sorted(all_permissions)
        for i, perm in enumerate(permissions, 1):
            print(f"{i:2d}. {perm}")
        
        print("\n" + "="*80)
        print(f"📊 الإجمالي: {len(permissions)} صلاحية")
        print(f"📊 Total: {len(permissions)} permissions")
        print("="*80 + "\n")

if __name__ == '__main__':
    test_permissions()

