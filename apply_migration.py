"""
Apply database migration for BankAccount fields
تطبيق تغييرات قاعدة البيانات لحقول BankAccount
"""

import sqlite3
import os

def apply_migration():
    """Apply the migration to add new fields to bank_accounts table"""

    db_path = 'erp_system.db'
    
    if not os.path.exists(db_path):
        print(f"❌ قاعدة البيانات غير موجودة: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 جاري تطبيق التغييرات على قاعدة البيانات...")
        print("=" * 60)
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(bank_accounts)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"✅ الحقول الموجودة حالياً: {len(columns)}")
        
        # Add account_type column
        if 'account_type' not in columns:
            print("➕ إضافة حقل account_type...")
            cursor.execute("ALTER TABLE bank_accounts ADD COLUMN account_type VARCHAR(20) DEFAULT 'current'")
            print("   ✅ تم إضافة account_type")
        else:
            print("   ⚠️  account_type موجود مسبقاً")
        
        # Add opening_balance column
        if 'opening_balance' not in columns:
            print("➕ إضافة حقل opening_balance...")
            cursor.execute("ALTER TABLE bank_accounts ADD COLUMN opening_balance FLOAT DEFAULT 0.0")
            print("   ✅ تم إضافة opening_balance")
        else:
            print("   ⚠️  opening_balance موجود مسبقاً")
        
        # Add notes column
        if 'notes' not in columns:
            print("➕ إضافة حقل notes...")
            cursor.execute("ALTER TABLE bank_accounts ADD COLUMN notes TEXT")
            print("   ✅ تم إضافة notes")
        else:
            print("   ⚠️  notes موجود مسبقاً")
        
        # Update existing records
        print("\n🔄 تحديث السجلات الموجودة...")
        cursor.execute("UPDATE bank_accounts SET account_type = 'current' WHERE account_type IS NULL")
        cursor.execute("UPDATE bank_accounts SET opening_balance = current_balance WHERE opening_balance IS NULL OR opening_balance = 0")
        
        # Commit changes
        conn.commit()
        
        # Verify changes
        cursor.execute("PRAGMA table_info(bank_accounts)")
        new_columns = [row[1] for row in cursor.fetchall()]
        
        print("\n" + "=" * 60)
        print(f"✅ عدد الحقول بعد التحديث: {len(new_columns)}")
        print("\n✅ الحقول الجديدة:")
        for col in ['account_type', 'opening_balance', 'notes']:
            if col in new_columns:
                print(f"   ✅ {col}")
            else:
                print(f"   ❌ {col} - لم يتم إضافته!")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ تم تطبيق جميع التغييرات بنجاح!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ حدث خطأ: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("تطبيق تغييرات قاعدة البيانات - BankAccount Migration")
    print("=" * 60)
    print()
    
    success = apply_migration()
    
    if success:
        print("\n✅ يمكنك الآن إعادة تشغيل التطبيق!")
        print("   python run.py")
    else:
        print("\n❌ فشل تطبيق التغييرات!")

