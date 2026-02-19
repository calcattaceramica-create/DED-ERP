#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
فحص عميق للمشكلة
Deep Investigation
"""

from app import create_app, db
from app.models import User, Role, Permission

def deep_investigation():
    """فحص عميق للمشكلة"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("🔍 فحص عميق للمشكلة")
        print("="*80 + "\n")
        
        # 1. فحص المستخدم ali
        ali = User.query.filter_by(username='ali').first()
        
        print("1️⃣ معلومات المستخدم ali:")
        print(f"   - الاسم: {ali.username}")
        print(f"   - الدور: {ali.role.name if ali.role else 'لا يوجد'}")
        print(f"   - is_admin: {ali.is_admin}")
        print(f"   - عدد الصلاحيات: {len(ali.role.permissions) if ali.role else 0}")
        print()
        
        # 2. اختبار has_permission مباشرة
        print("2️⃣ اختبار دالة has_permission:")
        test_perms = [
            'accounting.accounts.add',
            'accounting.accounts.edit',
            'accounting.accounts.delete',
        ]
        
        for perm in test_perms:
            result = ali.has_permission(perm)
            print(f"   - ali.has_permission('{perm}'): {result}")
        print()
        
        # 3. فحص الصلاحيات في قاعدة البيانات
        print("3️⃣ فحص الصلاحيات في قاعدة البيانات:")

        print(f"   - عدد الصلاحيات في الدور: {len(ali.role.permissions)}")

        # عرض الصلاحيات المتعلقة بالحسابات
        account_perms = [p for p in ali.role.permissions if 'accounts' in p.name]
        print(f"   - الصلاحيات المتعلقة بـ 'accounts':")
        for p in account_perms:
            print(f"     • {p.name}")
        print()
        
        # 4. فحص إذا كان هناك مستخدم آخر يستطيع الإضافة
        print("4️⃣ فحص جميع المستخدمين:")
        all_users = User.query.all()
        for user in all_users:
            can_add = user.has_permission('accounting.accounts.add')
            admin_mark = "👑" if user.is_admin else "👤"
            status = "✅" if can_add else "❌"
            print(f"   {admin_mark} {status} {user.username:15s} | is_admin={user.is_admin} | can_add={can_add}")
        print()
        
        # 5. فحص الـ decorator
        print("5️⃣ فحص الـ decorator في الكود:")
        print("   - يجب أن يكون: @permission_required('accounting.accounts.add')")
        print()
        
        # 6. اختبار محاكاة
        print("6️⃣ محاكاة الـ decorator:")
        from flask_login import current_user
        
        # محاكاة التحقق
        perm_name = 'accounting.accounts.add'
        
        print(f"   - الصلاحية المطلوبة: {perm_name}")
        print(f"   - ali.is_admin: {ali.is_admin}")
        
        if ali.is_admin:
            print("   ⚠️ المستخدم admin - سيتجاوز الفحص!")
        else:
            has_it = ali.has_permission(perm_name)
            print(f"   - ali.has_permission('{perm_name}'): {has_it}")
            
            if has_it:
                print("   ✅ سيُسمح بالوصول")
            else:
                print("   ❌ سيُرفض الوصول (403)")
        print()
        
        # 7. فحص الصلاحيات الفعلية في الدور
        print("7️⃣ جميع صلاحيات دور manager:")
        if ali.role:
            all_perm_names = sorted([p.name for p in ali.role.permissions])
            for i, perm in enumerate(all_perm_names, 1):
                marker = "⭐" if 'accounts' in perm else "  "
                print(f"   {marker} {i:2d}. {perm}")
        print()
        
        print("="*80)
        print("❓ السؤال المهم:")
        print("="*80)
        print("هل تستطيع الآن:")
        print("1. تسجيل الدخول بحساب ali")
        print("2. الذهاب إلى: http://localhost:5000/accounting/bank-accounts/add")
        print("3. هل تستطيع الوصول للصفحة؟")
        print("   - إذا نعم: ما هي رسالة الخطأ (إن وجدت)؟")
        print("   - إذا لا: ما هي الرسالة التي تظهر؟")
        print("="*80 + "\n")

if __name__ == '__main__':
    deep_investigation()

