#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check if user is admin"""

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("فحص حالة المستخدمين")
    print("="*60)
    
    users = User.query.all()
    for user in users:
        print(f"\n👤 {user.username}")
        print(f"   الاسم الكامل: {user.full_name}")
        print(f"   is_admin: {user.is_admin}")
        print(f"   الدور: {user.role.name_ar if user.role else 'لا يوجد'}")
        print(f"   نشط: {user.is_active}")
    
    print("\n" + "="*60)

