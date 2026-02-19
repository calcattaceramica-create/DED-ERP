"""
Update database to add bank transactions and expenses tables
تحديث قاعدة البيانات لإضافة جداول حركات البنك والمصروفات
"""
from run import app, db
from app.models import BankTransaction, Expense, BankAccount, SalesInvoice, PurchaseInvoice

def update_database():
    """Create new tables and add new columns"""
    with app.app_context():
        print("=== Starting database update ===")
        
        try:
            # Create all tables (will only create new ones)
            db.create_all()
            print("✅ Tables created successfully!")
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("\n📊 Available tables:")
            for table in sorted(tables):
                print(f"  - {table}")
            
            # Check bank_transactions table
            if 'bank_transactions' in tables:
                print("\n✅ bank_transactions table exists")
                columns = [col['name'] for col in inspector.get_columns('bank_transactions')]
                print(f"   Columns: {', '.join(columns)}")
            else:
                print("\n❌ bank_transactions table NOT found")
            
            # Check expenses table
            if 'expenses' in tables:
                print("\n✅ expenses table exists")
                columns = [col['name'] for col in inspector.get_columns('expenses')]
                print(f"   Columns: {', '.join(columns)}")
            else:
                print("\n❌ expenses table NOT found")
            
            # Check if bank_account_id exists in sales_invoices
            if 'sales_invoices' in tables:
                columns = [col['name'] for col in inspector.get_columns('sales_invoices')]
                if 'bank_account_id' in columns:
                    print("\n✅ bank_account_id column exists in sales_invoices")
                else:
                    print("\n⚠️  bank_account_id column NOT found in sales_invoices")
                    print("   You may need to add it manually or recreate the table")
            
            # Check if bank_account_id exists in purchase_invoices
            if 'purchase_invoices' in tables:
                columns = [col['name'] for col in inspector.get_columns('purchase_invoices')]
                if 'bank_account_id' in columns:
                    print("\n✅ bank_account_id column exists in purchase_invoices")
                else:
                    print("\n⚠️  bank_account_id column NOT found in purchase_invoices")
                    print("   You may need to add it manually or recreate the table")
            
            # Count existing records
            bank_accounts_count = BankAccount.query.count()
            print(f"\n📈 Statistics:")
            print(f"   Bank Accounts: {bank_accounts_count}")
            
            if bank_accounts_count == 0:
                print("\n⚠️  No bank accounts found. You should create at least one bank account first.")
            
            print("\n=== Database update completed successfully! ===")
            
        except Exception as e:
            print(f"\n❌ Error updating database: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    update_database()

