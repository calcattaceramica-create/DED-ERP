#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
إصلاح كامل لنقل البيانات من SQLite إلى PostgreSQL
"""

import sqlite3
import psycopg2
import os

# معلومات الاتصال
USERNAME = "postgres"
PASSWORD = "calcatta123"
HOST = "localhost"
PORT = "5432"
DATABASE = "ded_erp"

def convert_boolean(value):
    """تحويل القيم إلى Boolean"""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes')
    return bool(value)

def get_table_columns_types(pg_cursor, table_name):
    """الحصول على أنواع الأعمدة من PostgreSQL"""
    pg_cursor.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
    """)
    return {row[0]: row[1] for row in pg_cursor.fetchall()}

def migrate_all_data():
    """نقل جميع البيانات مع إصلاح Boolean"""
    print("=" * 100)
    print("🔄 نقل كامل للبيانات من SQLite إلى PostgreSQL")
    print("=" * 100)
    
    try:
        # الاتصال بـ SQLite
        print("\n1️⃣ الاتصال بـ SQLite...")
        sqlite_conn = sqlite3.connect('erp_system.db')
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # الاتصال بـ PostgreSQL
        print("2️⃣ الاتصال بـ PostgreSQL...")
        pg_conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            database=DATABASE,
            user=USERNAME,
            password=PASSWORD
        )
        pg_cursor = pg_conn.cursor()
        
        # الحصول على قائمة الجداول
        print("3️⃣ قراءة قائمة الجداول...")
        sqlite_cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        print(f"   عدد الجداول: {len(tables)}")
        
        # حذف جميع البيانات أولاً (مع تعطيل القيود)
        print("\n4️⃣ حذف البيانات القديمة...")
        pg_cursor.execute("SET session_replication_role = 'replica';")
        
        for table in tables:
            try:
                pg_cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
                print(f"   ✅ تم حذف بيانات جدول: {table}")
            except Exception as e:
                print(f"   ⚠️  تخطي جدول: {table}")
        
        pg_conn.commit()
        
        # نقل البيانات
        print("\n5️⃣ نقل البيانات...")
        total_rows = 0
        
        for table_name in tables:
            print(f"\n   📊 نقل جدول: {table_name}")
            
            try:
                # قراءة البيانات من SQLite
                sqlite_cursor.execute(f"SELECT * FROM {table_name}")
                rows = sqlite_cursor.fetchall()
                
                if not rows:
                    print(f"      ⚠️  الجدول فارغ")
                    continue
                
                # الحصول على أسماء الأعمدة
                columns = [description[0] for description in sqlite_cursor.description]
                
                # الحصول على أنواع الأعمدة من PostgreSQL
                pg_columns_types = get_table_columns_types(pg_cursor, table_name)
                
                # تحويل البيانات
                converted_data = []
                for row in rows:
                    row_data = []
                    for i, col_name in enumerate(columns):
                        value = row[i]
                        
                        # تحويل Boolean
                        if pg_columns_types.get(col_name) == 'boolean':
                            value = convert_boolean(value)
                        
                        row_data.append(value)
                    
                    converted_data.append(tuple(row_data))
                
                # إدراج البيانات
                columns_str = ', '.join(columns)
                placeholders = ', '.join(['%s'] * len(columns))
                insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                
                pg_cursor.executemany(insert_query, converted_data)
                pg_conn.commit()
                
                print(f"      ✅ تم نقل {len(converted_data)} صف")
                total_rows += len(converted_data)
                
            except Exception as e:
                print(f"      ❌ خطأ: {e}")
                pg_conn.rollback()
                continue
        
        # إعادة تفعيل القيود
        print("\n6️⃣ إعادة تفعيل القيود...")
        pg_cursor.execute("SET session_replication_role = 'origin';")
        pg_conn.commit()
        
        # إغلاق الاتصالات
        sqlite_conn.close()
        pg_conn.close()
        
        print("\n" + "=" * 100)
        print(f"✅ تم نقل {total_rows} صف بنجاح!")
        print("=" * 100)
        
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    migrate_all_data()

