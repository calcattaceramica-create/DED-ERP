"""
سكريبت لإعداد PostgreSQL تلقائياً
"""
import subprocess
import sys
import os

# مسار PostgreSQL
POSTGRES_PATH = r"C:\Program Files\PostgreSQL\16\bin"
PSQL_EXE = os.path.join(POSTGRES_PATH, "psql.exe")
PASSWORD = "calcatta123"

def check_postgresql():
    """التحقق من تثبيت PostgreSQL"""
    if not os.path.exists(PSQL_EXE):
        print("❌ PostgreSQL غير مثبت في المسار الافتراضي!")
        return False
    print("✅ PostgreSQL 16 مثبت بنجاح!")
    return True

def create_database():
    """إنشاء قاعدة البيانات ded_erp"""
    print("\n📋 جاري إنشاء قاعدة البيانات ded_erp...")
    
    env = os.environ.copy()
    env['PGPASSWORD'] = PASSWORD
    
    cmd = [
        PSQL_EXE,
        '-U', 'postgres',
        '-h', 'localhost',
        '-p', '5432',
        '-c', 'CREATE DATABASE ded_erp;'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ تم إنشاء قاعدة البيانات ded_erp بنجاح!")
            return True
        elif "already exists" in result.stderr:
            print("⚠️  قاعدة البيانات ded_erp موجودة بالفعل!")
            return True
        else:
            print(f"❌ خطأ في إنشاء قاعدة البيانات:")
            print(f"   {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def verify_database():
    """التحقق من وجود قاعدة البيانات"""
    print("\n🔍 جاري التحقق من قاعدة البيانات...")
    
    env = os.environ.copy()
    env['PGPASSWORD'] = PASSWORD
    
    cmd = [
        PSQL_EXE,
        '-U', 'postgres',
        '-h', 'localhost',
        '-p', '5432',
        '-l'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if 'ded_erp' in result.stdout:
            print("✅ قاعدة البيانات ded_erp موجودة وجاهزة!")
            return True
        else:
            print("❌ قاعدة البيانات ded_erp غير موجودة!")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في التحقق: {e}")
        return False

def install_psycopg2():
    """تثبيت psycopg2-binary"""
    print("\n📦 جاري تثبيت psycopg2-binary...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0 or "already satisfied" in result.stdout.lower():
            print("✅ psycopg2-binary جاهز!")
            return True
        else:
            print(f"❌ خطأ في التثبيت:")
            print(f"   {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 إعداد PostgreSQL لمشروع DED ERP")
    print("=" * 60)
    
    if not check_postgresql():
        return
    
    if not create_database():
        print("\n❌ فشل إنشاء قاعدة البيانات!")
        return
    
    if not verify_database():
        return
    
    if not install_psycopg2():
        return
    
    print("\n" + "=" * 60)
    print("✅ تم إعداد PostgreSQL بنجاح!")
    print("=" * 60)
    print("\n📋 الخطوة التالية:")
    print("   قم بتشغيل: python migrate_to_postgresql.py")
    print("=" * 60)

if __name__ == "__main__":
    main()

