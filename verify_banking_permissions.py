#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
التحقق من صلاحيات البنوك للمستخدم ali
"""

from app import create_app, db
from app.models import User, Permission

app = create_app()

with app.app_context():
    print("=" * 100)
    print("🏦 التحقق من صلاحيات البنوك للمستخدم ali")
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
    
    # صلاحيات الحسابات البنكية
    bank_permissions = [
        'accounting.view',
        'accounting.bank_accounts.view',
        'accounting.accounts.view',
        'accounting.accounts.add',
        'accounting.accounts.edit',
        'accounting.accounts.delete',
    ]
    
    print(f"\n🏦 صلاحيات الحسابات البنكية:")
    print("-" * 100)
    
    for perm_name in bank_permissions:
        has_perm = user.has_permission(perm_name)
        status = "✅" if has_perm else "❌"
        print(f"   {status} {perm_name}: {has_perm}")
        
        if not has_perm:
            # التحقق من وجودها في DB
            perm = Permission.query.filter_by(name=perm_name).first()
            if perm:
                print(f"      ⚠️  الصلاحية موجودة في DB (ID: {perm.id}) لكن غير مضافة لدور المدير!")
            else:
                print(f"      ❌ الصلاحية غير موجودة في DB!")
    
    print(f"\n📋 ملخص الصلاحيات:")
    print("-" * 100)
    
    can_view = user.has_permission('accounting.view') or user.has_permission('accounting.bank_accounts.view')
    can_add = user.has_permission('accounting.accounts.add')
    can_edit = user.has_permission('accounting.accounts.edit')
    can_delete = user.has_permission('accounting.accounts.delete')
    
    print(f"   {'✅' if can_view else '❌'} عرض الحسابات البنكية: {can_view}")
    print(f"   {'✅' if can_add else '❌'} إضافة حساب بنكي: {can_add}")
    print(f"   {'✅' if can_edit else '❌'} تعديل حساب بنكي: {can_edit}")
    print(f"   {'✅' if can_delete else '❌'} حذف حساب بنكي: {can_delete}")
    
    print(f"\n🔒 الحماية المتوقعة:")
    print("-" * 100)
    print(f"   Route: /bank-accounts - محمي بـ accounting.view")
    print(f"   Route: /bank-accounts/add - محمي بـ accounting.accounts.add")
    print(f"   Route: /bank-accounts/edit/<id> - محمي بـ accounting.accounts.edit")
    print(f"   Route: /bank-accounts/delete/<id> - محمي بـ accounting.accounts.delete")
    
    print("\n" + "=" * 100)
    
    if not can_add and not can_delete:
        print("✅ الحماية تعمل بشكل صحيح!")
        print("✅ المستخدم ali لا يستطيع إضافة أو حذف الحسابات البنكية")
        print("✅ لكنه يستطيع عرضها وتعديلها فقط")
    else:
        print("⚠️  تحذير: المستخدم لديه صلاحيات إضافة أو حذف!")
        if can_add:
            print("   ❌ يستطيع إضافة حسابات بنكية")
        if can_delete:
            print("   ❌ يستطيع حذف حسابات بنكية")
    
    print("=" * 100)

