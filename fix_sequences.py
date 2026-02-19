#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
إصلاح تسلسلات PostgreSQL بعد نقل البيانات
"""

import psycopg2

# معلومات الاتصال
USERNAME = "postgres"
PASSWORD = "calcatta123"
HOST = "localhost"
PORT = "5432"
DATABASE = "ded_erp"

def fix_sequences():
    """إصلاح جميع التسلسلات في قاعدة البيانات"""
    print("=" * 100)
    print("🔧 إصلاح تسلسلات PostgreSQL")
    print("=" * 100)
    
    try:
        # الاتصال بـ PostgreSQL
        print("\n1️⃣ الاتصال بـ PostgreSQL...")
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            database=DATABASE,
            user=USERNAME,
            password=PASSWORD
        )
        cursor = conn.cursor()
        
        # الحصول على قائمة الجداول
        print("2️⃣ قراءة قائمة الجداول...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"   عدد الجداول: {len(tables)}\n")
        
        # إصلاح التسلسل لكل جدول
        print("3️⃣ إصلاح التسلسلات...\n")
        fixed_count = 0
        
        for table in tables:
            try:
                # محاولة إصلاح التسلسل
                cursor.execute(f"""
                    SELECT setval(
                        pg_get_serial_sequence('{table}', 'id'),
                        COALESCE((SELECT MAX(id) FROM {table}), 1),
                        true
                    )
                """)
                result = cursor.fetchone()
                
                if result and result[0]:
                    print(f"   ✅ {table}: التسلسل الجديد = {result[0]}")
                    fixed_count += 1
                else:
                    print(f"   ⚠️  {table}: لا يوجد عمود id أو الجدول فارغ")
                    
            except Exception as e:
                print(f"   ⚠️  {table}: {str(e)[:50]}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 100)
        print(f"✅ تم إصلاح {fixed_count} تسلسل بنجاح!")
        print("=" * 100)
        
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    fix_sequences()

