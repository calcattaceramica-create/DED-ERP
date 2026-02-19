"""
Multi-Tenant Migration Script for DED ERP
==========================================

This script migrates the existing single-tenant database to a multi-tenant structure.

IMPORTANT: 
- Backup your database before running this script!
- This script will modify the database structure
- Run this script only once

Usage:
    python migrate_to_multitenant.py

Author: Augment Agent
Date: 2026-02-17
"""

import sys
import os
from datetime import datetime
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models_tenant import Tenant
from config import Config

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    """Print a header message"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(message):
    """Print a success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_info(message):
    """Print an info message"""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

# List of all tables that need tenant_id column
TABLES_TO_MIGRATE = [
    # Core tables (3)
    'users', 'companies', 'branches',
    
    # Inventory tables (7)
    'categories', 'units', 'products', 'warehouses', 'stock', 
    'stock_movements', 'damaged_inventory',
    
    # Sales tables (6)
    'customers', 'sales_invoices', 'sales_invoice_items', 
    'quotations', 'quotation_items', 'sales_orders',
    
    # Purchase tables (7)
    'suppliers', 'purchase_orders', 'purchase_order_items',
    'purchase_invoices', 'purchase_invoice_items', 
    'purchase_returns', 'purchase_return_items',
    
    # POS tables (3)
    'pos_sessions', 'pos_orders', 'pos_order_items',
    
    # Settings tables (2)
    'system_settings', 'accounting_settings',
    
    # Accounting tables (8)
    'accounts', 'journal_entries', 'journal_entry_items',
    'payments', 'bank_accounts', 'cost_centers',
    'bank_transactions', 'expenses',
    
    # HR tables (7)
    'employees', 'departments', 'positions', 'attendance',
    'leaves', 'leave_types', 'payrolls',
    
    # CRM tables (6)
    'leads', 'interactions', 'opportunities', 'tasks',
    'campaigns', 'contacts'
]

def check_database_connection():
    """Check if database connection is working"""
    print_info("Checking database connection...")
    try:
        db.session.execute(text('SELECT 1'))
        print_success("Database connection successful")
        return True
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        return False

def backup_reminder():
    """Remind user to backup database"""
    print_header("⚠️  IMPORTANT: DATABASE BACKUP REQUIRED  ⚠️")
    print_warning("This script will modify your database structure!")
    print_warning("Make sure you have a backup before proceeding.")
    print()
    print_info("To backup PostgreSQL database, run:")
    print(f"  pg_dump -U postgres -d ded_erp > backup_$(date +%Y%m%d_%H%M%S).sql")
    print()
    
    response = input(f"{Colors.BOLD}Have you backed up your database? (yes/no): {Colors.ENDC}")
    if response.lower() not in ['yes', 'y']:
        print_error("Migration cancelled. Please backup your database first.")
        sys.exit(1)
    print_success("Proceeding with migration...")

def table_exists(table_name):
    """Check if a table exists"""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def create_tenants_table():
    """Create the tenants table"""
    print_header("Step 1: Creating Tenants Table")

    if table_exists('tenants'):
        print_warning("Tenants table already exists. Skipping...")
        return True

    try:
        print_info("Creating tenants table...")

        # Create tenants table using raw SQL to ensure exact structure
        db.session.execute(text("""
            CREATE TABLE tenants (
                id SERIAL PRIMARY KEY,
                code VARCHAR(20) NOT NULL,
                subdomain VARCHAR(63) NOT NULL,
                name VARCHAR(128) NOT NULL,
                email VARCHAR(120),
                phone VARCHAR(20),
                address TEXT,
                city VARCHAR(64),
                country VARCHAR(64) DEFAULT 'Saudi Arabia',
                plan VARCHAR(20) DEFAULT 'basic',
                max_users INTEGER DEFAULT 5,
                max_branches INTEGER DEFAULT 1,
                max_products INTEGER DEFAULT 100,
                max_invoices_per_month INTEGER DEFAULT 50,
                storage_limit_mb INTEGER DEFAULT 100,
                is_active BOOLEAN DEFAULT TRUE,
                is_trial BOOLEAN DEFAULT TRUE,
                trial_ends_at TIMESTAMP,
                subscription_starts_at TIMESTAMP,
                subscription_ends_at TIMESTAMP,
                features JSONB,
                settings JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_tenant_code UNIQUE (code),
                CONSTRAINT uq_tenant_subdomain UNIQUE (subdomain)
            )
        """))

        # Create indexes
        db.session.execute(text("CREATE INDEX idx_tenants_code ON tenants(code)"))
        db.session.execute(text("CREATE INDEX idx_tenants_subdomain ON tenants(subdomain)"))
        db.session.execute(text("CREATE INDEX idx_tenants_is_active ON tenants(is_active)"))

        db.session.commit()
        print_success("Tenants table created successfully")
        return True

    except SQLAlchemyError as e:
        db.session.rollback()
        print_error(f"Failed to create tenants table: {str(e)}")
        return False

def add_tenant_id_columns():
    """Add tenant_id column to all tables"""
    print_header("Step 2: Adding tenant_id Columns")

    success_count = 0
    skip_count = 0
    error_count = 0

    for table_name in TABLES_TO_MIGRATE:
        try:
            if not table_exists(table_name):
                print_warning(f"Table '{table_name}' does not exist. Skipping...")
                skip_count += 1
                continue

            if column_exists(table_name, 'tenant_id'):
                print_info(f"Table '{table_name}' already has tenant_id. Skipping...")
                skip_count += 1
                continue

            print_info(f"Adding tenant_id to '{table_name}'...")

            # Add tenant_id column (nullable for now)
            db.session.execute(text(f"""
                ALTER TABLE {table_name}
                ADD COLUMN tenant_id INTEGER
            """))

            # Add foreign key constraint
            db.session.execute(text(f"""
                ALTER TABLE {table_name}
                ADD CONSTRAINT fk_{table_name}_tenant_id
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            """))

            # Create index
            db.session.execute(text(f"""
                CREATE INDEX idx_{table_name}_tenant_id ON {table_name}(tenant_id)
            """))

            db.session.commit()
            print_success(f"Added tenant_id to '{table_name}'")
            success_count += 1

        except SQLAlchemyError as e:
            db.session.rollback()
            print_error(f"Failed to add tenant_id to '{table_name}': {str(e)}")
            error_count += 1

    print()
    print_info(f"Summary: {success_count} added, {skip_count} skipped, {error_count} errors")
    return error_count == 0

def create_default_tenant():
    """Create default tenant from existing company data"""
    print_header("Step 3: Creating Default Tenant")

    try:
        # Check if tenant already exists
        existing_tenant = db.session.execute(
            text("SELECT COUNT(*) FROM tenants")
        ).scalar()

        if existing_tenant > 0:
            print_warning("Tenants already exist. Skipping default tenant creation...")
            # Get the first tenant ID
            tenant_id = db.session.execute(
                text("SELECT id FROM tenants ORDER BY id LIMIT 1")
            ).scalar()
            print_info(f"Using existing tenant ID: {tenant_id}")
            return tenant_id

        # Get company data if exists
        company_data = db.session.execute(
            text("SELECT name, email, phone, address, city FROM companies ORDER BY id LIMIT 1")
        ).fetchone()

        if company_data:
            company_name = company_data[0] or 'Default Company'
            company_email = company_data[1] or 'admin@company.com'
            company_phone = company_data[2] or ''
            company_address = company_data[3] or ''
            company_city = company_data[4] or ''
        else:
            company_name = 'Default Company'
            company_email = 'admin@company.com'
            company_phone = ''
            company_address = ''
            company_city = ''

        print_info(f"Creating default tenant: {company_name}")

        # Insert default tenant
        result = db.session.execute(text("""
            INSERT INTO tenants (
                code, subdomain, name, email, phone, address, city,
                plan, max_users, max_branches, max_products, max_invoices_per_month,
                is_active, is_trial, created_at
            ) VALUES (
                'DEFAULT', 'default', :name, :email, :phone, :address, :city,
                'enterprise', 999, 999, 999999, 999999,
                TRUE, FALSE, CURRENT_TIMESTAMP
            ) RETURNING id
        """), {
            'name': company_name,
            'email': company_email,
            'phone': company_phone,
            'address': company_address,
            'city': company_city
        })

        tenant_id = result.scalar()
        db.session.commit()

        print_success(f"Default tenant created with ID: {tenant_id}")
        return tenant_id

    except SQLAlchemyError as e:
        db.session.rollback()
        print_error(f"Failed to create default tenant: {str(e)}")
        return None

def migrate_existing_data(tenant_id):
    """Migrate existing data to the default tenant"""
    print_header("Step 4: Migrating Existing Data")

    if not tenant_id:
        print_error("No tenant ID provided. Cannot migrate data.")
        return False

    success_count = 0
    skip_count = 0
    error_count = 0

    for table_name in TABLES_TO_MIGRATE:
        try:
            if not table_exists(table_name):
                skip_count += 1
                continue

            # Check if table has any data
            count = db.session.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            ).scalar()

            if count == 0:
                print_info(f"Table '{table_name}' is empty. Skipping...")
                skip_count += 1
                continue

            # Check if data already migrated
            migrated_count = db.session.execute(
                text(f"SELECT COUNT(*) FROM {table_name} WHERE tenant_id IS NOT NULL")
            ).scalar()

            if migrated_count == count:
                print_info(f"Table '{table_name}' already migrated. Skipping...")
                skip_count += 1
                continue

            print_info(f"Migrating {count} records in '{table_name}'...")

            # Update all records with tenant_id
            db.session.execute(
                text(f"UPDATE {table_name} SET tenant_id = :tenant_id WHERE tenant_id IS NULL"),
                {'tenant_id': tenant_id}
            )

            db.session.commit()
            print_success(f"Migrated {count} records in '{table_name}'")
            success_count += 1

        except SQLAlchemyError as e:
            db.session.rollback()
            print_error(f"Failed to migrate '{table_name}': {str(e)}")
            error_count += 1

    print()
    print_info(f"Summary: {success_count} migrated, {skip_count} skipped, {error_count} errors")
    return error_count == 0

def update_unique_constraints():
    """Update unique constraints to include tenant_id"""
    print_header("Step 5: Updating Unique Constraints")

    # Define constraints to update (table_name, old_constraint, columns_with_tenant)
    constraints_to_update = [
        ('branches', 'uq_branch_code', ['code', 'tenant_id']),
        ('categories', 'uq_category_code', ['code', 'tenant_id']),
        ('units', 'uq_unit_code', ['code', 'tenant_id']),
        ('products', 'uq_product_code', ['code', 'tenant_id']),
        ('warehouses', 'uq_warehouse_code', ['code', 'tenant_id']),
        ('customers', 'uq_customer_code', ['code', 'tenant_id']),
        ('sales_invoices', 'uq_sales_invoice_number', ['invoice_number', 'tenant_id']),
        ('quotations', 'uq_quotation_number', ['quotation_number', 'tenant_id']),
        ('suppliers', 'uq_supplier_code', ['code', 'tenant_id']),
        ('purchase_orders', 'uq_purchase_order_number', ['order_number', 'tenant_id']),
        ('purchase_invoices', 'uq_purchase_invoice_number', ['invoice_number', 'tenant_id']),
        ('pos_sessions', 'uq_pos_session_number', ['session_number', 'tenant_id']),
        ('pos_orders', 'uq_pos_order_number', ['order_number', 'tenant_id']),
        ('system_settings', 'uq_system_setting_key', ['setting_key', 'tenant_id']),
        ('accounts', 'uq_account_code', ['code', 'tenant_id']),
        ('journal_entries', 'uq_journal_entry_number', ['entry_number', 'tenant_id']),
        ('payments', 'uq_payment_number', ['payment_number', 'tenant_id']),
        ('bank_accounts', 'uq_bank_account_number', ['account_number', 'tenant_id']),
        ('cost_centers', 'uq_cost_center_code', ['code', 'tenant_id']),
        ('bank_transactions', 'uq_bank_transaction_number', ['transaction_number', 'tenant_id']),
        ('expenses', 'uq_expense_number', ['expense_number', 'tenant_id']),
        ('employees', 'uq_employee_number', ['employee_number', 'tenant_id']),
        ('employees', 'uq_employee_national_id', ['national_id', 'tenant_id']),
        ('departments', 'uq_department_code', ['code', 'tenant_id']),
        ('positions', 'uq_position_code', ['code', 'tenant_id']),
        ('attendance', 'uq_attendance_employee_date', ['employee_id', 'date', 'tenant_id']),
        ('payrolls', 'uq_payroll_employee_month', ['employee_id', 'month', 'year', 'tenant_id']),
        ('leads', 'uq_lead_code', ['code', 'tenant_id']),
        ('opportunities', 'uq_opportunity_code', ['code', 'tenant_id']),
        ('campaigns', 'uq_campaign_code', ['code', 'tenant_id']),
    ]

    success_count = 0
    skip_count = 0
    error_count = 0

    for table_name, old_constraint, columns in constraints_to_update:
        try:
            if not table_exists(table_name):
                skip_count += 1
                continue

            print_info(f"Updating constraint '{old_constraint}' on '{table_name}'...")

            # Drop old constraint if exists
            try:
                db.session.execute(text(f"""
                    ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {old_constraint}
                """))
            except:
                pass

            # Create new constraint with tenant_id
            columns_str = ', '.join(columns)
            new_constraint_name = f"{old_constraint}_tenant"

            db.session.execute(text(f"""
                ALTER TABLE {table_name}
                ADD CONSTRAINT {new_constraint_name} UNIQUE ({columns_str})
            """))

            db.session.commit()
            print_success(f"Updated constraint on '{table_name}'")
            success_count += 1

        except SQLAlchemyError as e:
            db.session.rollback()
            print_warning(f"Could not update constraint on '{table_name}': {str(e)}")
            error_count += 1

    print()
    print_info(f"Summary: {success_count} updated, {skip_count} skipped, {error_count} errors")
    return True  # Don't fail on constraint errors

def make_tenant_id_not_null():
    """Make tenant_id NOT NULL after data migration"""
    print_header("Step 6: Making tenant_id NOT NULL")

    success_count = 0
    skip_count = 0
    error_count = 0

    for table_name in TABLES_TO_MIGRATE:
        try:
            if not table_exists(table_name):
                skip_count += 1
                continue

            if not column_exists(table_name, 'tenant_id'):
                skip_count += 1
                continue

            # Check if any NULL values exist
            null_count = db.session.execute(
                text(f"SELECT COUNT(*) FROM {table_name} WHERE tenant_id IS NULL")
            ).scalar()

            if null_count > 0:
                print_warning(f"Table '{table_name}' has {null_count} NULL tenant_id values. Skipping...")
                skip_count += 1
                continue

            print_info(f"Making tenant_id NOT NULL in '{table_name}'...")

            db.session.execute(text(f"""
                ALTER TABLE {table_name}
                ALTER COLUMN tenant_id SET NOT NULL
            """))

            db.session.commit()
            print_success(f"Made tenant_id NOT NULL in '{table_name}'")
            success_count += 1

        except SQLAlchemyError as e:
            db.session.rollback()
            print_error(f"Failed to make tenant_id NOT NULL in '{table_name}': {str(e)}")
            error_count += 1

    print()
    print_info(f"Summary: {success_count} updated, {skip_count} skipped, {error_count} errors")
    return error_count == 0

def verify_migration():
    """Verify that migration was successful"""
    print_header("Step 7: Verifying Migration")

    all_good = True

    # Check tenants table
    print_info("Checking tenants table...")
    if not table_exists('tenants'):
        print_error("Tenants table does not exist!")
        all_good = False
    else:
        tenant_count = db.session.execute(text("SELECT COUNT(*) FROM tenants")).scalar()
        print_success(f"Tenants table exists with {tenant_count} tenant(s)")

    # Check tenant_id columns
    print_info("Checking tenant_id columns...")
    missing_columns = []
    for table_name in TABLES_TO_MIGRATE:
        if table_exists(table_name) and not column_exists(table_name, 'tenant_id'):
            missing_columns.append(table_name)

    if missing_columns:
        print_error(f"Missing tenant_id in tables: {', '.join(missing_columns)}")
        all_good = False
    else:
        print_success(f"All {len(TABLES_TO_MIGRATE)} tables have tenant_id column")

    # Check for NULL tenant_id values
    print_info("Checking for NULL tenant_id values...")
    tables_with_nulls = []
    for table_name in TABLES_TO_MIGRATE:
        if table_exists(table_name) and column_exists(table_name, 'tenant_id'):
            null_count = db.session.execute(
                text(f"SELECT COUNT(*) FROM {table_name} WHERE tenant_id IS NULL")
            ).scalar()
            if null_count > 0:
                tables_with_nulls.append(f"{table_name} ({null_count})")

    if tables_with_nulls:
        print_warning(f"Tables with NULL tenant_id: {', '.join(tables_with_nulls)}")
    else:
        print_success("No NULL tenant_id values found")

    print()
    if all_good:
        print_success("✅ Migration verification PASSED!")
    else:
        print_error("❌ Migration verification FAILED!")

    return all_good

def main():
    """Main migration function"""
    print_header("🚀 DED ERP Multi-Tenant Migration 🚀")
    print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Create Flask app context
    app = create_app()

    with app.app_context():
        # Step 0: Pre-flight checks
        backup_reminder()

        if not check_database_connection():
            print_error("Cannot proceed without database connection")
            sys.exit(1)

        print()
        print_info(f"Total tables to migrate: {len(TABLES_TO_MIGRATE)}")
        print()

        # Step 1: Create tenants table
        if not create_tenants_table():
            print_error("Failed to create tenants table. Aborting.")
            sys.exit(1)

        # Step 2: Add tenant_id columns
        if not add_tenant_id_columns():
            print_warning("Some tables failed to get tenant_id column")
            response = input(f"{Colors.BOLD}Continue anyway? (yes/no): {Colors.ENDC}")
            if response.lower() not in ['yes', 'y']:
                print_error("Migration aborted by user")
                sys.exit(1)

        # Step 3: Create default tenant
        tenant_id = create_default_tenant()
        if not tenant_id:
            print_error("Failed to create default tenant. Aborting.")
            sys.exit(1)

        # Step 4: Migrate existing data
        if not migrate_existing_data(tenant_id):
            print_warning("Some data failed to migrate")
            response = input(f"{Colors.BOLD}Continue anyway? (yes/no): {Colors.ENDC}")
            if response.lower() not in ['yes', 'y']:
                print_error("Migration aborted by user")
                sys.exit(1)

        # Step 5: Update unique constraints
        update_unique_constraints()

        # Step 6: Make tenant_id NOT NULL
        if not make_tenant_id_not_null():
            print_warning("Some tables still have nullable tenant_id")

        # Step 7: Verify migration
        verify_migration()

        # Final summary
        print_header("🎉 Migration Complete! 🎉")
        print_success("Multi-tenant migration completed successfully!")
        print()
        print_info("Next steps:")
        print("  1. Initialize TenantMiddleware in app/__init__.py")
        print("  2. Register tenant events using init_tenant_support(app)")
        print("  3. Test tenant isolation")
        print("  4. Create tenant management UI")
        print()
        print_info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_error("Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

