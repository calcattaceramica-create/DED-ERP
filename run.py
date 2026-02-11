import os
import sys

# Use production config on Render, development otherwise
config_name = os.getenv('FLASK_ENV', 'development')
if config_name == 'production':
    config_name = 'production'

print(f"Starting application with config: {config_name}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Import app after printing initial info
from app import create_app, db
from app.models import *

app = create_app(config_name)

print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Initialize database on startup (for Render deployment)
def init_database():
    """Initialize database with error handling"""
    with app.app_context():
        try:
            # Ensure database directory exists
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                print(f"Created database directory: {db_dir}")

            db.create_all()
            print("✅ Database tables created successfully!")

            # Initialize default data if database is empty
            from app.models import Company, Branch, Role, User, Unit, Warehouse, Account

            if not Company.query.first():
                # Create default company
                company = Company(
                    name='شركة نموذجية',
                    name_en='Sample Company',
                    tax_number='123456789',
                    city='الرياض',
                    country='السعودية',
                    currency='SAR',
                    tax_rate=15.0
                )
                db.session.add(company)

                # Create default branch
                branch = Branch(
                    name='الفرع الرئيسي',
                    name_en='Main Branch',
                    code='BR001',
                    company_id=1,
                    city='الرياض',
                    is_active=True
                )
                db.session.add(branch)

                # Create default roles
                admin_role = Role(name='admin', name_ar='مدير النظام', description='Full system access')
                manager_role = Role(name='manager', name_ar='مدير', description='Manager access')
                user_role = Role(name='user', name_ar='مستخدم', description='Basic user access')
                db.session.add_all([admin_role, manager_role, user_role])

                # Create default admin user
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    full_name='مدير النظام',
                    is_active=True,
                    is_admin=True,
                    language='ar',
                    branch_id=1,
                    role_id=1
                )
                admin.set_password('admin123')
                db.session.add(admin)

                # Create default units
                units = [
                    Unit(name='قطعة', name_en='Piece', symbol='قطعة'),
                    Unit(name='كيلوجرام', name_en='Kilogram', symbol='كجم'),
                    Unit(name='متر', name_en='Meter', symbol='م'),
                    Unit(name='لتر', name_en='Liter', symbol='لتر'),
                    Unit(name='صندوق', name_en='Box', symbol='صندوق'),
                ]
                db.session.add_all(units)

                # Create default warehouse
                warehouse = Warehouse(
                    name='المستودع الرئيسي',
                    name_en='Main Warehouse',
                    code='WH001',
                    branch_id=1,
                    is_active=True
                )
                db.session.add(warehouse)

                # Create default chart of accounts
                accounts = [
                    Account(code='1000', name='الأصول', name_en='Assets', account_type='asset', is_system=True),
                    Account(code='2000', name='الخصوم', name_en='Liabilities', account_type='liability', is_system=True),
                    Account(code='3000', name='حقوق الملكية', name_en='Equity', account_type='equity', is_system=True),
                    Account(code='4000', name='الإيرادات', name_en='Revenue', account_type='revenue', is_system=True),
                    Account(code='5000', name='المصروفات', name_en='Expenses', account_type='expense', is_system=True),
                ]
                db.session.add_all(accounts)

                db.session.commit()
                print('✅ Default data initialized successfully!')
            else:
                print('ℹ️ Database already contains data, skipping initialization')
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            import traceback
            traceback.print_exc()
            # Don't exit - let the app start anyway

# Initialize database on startup
init_database()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Role': Role,
        'Permission': Permission,
        'Company': Company,
        'Branch': Branch,
        'Category': Category,
        'Unit': Unit,
        'Product': Product,
        'Warehouse': Warehouse,
        'Stock': Stock,
        'Customer': Customer,
        'Supplier': Supplier,
        'SalesInvoice': SalesInvoice,
        'PurchaseInvoice': PurchaseInvoice,
        'Account': Account,
        'JournalEntry': JournalEntry,
        'Employee': Employee,
        'Department': Department,
    }

@app.cli.command()
def init_db():
    """Initialize the database with default data"""
    db.create_all()
    
    # Create default company
    if not Company.query.first():
        company = Company(
            name='شركة نموذجية',
            name_en='Sample Company',
            tax_number='123456789',
            city='الرياض',
            country='السعودية',
            currency='SAR',
            tax_rate=15.0
        )
        db.session.add(company)
    
    # Create default branch
    if not Branch.query.first():
        branch = Branch(
            name='الفرع الرئيسي',
            name_en='Main Branch',
            code='BR001',
            company_id=1,
            city='الرياض',
            is_active=True
        )
        db.session.add(branch)
    
    # Create default roles
    if not Role.query.first():
        admin_role = Role(name='admin', name_ar='مدير النظام', description='Full system access')
        manager_role = Role(name='manager', name_ar='مدير', description='Manager access')
        user_role = Role(name='user', name_ar='مستخدم', description='Basic user access')
        db.session.add_all([admin_role, manager_role, user_role])
    
    # Create default admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            full_name='مدير النظام',
            is_active=True,
            is_admin=True,
            language='ar',
            branch_id=1,
            role_id=1
        )
        admin.set_password('admin123')
        db.session.add(admin)
    
    # Create default units
    if not Unit.query.first():
        units = [
            Unit(name='قطعة', name_en='Piece', symbol='قطعة'),
            Unit(name='كيلوجرام', name_en='Kilogram', symbol='كجم'),
            Unit(name='متر', name_en='Meter', symbol='م'),
            Unit(name='لتر', name_en='Liter', symbol='لتر'),
            Unit(name='صندوق', name_en='Box', symbol='صندوق'),
        ]
        db.session.add_all(units)
    
    # Create default warehouse
    if not Warehouse.query.first():
        warehouse = Warehouse(
            name='المستودع الرئيسي',
            name_en='Main Warehouse',
            code='WH001',
            branch_id=1,
            is_active=True
        )
        db.session.add(warehouse)
    
    # Create default chart of accounts
    if not Account.query.first():
        accounts = [
            Account(code='1000', name='الأصول', name_en='Assets', account_type='asset', is_system=True),
            Account(code='2000', name='الخصوم', name_en='Liabilities', account_type='liability', is_system=True),
            Account(code='3000', name='حقوق الملكية', name_en='Equity', account_type='equity', is_system=True),
            Account(code='4000', name='الإيرادات', name_en='Revenue', account_type='revenue', is_system=True),
            Account(code='5000', name='المصروفات', name_en='Expenses', account_type='expense', is_system=True),
        ]
        db.session.add_all(accounts)
    
    db.session.commit()
    print('Database initialized successfully!')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

