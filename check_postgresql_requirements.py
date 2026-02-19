#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
التحقق من متطلبات PostgreSQL
"""

import sys
import subprocess

def check_psycopg2():
    """التحقق من تثبيت psycopg2"""
    print("=" * 100)
    print("🔍 التحقق من المتطلبات")
    print("=" * 100)
    
    print("\n1️⃣ التحقق من مكتبة psycopg2...")
    
    try:
        import psycopg2
        print(f"   ✅ psycopg2 مثبتة - الإصدار: {psycopg2.__version__}")
        return True
    except ImportError:
        print("   ❌ psycopg2 غير مثبتة!")
        print("\n   📦 لتثبيتها، قم بتشغيل:")
        print("      pip install psycopg2-binary")
        
        install = input("\n   هل تريد تثبيتها الآن؟ (y/n): ").strip().lower()
        
        if install == 'y':
            print("\n   📥 جاري التثبيت...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
                print("   ✅ تم التثبيت بنجاح!")
                return True
            except Exception as e:
                print(f"   ❌ فشل التثبيت: {e}")
                return False
        else:
            return False

def check_postgresql_service():
    """التحقق من خدمة PostgreSQL"""
    print("\n2️⃣ التحقق من خدمة PostgreSQL...")
    
    try:
        # محاولة الاتصال بـ PostgreSQL على المنفذ الافتراضي
        import socket
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 5432))
        sock.close()
        
        if result == 0:
            print("   ✅ خدمة PostgreSQL تعمل على المنفذ 5432")
            return True
        else:
            print("   ⚠️  لا يمكن الاتصال بـ PostgreSQL على المنفذ 5432")
            print("   📝 تأكد من:")
            print("      - تثبيت PostgreSQL")
            print("      - تشغيل خدمة PostgreSQL")
            print("      - المنفذ 5432 غير محجوب")
            return False
            
    except Exception as e:
        print(f"   ⚠️  خطأ في التحقق: {e}")
        return False

def check_sqlite_database():
    """التحقق من وجود قاعدة SQLite"""
    print("\n3️⃣ التحقق من قاعدة بيانات SQLite...")
    
    import os
    
    if os.path.exists('erp_system.db'):
        size = os.path.getsize('erp_system.db')
        size_mb = size / (1024 * 1024)
        print(f"   ✅ قاعدة البيانات موجودة - الحجم: {size_mb:.2f} MB")
        return True
    else:
        print("   ❌ قاعدة البيانات غير موجودة!")
        return False

def check_python_version():
    """التحقق من إصدار Python"""
    print("\n4️⃣ التحقق من إصدار Python...")
    
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print("   ✅ الإصدار مناسب")
        return True
    else:
        print("   ⚠️  يفضل Python 3.7 أو أحدث")
        return True

def main():
    print("=" * 100)
    print("🔧 فحص متطلبات التحويل إلى PostgreSQL")
    print("=" * 100)
    
    checks = [
        ("Python", check_python_version()),
        ("SQLite Database", check_sqlite_database()),
        ("psycopg2", check_psycopg2()),
        ("PostgreSQL Service", check_postgresql_service()),
    ]
    
    print("\n" + "=" * 100)
    print("📊 ملخص الفحص")
    print("=" * 100)
    
    all_passed = True
    
    for name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"   {status} {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 100)
    
    if all_passed:
        print("✅ جميع المتطلبات متوفرة!")
        print("\n📋 الخطوة التالية:")
        print("   قم بتشغيل: python migrate_to_postgresql.py")
    else:
        print("⚠️  بعض المتطلبات غير متوفرة!")
        print("\n📋 يرجى إكمال المتطلبات الناقصة أولاً")
    
    print("=" * 100)

if __name__ == '__main__':
    main()

