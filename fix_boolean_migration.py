#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
إصلاح نقل البيانات Boolean من SQLite إلى PostgreSQL
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_values

# معلومات الاتصال
USERNAME = "postgres"
PASSWORD = "calcatta123"
HOST = "localhost"
PORT = "5432"
DATABASE = "ded_erp"

# الجداول التي فشل نقلها
FAILED_TABLES = [
    'accounts',
    'bank_accounts',
    'branches',
    'categories',
    'customers',
    'products',
    'session_logs',
    'suppliers',
    'units',
    'users',
    'warehouses'
]

# الأعمدة Boolean في كل جدول
BOOLEAN_COLUMNS = {
    'accounts': ['is_active', 'is_system'],
    'bank_accounts': ['is_active'],
    'branches': ['is_active'],
    'categories': ['is_active'],
    'customers': ['is_active', 'is_supplier'],
    'products': ['is_active', 'track_inventory', 'allow_negative_stock', 'is_service'],
    'session_logs': ['is_active'],
    'suppliers': ['is_active', 'is_customer'],
    'units': ['is_active'],
    'users': ['is_active', 'is_admin'],
    'warehouses': ['is_active']
}

def convert_boolean(value):
    """تحويل القيمة إلى Boolean"""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes')
    return bool(value)

def migrate_table(sqlite_cursor, pg_cursor, pg_conn, table_name):
    """نقل جدول واحد مع تحويل Boolean"""
    print(f"\n   📊 نقل جدول: {table_name}")
    
    try:
        # قراءة البيانات من SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"      ⚠️  الجدول فارغ")
            return 0
        
        # الحصول على أسماء الأعمدة
        columns = [description[0] for description in sqlite_cursor.description]
        boolean_cols = BOOLEAN_COLUMNS.get(table_name, [])
        
        # تحويل البيانات
        converted_data = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            
            # تحويل الأعمدة Boolean
            for col in boolean_cols:
                if col in row_dict:
                    row_dict[col] = convert_boolean(row_dict[col])
            
            converted_data.append(tuple(row_dict.values()))
        
        # حذف البيانات القديمة
        pg_cursor.execute(f"DELETE FROM {table_name}")
        
        # تعطيل القيود المؤقتة
        pg_cursor.execute(f"ALTER TABLE {table_name} DISABLE TRIGGER ALL")
        
        # إدراج البيانات
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        pg_cursor.executemany(insert_query, converted_data)
        
        # إعادة تفعيل القيود
        pg_cursor.execute(f"ALTER TABLE {table_name} ENABLE TRIGGER ALL")
        
        pg_conn.commit()
        
        print(f"      ✅ تم نقل {len(converted_data)} صف")
        return len(converted_data)
        
    except Exception as e:
        print(f"      ❌ خطأ: {e}")
        pg_conn.rollback()
        return 0

def main():
    print("=" * 100)
    print("🔧 إصلاح نقل البيانات Boolean")
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
        
        # نقل الجداول
        print("\n3️⃣ نقل الجداول...")
        total_rows = 0
        
        for table_name in FAILED_TABLES:
            rows = migrate_table(sqlite_cursor, pg_cursor, pg_conn, table_name)
            total_rows += rows
        
        # إغلاق الاتصالات
        sqlite_conn.close()
        pg_conn.close()
        
        print("\n" + "=" * 100)
        print(f"✅ تم إصلاح ونقل {total_rows} صف بنجاح!")
        print("=" * 100)
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

