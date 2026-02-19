#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
سكريبت نقل البيانات من SQLite إلى PostgreSQL
"""

import os
import sys
import shutil
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

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

def get_postgresql_url():
    """الحصول على رابط PostgreSQL من المستخدم"""
    print("\n" + "=" * 100)
    print("🔧 إعداد اتصال PostgreSQL")
    print("=" * 100)
    
    print("\nالرجاء إدخال معلومات الاتصال بقاعدة البيانات PostgreSQL:")
    print("(اضغط Enter لاستخدام القيمة الافتراضية)")
    
    host = input("\n1. Host [localhost]: ").strip() or "localhost"
    port = input("2. Port [5432]: ").strip() or "5432"
    database = input("3. Database name [ded_erp]: ").strip() or "ded_erp"
    username = input("4. Username [postgres]: ").strip() or "postgres"
    password = input("5. Password: ").strip()
    
    if not password:
        print("❌ كلمة المرور مطلوبة!")
        return None
    
    pg_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    print(f"\n📝 رابط الاتصال: postgresql://{username}:****@{host}:{port}/{database}")
    
    confirm = input("\nهل المعلومات صحيحة؟ (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ تم الإلغاء")
        return None
    
    return pg_url, username, password, host, port, database

def test_postgresql_connection(pg_url):
    """اختبار الاتصال بـ PostgreSQL"""
    print("\n🔍 اختبار الاتصال بـ PostgreSQL...")
    
    try:
        engine = create_engine(pg_url)
        connection = engine.connect()
        connection.close()
        print("✅ الاتصال بـ PostgreSQL ناجح!")
        return True
    except Exception as e:
        print(f"❌ فشل الاتصال بـ PostgreSQL: {e}")
        return False

def migrate_data(sqlite_url, pg_url):
    """نقل البيانات من SQLite إلى PostgreSQL"""
    print("\n" + "=" * 100)
    print("🚀 بدء عملية نقل البيانات")
    print("=" * 100)
    
    try:
        # الاتصال بقاعدتي البيانات
        print("\n1️⃣ الاتصال بقاعدة البيانات SQLite...")
        sqlite_engine = create_engine(sqlite_url)
        
        print("2️⃣ الاتصال بقاعدة البيانات PostgreSQL...")
        pg_engine = create_engine(pg_url)
        
        # قراءة البيانات من SQLite
        print("\n3️⃣ قراءة هيكل الجداول من SQLite...")
        metadata = MetaData()
        metadata.reflect(bind=sqlite_engine)
        
        tables = metadata.sorted_tables
        print(f"   عدد الجداول: {len(tables)}")
        
        # إنشاء الجداول في PostgreSQL
        print("\n4️⃣ إنشاء الجداول في PostgreSQL...")
        metadata.create_all(pg_engine)
        print("   ✅ تم إنشاء جميع الجداول")
        
        # نقل البيانات
        print("\n5️⃣ نقل البيانات...")
        
        SQLiteSession = sessionmaker(bind=sqlite_engine)
        PGSession = sessionmaker(bind=pg_engine)
        
        sqlite_session = SQLiteSession()
        pg_session = PGSession()
        
        total_rows = 0
        
        for table in tables:
            table_name = table.name
            print(f"\n   📊 نقل جدول: {table_name}")
            
            # قراءة البيانات من SQLite
            sqlite_conn = sqlite_engine.connect()
            rows = sqlite_conn.execute(table.select()).fetchall()
            row_count = len(rows)
            
            if row_count > 0:
                # إدراج البيانات في PostgreSQL
                pg_conn = pg_engine.connect()
                
                for row in rows:
                    pg_conn.execute(table.insert().values(**dict(row._mapping)))
                
                pg_conn.commit()
                pg_conn.close()
                
                print(f"      ✅ تم نقل {row_count} صف")
                total_rows += row_count
            else:
                print(f"      ⚠️  الجدول فارغ")
            
            sqlite_conn.close()
        
        sqlite_session.close()
        pg_session.close()
        
        print("\n" + "=" * 100)
        print(f"✅ تم نقل جميع البيانات بنجاح!")
        print(f"📊 إجمالي الصفوف المنقولة: {total_rows}")
        print("=" * 100)
        
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ أثناء نقل البيانات: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_env_file(username, password, host, port, database):
    """إنشاء ملف .env"""
    print("\n📝 إنشاء ملف .env...")
    
    env_content = f"""# Database Configuration
DATABASE_URL=postgresql://{username}:{password}@{host}:{port}/{database}

# Application Configuration
SECRET_KEY={os.urandom(24).hex()}
FLASK_ENV=development
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ تم إنشاء ملف .env بنجاح!")

def main():
    print("=" * 100)
    print("🔄 سكريبت نقل البيانات من SQLite إلى PostgreSQL")
    print("=" * 100)
    
    # 1. إنشاء نسخة احتياطية
    if not create_backup():
        return
    
    # 2. الحصول على معلومات PostgreSQL
    pg_info = get_postgresql_url()
    if not pg_info:
        return
    
    pg_url, username, password, host, port, database = pg_info
    
    # 3. اختبار الاتصال
    if not test_postgresql_connection(pg_url):
        return
    
    # 4. نقل البيانات
    sqlite_url = 'sqlite:///erp_system.db'
    
    if migrate_data(sqlite_url, pg_url):
        # 5. إنشاء ملف .env
        create_env_file(username, password, host, port, database)
        
        print("\n" + "=" * 100)
        print("🎉 تم الانتهاء من عملية النقل بنجاح!")
        print("=" * 100)
        print("\n📋 الخطوات التالية:")
        print("   1. ✅ تم نقل جميع البيانات إلى PostgreSQL")
        print("   2. ✅ تم إنشاء ملف .env")
        print("   3. 🔄 أعد تشغيل التطبيق")
        print("\n⚠️  ملاحظة: ملف SQLite القديم لا يزال موجوداً كنسخة احتياطية")
        print("=" * 100)
    else:
        print("\n❌ فشلت عملية النقل!")

if __name__ == '__main__':
    main()

