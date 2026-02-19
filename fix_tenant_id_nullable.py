"""
Fix tenant_id columns to allow NULL values
This script updates all tables to make tenant_id nullable
"""

from app import create_app, db
from sqlalchemy import text

app = create_app()

# List of tables that have tenant_id column
TABLES_WITH_TENANT_ID = [
    'users',
    'branches',
    'warehouses',
    'products',
    'product_categories',
    'units',
    'stock',
    'stock_movements',
    'damaged_inventory',
    'customers',
    'sales_invoices',
    'sales_invoice_items',
    'quotations',
    'quotation_items',
    'sales_orders',
    'suppliers',
    'purchase_orders',
    'purchase_order_items',
    'purchase_invoices',
    'purchase_invoice_items',
    'purchase_returns',
    'purchase_return_items',
    'accounts',
    'journal_entries',
    'journal_entry_items',
    'payments',
    'bank_accounts',
    'cost_centers',
    'bank_transactions',
    'expenses',
    'employees',
    'departments',
    'positions',
    'attendance',
    'leaves',
    'leave_types',
    'payrolls',
    'pos_sessions',
    'pos_orders',
    'pos_order_items',
    'system_settings',
    'accounting_settings',
    'leads',
    'interactions',
    'opportunities',
    'tasks',
    'campaigns',
    'contacts',
]

def fix_tenant_id_columns():
    """Make tenant_id columns nullable in all tables"""
    with app.app_context():
        print("🔧 Starting to fix tenant_id columns...")
        print("=" * 80)
        
        success_count = 0
        error_count = 0
        
        for table_name in TABLES_WITH_TENANT_ID:
            try:
                # Check if table exists
                check_query = text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = :table_name
                    )
                """)
                result = db.session.execute(check_query, {"table_name": table_name})
                table_exists = result.scalar()
                
                if not table_exists:
                    print(f"⏭️  Skipping {table_name} (table does not exist)")
                    continue
                
                # Check if tenant_id column exists
                check_column_query = text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = :table_name AND column_name = 'tenant_id'
                    )
                """)
                result = db.session.execute(check_column_query, {"table_name": table_name})
                column_exists = result.scalar()
                
                if not column_exists:
                    print(f"⏭️  Skipping {table_name} (tenant_id column does not exist)")
                    continue
                
                # Alter column to allow NULL
                alter_query = text(f"""
                    ALTER TABLE {table_name} 
                    ALTER COLUMN tenant_id DROP NOT NULL
                """)
                
                db.session.execute(alter_query)
                db.session.commit()
                
                print(f"✅ Fixed {table_name}")
                success_count += 1
                
            except Exception as e:
                print(f"❌ Error fixing {table_name}: {str(e)}")
                db.session.rollback()
                error_count += 1
        
        print("=" * 80)
        print(f"✅ Successfully fixed {success_count} tables")
        if error_count > 0:
            print(f"❌ Failed to fix {error_count} tables")
        print("🎉 Done!")

if __name__ == '__main__':
    fix_tenant_id_columns()

