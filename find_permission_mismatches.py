#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
البحث عن عدم التطابق بين الصلاحيات في الكود وقاعدة البيانات
Find mismatches between permissions in code and database
"""

from app import create_app, db
from app.models import Permission
import re
import os

app = create_app()

# استخراج جميع الصلاحيات المستخدمة في الكود
def find_permissions_in_code():
    """البحث عن جميع الصلاحيات المستخدمة في ملفات routes"""
    permissions_in_code = set()
    
    # المجلدات التي تحتوي على routes
    route_dirs = ['app/accounting', 'app/inventory', 'app/sales', 'app/purchases', 
                  'app/pos', 'app/hr', 'app/settings', 'app/main']
    
    for route_dir in route_dirs:
        routes_file = os.path.join(route_dir, 'routes.py')
        if os.path.exists(routes_file):
            with open(routes_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # البحث عن @permission_required('permission.name')
            pattern = r"@permission_required\(['\"]([^'\"]+)['\"]"
            matches = re.findall(pattern, content)
            permissions_in_code.update(matches)
            
            # البحث عن @any_permission_required
            pattern2 = r"@any_permission_required\(['\"]([^'\"]+)['\"]"
            matches2 = re.findall(pattern2, content)
            permissions_in_code.update(matches2)
            
            # البحث عن @all_permissions_required
            pattern3 = r"@all_permissions_required\(['\"]([^'\"]+)['\"]"
            matches3 = re.findall(pattern3, content)
            permissions_in_code.update(matches3)
    
    return permissions_in_code

# استخراج جميع الصلاحيات من قاعدة البيانات
def get_permissions_from_db():
    """الحصول على جميع الصلاحيات من قاعدة البيانات"""
    with app.app_context():
        perms = Permission.query.all()
        return {p.name for p in perms}

print("\n" + "="*100)
print("🔍 البحث عن عدم التطابق بين الصلاحيات في الكود وقاعدة البيانات")
print("="*100)

# الحصول على الصلاحيات
permissions_in_code = find_permissions_in_code()
permissions_in_db = get_permissions_from_db()

print(f"\n📊 الإحصائيات:")
print(f"   - صلاحيات في الكود: {len(permissions_in_code)}")
print(f"   - صلاحيات في قاعدة البيانات: {len(permissions_in_db)}")

# الصلاحيات الموجودة في الكود ولكن غير موجودة في قاعدة البيانات
missing_in_db = permissions_in_code - permissions_in_db
if missing_in_db:
    print(f"\n❌ صلاحيات مستخدمة في الكود ولكن غير موجودة في قاعدة البيانات ({len(missing_in_db)}):")
    for perm in sorted(missing_in_db):
        print(f"   - {perm}")
else:
    print(f"\n✅ جميع الصلاحيات المستخدمة في الكود موجودة في قاعدة البيانات")

# الصلاحيات الموجودة في قاعدة البيانات ولكن غير مستخدمة في الكود
unused_in_code = permissions_in_db - permissions_in_code
if unused_in_code:
    print(f"\n⚠️  صلاحيات موجودة في قاعدة البيانات ولكن غير مستخدمة في الكود ({len(unused_in_code)}):")
    for perm in sorted(unused_in_code):
        print(f"   - {perm}")

# عرض جميع الصلاحيات المستخدمة في الكود مع حالتها
print(f"\n📋 جميع الصلاحيات المستخدمة في الكود:")
print("-" * 100)
for perm in sorted(permissions_in_code):
    status = "✅" if perm in permissions_in_db else "❌"
    print(f"{status} {perm}")

print("\n" + "="*100)

