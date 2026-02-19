"""
Add Missing Columns to Database
================================

This script adds any missing columns that were added to models but not in the database.

Author: Augment Agent
Date: 2026-02-17
"""

import sys
import os
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

# ANSI color codes
class Colors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    WARNING = '\033[93m'
    OKCYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

def add_is_super_admin_column():
    """Add is_super_admin column to users table"""
    print_info("Adding is_super_admin column to users table...")

    try:
        # Check if column exists
        result = db.session.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='users' AND column_name='is_super_admin'
        """))

        if result.fetchone():
            print_info("Column is_super_admin already exists. Skipping...")
            return True

        # Add the column
        db.session.execute(text("""
            ALTER TABLE users
            ADD COLUMN is_super_admin BOOLEAN DEFAULT FALSE
        """))

        db.session.commit()
        print_success("Added is_super_admin column to users table")
        return True

    except SQLAlchemyError as e:
        db.session.rollback()
        print_error(f"Failed to add is_super_admin column: {str(e)}")
        return False

def add_tenant_id_to_table(table_name):
    """Add tenant_id column to a specific table"""
    print_info(f"Checking tenant_id column in {table_name} table...")

    try:
        # Check if column exists
        result = db.session.execute(text(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='{table_name}' AND column_name='tenant_id'
        """))

        if result.fetchone():
            print_info(f"Column tenant_id already exists in {table_name}. Skipping...")
            return True

        # Add the column
        print_info(f"Adding tenant_id to {table_name}...")
        db.session.execute(text(f"""
            ALTER TABLE {table_name}
            ADD COLUMN tenant_id INTEGER REFERENCES tenants(id)
        """))

        # Create index
        db.session.execute(text(f"""
            CREATE INDEX idx_{table_name}_tenant_id ON {table_name}(tenant_id)
        """))

        # Get default tenant ID
        result = db.session.execute(text("SELECT id FROM tenants ORDER BY id LIMIT 1"))
        tenant = result.fetchone()

        if tenant:
            tenant_id = tenant[0]
            # Update existing records
            db.session.execute(text(f"""
                UPDATE {table_name}
                SET tenant_id = {tenant_id}
                WHERE tenant_id IS NULL
            """))
            print_info(f"Updated existing records in {table_name} with tenant_id={tenant_id}")

        db.session.commit()
        print_success(f"Added tenant_id column to {table_name} table")
        return True

    except SQLAlchemyError as e:
        db.session.rollback()
        print_error(f"Failed to add tenant_id to {table_name}: {str(e)}")
        return False

def main():
    """Main function"""
    print()
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'Adding Missing Columns':^70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print()

    app = create_app()

    with app.app_context():
        success = True

        # Add is_super_admin column
        if not add_is_super_admin_column():
            success = False

        # Add tenant_id to stocks table
        if not add_tenant_id_to_table('stocks'):
            success = False

        # Add tenant_id to stock_movements table
        if not add_tenant_id_to_table('stock_movements'):
            success = False

        if not success:
            print()
            print_error("Some columns failed to add")
            sys.exit(1)

        print()
        print_success("All missing columns added successfully!")
        print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print()
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

