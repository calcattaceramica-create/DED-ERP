"""
Add bank_account_id columns to sales_invoices and purchase_invoices
إضافة عمود bank_account_id للفواتير
"""
from run import app, db

def add_columns():
    """Add bank_account_id columns"""
    with app.app_context():
        print("=== Adding bank_account_id columns ===")
        
        try:
            # Add column to sales_invoices
            try:
                db.session.execute(db.text(
                    "ALTER TABLE sales_invoices ADD COLUMN bank_account_id INTEGER REFERENCES bank_accounts(id)"
                ))
                db.session.commit()
                print("✅ Added bank_account_id to sales_invoices")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("ℹ️  bank_account_id already exists in sales_invoices")
                else:
                    print(f"⚠️  Error adding to sales_invoices: {str(e)}")
                db.session.rollback()
            
            # Add column to purchase_invoices
            try:
                db.session.execute(db.text(
                    "ALTER TABLE purchase_invoices ADD COLUMN bank_account_id INTEGER REFERENCES bank_accounts(id)"
                ))
                db.session.commit()
                print("✅ Added bank_account_id to purchase_invoices")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("ℹ️  bank_account_id already exists in purchase_invoices")
                else:
                    print(f"⚠️  Error adding to purchase_invoices: {str(e)}")
                db.session.rollback()
            
            print("\n=== Columns added successfully! ===")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    add_columns()

