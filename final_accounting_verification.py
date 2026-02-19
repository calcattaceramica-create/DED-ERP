#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
التحقق النهائي الشامل من صلاحيات المحاسبة والبنوك
"""

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print("=" * 100)
    print("🔍 التحقق النهائي الشامل من صلاحيات المحاسبة والبنوك")
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
    
    # اختبار شامل
    tests = [
        {
            'name': '📊 المحاسبة العامة',
            'permissions': [
                ('accounting.view', True, 'عرض وحدة المحاسبة'),
            ]
        },
        {
            'name': '🏦 الحسابات البنكية',
            'permissions': [
                ('accounting.bank_accounts.view', True, 'عرض الحسابات البنكية'),
                ('accounting.accounts.view', True, 'عرض تفاصيل الحساب'),
                ('accounting.accounts.add', False, 'إضافة حساب بنكي'),
                ('accounting.accounts.edit', True, 'تعديل حساب بنكي'),
                ('accounting.accounts.delete', False, 'حذف حساب بنكي'),
            ]
        },
        {
            'name': '📝 القيود اليومية',
            'permissions': [
                ('accounting.transactions.view', True, 'عرض القيود'),
                ('accounting.transactions.create', True, 'إنشاء قيد'),
                ('accounting.transactions.edit', True, 'تعديل قيد'),
                ('accounting.transactions.delete', True, 'حذف قيد'),
            ]
        },
        {
            'name': '💰 المدفوعات',
            'permissions': [
                ('accounting.payments.view', True, 'عرض المدفوعات'),
                ('accounting.payments.add', True, 'إضافة مدفوعة'),
                ('accounting.payments.edit', True, 'تعديل مدفوعة'),
                ('accounting.payments.delete', True, 'حذف مدفوعة'),
            ]
        },
        {
            'name': '📈 التقارير',
            'permissions': [
                ('accounting.reports.view', True, 'عرض التقارير'),
                ('accounting.reports.trial_balance', True, 'ميزان المراجعة'),
                ('accounting.reports.income_statement', True, 'قائمة الدخل'),
                ('accounting.reports.balance_sheet', True, 'الميزانية العمومية'),
            ]
        },
    ]
    
    all_passed = True
    
    for test_group in tests:
        print(f"\n{test_group['name']}:")
        print("-" * 100)
        
        for perm_name, expected, description in test_group['permissions']:
            actual = user.has_permission(perm_name)
            
            if actual == expected:
                status = "✅"
            else:
                status = "❌"
                all_passed = False
            
            expected_str = "يجب أن يكون True" if expected else "يجب أن يكون False"
            actual_str = "True" if actual else "False"
            
            print(f"   {status} {description}")
            print(f"      الصلاحية: {perm_name}")
            print(f"      المتوقع: {expected_str} | الفعلي: {actual_str}")
            
            if actual != expected:
                print(f"      ⚠️  خطأ: الصلاحية لا تطابق المتوقع!")
    
    print("\n" + "=" * 100)
    
    if all_passed:
        print("✅ جميع الاختبارات نجحت!")
        print("✅ نظام الصلاحيات يعمل بشكل صحيح 100%")
        print("\n📋 ملخص:")
        print("   ✅ المستخدم ali يستطيع:")
        print("      - عرض جميع بيانات المحاسبة")
        print("      - تعديل الحسابات البنكية")
        print("      - إدارة القيود والمدفوعات")
        print("      - عرض التقارير")
        print("\n   ❌ المستخدم ali لا يستطيع:")
        print("      - إضافة حسابات بنكية جديدة")
        print("      - حذف حسابات بنكية")
    else:
        print("❌ بعض الاختبارات فشلت!")
        print("❌ يرجى مراجعة الصلاحيات أعلاه")
    
    print("=" * 100)

