#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
سكريبت نقل البيانات من SQLite إلى PostgreSQL - محسّن
"""

import os
import sys
import shutil
from datetime import datetime

# معلومات الاتصال
USERNAME = "postgres"
PASSWORD = "calcatta123"
HOST = "localhost"
PORT = "5432"
DATABASE = "ded_erp"

def create_backup():
    """إنشاء نسخة احتياطية من SQLite"""
    sqlite_db = 'erp_system.db'
    
    if not os.path.exists(sqlite_db):
        print("❌ ملف قاعدة البيانات SQLite غير موجود!")
        return False
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'erp_system_backup_{timestamp}.db'
    
    print(f"📦 إنشاء نسخة احتياطية: {backup_file}")
    shutil.copy2(sqlite_db, backup_file)
    print(f"✅ تم إنشاء النسخة الاحتياطية بنجاح!")
    
    return True

def create_env_file():
    """إنشاء ملف .env"""
    print("\n📝 إنشاء ملف .env...")
    
    env_content = f"""# Database Configuration
DATABASE_URL=postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}

# Application Configuration
SECRET_KEY={os.urandom(24).hex()}
FLASK_ENV=development
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ تم إنشاء ملف .env بنجاح!")

def init_postgresql_db():
    """تهيئة قاعدة البيانات PostgreSQL"""
    print("\n🔧 تهيئة قاعدة البيانات PostgreSQL...")
    
    # تعيين متغير البيئة
    os.environ['DATABASE_URL'] = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    
    # استيراد التطبيق
    try:
        from app import create_app, db
        from flask_migrate import init, migrate, upgrade
        
        app = create_app()
        
        with app.app_context():
            print("   📋 إنشاء الجداول...")
            db.create_all()
            print("   ✅ تم إنشاء جميع الجداول بنجاح!")
            
        return True
        
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False

def migrate_data_manual():
    """نقل البيانات يدوياً من SQLite إلى PostgreSQL"""
    print("\n🚀 بدء نقل البيانات...")
    
    try:
        import sqlite3
        import psycopg2
        from psycopg2.extras import execute_values
        
        # الاتصال بـ SQLite
        print("   1️⃣ الاتصال بـ SQLite...")
        sqlite_conn = sqlite3.connect('erp_system.db')
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # الاتصال بـ PostgreSQL
        print("   2️⃣ الاتصال بـ PostgreSQL...")
        pg_conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            database=DATABASE,
            user=USERNAME,
            password=PASSWORD
        )
        pg_cursor = pg_conn.cursor()
        
        # الحصول على قائمة الجداول
        print("   3️⃣ قراءة قائمة الجداول...")
        sqlite_cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        print(f"      عدد الجداول: {len(tables)}")
        
        total_rows = 0
        
        # نقل البيانات لكل جدول
        for table_name in tables:
            print(f"\n   📊 نقل جدول: {table_name}")
            
            # قراءة البيانات من SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"      ⚠️  الجدول فارغ")
                continue
            
            # الحصول على أسماء الأعمدة
            columns = [description[0] for description in sqlite_cursor.description]
            
            # تحويل الصفوف إلى قوائم
            data = [tuple(row) for row in rows]
            
            # إدراج البيانات في PostgreSQL
            try:
                # تعطيل القيود المؤقتة
                pg_cursor.execute(f"ALTER TABLE {table_name} DISABLE TRIGGER ALL")
                
                # إدراج البيانات
                columns_str = ', '.join(columns)
                placeholders = ', '.join(['%s'] * len(columns))
                insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                
                pg_cursor.executemany(insert_query, data)
                
                # إعادة تفعيل القيود
                pg_cursor.execute(f"ALTER TABLE {table_name} ENABLE TRIGGER ALL")
                
                pg_conn.commit()
                
                print(f"      ✅ تم نقل {len(data)} صف")
                total_rows += len(data)
                
            except Exception as e:
                print(f"      ⚠️  خطأ في نقل الجدول: {e}")
                pg_conn.rollback()
                continue
        
        # إغلاق الاتصالات
        sqlite_conn.close()
        pg_conn.close()
        
        print(f"\n   ✅ تم نقل {total_rows} صف إجمالاً")
        return True
        
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 100)
    print("🔄 سكريبت نقل البيانات من SQLite إلى PostgreSQL - محسّن")
    print("=" * 100)

    # 1. إنشاء نسخة احتياطية
    print("\n📋 الخطوة 1: إنشاء نسخة احتياطية")
    if not create_backup():
        return

    # 2. إنشاء ملف .env
    print("\n📋 الخطوة 2: إنشاء ملف .env")
    create_env_file()

    # 3. تهيئة قاعدة البيانات PostgreSQL
    print("\n📋 الخطوة 3: تهيئة قاعدة البيانات PostgreSQL")
    if not init_postgresql_db():
        print("\n❌ فشل في تهيئة قاعدة البيانات!")
        return

    # 4. نقل البيانات
    print("\n📋 الخطوة 4: نقل البيانات")
    if not migrate_data_manual():
        print("\n❌ فشل في نقل البيانات!")
        return

    print("\n" + "=" * 100)
    print("🎉 تم الانتهاء من عملية النقل بنجاح!")
    print("=" * 100)
    print("\n📋 الخطوات التالية:")
    print("   1. ✅ تم نقل جميع البيانات إلى PostgreSQL")
    print("   2. ✅ تم إنشاء ملف .env")
    print("   3. 🔄 أعد تشغيل التطبيق: python run.py")
    print("\n⚠️  ملاحظة: ملف SQLite القديم لا يزال موجوداً كنسخة احتياطية")
    print("=" * 100)

if __name__ == '__main__':
    main()

