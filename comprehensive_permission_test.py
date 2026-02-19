#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام الصلاحيات - فحص كل route في النظام
Comprehensive permission system test - check every route
"""

from app import create_app, db
from app.models import User, Permission, Role
import re

app = create_app()

# قائمة بجميع الملفات التي تحتوي على routes
ROUTE_FILES = [
    'app/accounting/routes.py',
    'app/inventory/routes.py',
    'app/sales/routes.py',
    'app/purchases/routes.py',
    'app/pos/routes.py',
    'app/hr/routes.py',
    'app/settings/routes.py',
    'app/main/routes.py',
]

def extract_routes_and_permissions(file_path):
    """استخراج جميع الـ routes والصلاحيات المطلوبة من ملف"""
    routes = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # البحث عن @bp.route و @permission_required
        route_pattern = r"@bp\.route\(['\"]([^'\"]+)['\"]"
        permission_pattern = r"@permission_required\(['\"]([^'\"]+)['\"]"
        
        lines = content.split('\n')
        current_route = None
        current_permissions = []
        
        for i, line in enumerate(lines):
            # البحث عن route
            route_match = re.search(route_pattern, line)
            if route_match:
                if current_route:
                    routes.append({
                        'route': current_route,
                        'permissions': current_permissions.copy()
                    })
                current_route = route_match.group(1)
                current_permissions = []
            
            # البحث عن permission
            perm_match = re.search(permission_pattern, line)
            if perm_match:
                current_permissions.append(perm_match.group(1))
        
        # إضافة آخر route
        if current_route:
            routes.append({
                'route': current_route,
                'permissions': current_permissions.copy()
            })
    
    except Exception as e:
        print(f"خطأ في قراءة {file_path}: {e}")
    
    return routes

def check_permission_exists(permission_name):
    """التحقق من وجود الصلاحية في قاعدة البيانات"""
    with app.app_context():
        perm = Permission.query.filter_by(name=permission_name).first()
        return perm is not None

print("\n" + "="*100)
print("🔍 فحص شامل لنظام الصلاحيات - Comprehensive Permission System Check")
print("="*100)

all_issues = []
total_routes = 0
protected_routes = 0
unprotected_routes = 0

for file_path in ROUTE_FILES:
    print(f"\n📁 فحص ملف: {file_path}")
    print("-" * 100)
    
    routes = extract_routes_and_permissions(file_path)
    
    for route_info in routes:
        total_routes += 1
        route = route_info['route']
        permissions = route_info['permissions']
        
        # تجاهل بعض الـ routes التي لا تحتاج صلاحيات
        skip_routes = ['/', '/login', '/logout', '/static', '/health']
        if any(skip in route for skip in skip_routes):
            continue
        
        if not permissions:
            unprotected_routes += 1
            issue = f"⚠️  Route غير محمي: {route} في {file_path}"
            print(issue)
            all_issues.append(issue)
        else:
            protected_routes += 1
            # التحقق من وجود الصلاحيات في قاعدة البيانات
            for perm in permissions:
                if not check_permission_exists(perm):
                    issue = f"❌ صلاحية غير موجودة: {perm} مطلوبة في {route}"
                    print(issue)
                    all_issues.append(issue)
                else:
                    print(f"   ✅ {route} -> {perm}")

print("\n" + "="*100)
print("📊 ملخص النتائج - Summary")
print("="*100)
print(f"إجمالي الـ Routes: {total_routes}")
print(f"Routes محمية: {protected_routes}")
print(f"Routes غير محمية: {unprotected_routes}")
print(f"إجمالي المشاكل: {len(all_issues)}")

if all_issues:
    print("\n" + "="*100)
    print("❌ المشاكل المكتشفة:")
    print("="*100)
    for issue in all_issues:
        print(issue)
else:
    print("\n✅ لا توجد مشاكل! جميع الـ Routes محمية بشكل صحيح!")

print("\n" + "="*100)

