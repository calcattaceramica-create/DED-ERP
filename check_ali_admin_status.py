#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
فحص حالة admin للمدير ali
"""

from app import create_app, db
from app.models import User

def check_admin_status():
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("🔍 فحص حالة Admin")
        print("="*80 + "\n")
        
        # فحص جميع المستخدمين
        users = User.query.all()
        
        print(f"📊 عدد المستخدمين: {len(users)}\n")
        
        for user in users:
            admin_status = "✅ Admin" if user.is_admin else "❌ Not Admin"
            role_name = user.role.name if user.role else "لا يوجد دور"
            print(f"{admin_status} | {user.username:15s} | الدور: {role_name}")
        
        print("\n" + "="*80)
        print("⚠️ المشكلة:")
        print("="*80)
        print("إذا كان المستخدم is_admin = True، فإنه يتجاوز نظام الصلاحيات!")
        print("السطر 44-45 في app/models.py:")
        print("  if self.is_admin:")
        print("      return True")
        print()
        print("الحل: تغيير is_admin = False للمستخدمين الذين يجب أن يخضعوا لنظام الصلاحيات")
        print("="*80 + "\n")

if __name__ == '__main__':
    check_admin_status()

