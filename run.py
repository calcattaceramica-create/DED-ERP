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
from app.models import (
    User, Role, Permission, Company, Branch, Category, Unit, Product,
    Warehouse, Stock, Customer, Supplier, SalesInvoice, PurchaseInvoice,
    Account, JournalEntry, Employee, Department
)

app = create_app(config_name)

print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Initialize database on startup (for Render deployment)
def init_database():
    """Initialize database with error handling"""
    with app.app_context():
        try:
            # Ensure database directory exists (only for SQLite)
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir)
                    print(f"Created database directory: {db_dir}")

            db.create_all()
            print("✅ Database tables created successfully!")

            # Initialize default data if database is empty
            from app.models import Company, Branch, Role, User, Unit, Warehouse, Account, Permission

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

                # Create default permissions
                permissions = [
                    # Dashboard
                    Permission(name='dashboard.view', name_ar='عرض لوحة التحكم', module='main'),

                    # Inventory
                    Permission(name='inventory.view', name_ar='عرض المخزون', module='inventory'),
                    Permission(name='inventory.stock.view', name_ar='عرض المخزون', module='inventory'),
                    Permission(name='inventory.stock.add', name_ar='إضافة مخزون', module='inventory'),
                    Permission(name='inventory.stock.edit', name_ar='تعديل مخزون', module='inventory'),
                    Permission(name='inventory.stock.delete', name_ar='حذف مخزون', module='inventory'),
                    Permission(name='inventory.products.view', name_ar='عرض المنتجات', module='inventory'),
                    Permission(name='inventory.products.create', name_ar='إضافة منتج', module='inventory'),
                    Permission(name='inventory.products.edit', name_ar='تعديل منتج', module='inventory'),
                    Permission(name='inventory.products.delete', name_ar='حذف منتج', module='inventory'),
                    Permission(name='inventory.damaged.view', name_ar='عرض المخزون التالف', module='inventory'),
                    Permission(name='inventory.damaged.add', name_ar='إضافة مخزون تالف', module='inventory'),
                    Permission(name='inventory.damaged.edit', name_ar='تعديل مخزون تالف', module='inventory'),
                    Permission(name='inventory.damaged.delete', name_ar='حذف مخزون تالف', module='inventory'),

                    # Sales
                    Permission(name='sales.view', name_ar='عرض المبيعات', module='sales'),
                    Permission(name='sales.invoices.view', name_ar='عرض فواتير المبيعات', module='sales'),
                    Permission(name='sales.invoices.add', name_ar='إضافة فاتورة مبيعات', module='sales'),
                    Permission(name='sales.invoices.edit', name_ar='تعديل فاتورة مبيعات', module='sales'),
                    Permission(name='sales.invoices.delete', name_ar='حذف فاتورة مبيعات', module='sales'),
                    Permission(name='sales.customers.view', name_ar='عرض العملاء', module='sales'),
                    Permission(name='sales.customers.add', name_ar='إضافة عميل', module='sales'),
                    Permission(name='sales.customers.edit', name_ar='تعديل عميل', module='sales'),
                    Permission(name='sales.customers.delete', name_ar='حذف عميل', module='sales'),

                    # Purchases
                    Permission(name='purchases.view', name_ar='عرض المشتريات', module='purchases'),
                    Permission(name='purchases.invoices.view', name_ar='عرض فواتير المشتريات', module='purchases'),
                    Permission(name='purchases.invoices.add', name_ar='إضافة فاتورة مشتريات', module='purchases'),
                    Permission(name='purchases.invoices.edit', name_ar='تعديل فاتورة مشتريات', module='purchases'),
                    Permission(name='purchases.invoices.delete', name_ar='حذف فاتورة مشتريات', module='purchases'),
                    Permission(name='purchases.suppliers.view', name_ar='عرض الموردين', module='purchases'),
                    Permission(name='purchases.suppliers.add', name_ar='إضافة مورد', module='purchases'),
                    Permission(name='purchases.suppliers.edit', name_ar='تعديل مورد', module='purchases'),
                    Permission(name='purchases.suppliers.delete', name_ar='حذف مورد', module='purchases'),

                    # Accounting
                    Permission(name='accounting.view', name_ar='عرض المحاسبة', module='accounting'),
                    Permission(name='accounting.accounts.view', name_ar='عرض الحسابات', module='accounting'),
                    Permission(name='accounting.accounts.add', name_ar='إضافة حساب', module='accounting'),
                    Permission(name='accounting.accounts.edit', name_ar='تعديل حساب', module='accounting'),
                    Permission(name='accounting.accounts.delete', name_ar='حذف حساب', module='accounting'),
                    Permission(name='accounting.entries.view', name_ar='عرض القيود', module='accounting'),
                    Permission(name='accounting.entries.add', name_ar='إضافة قيد', module='accounting'),
                    Permission(name='accounting.entries.edit', name_ar='تعديل قيد', module='accounting'),
                    Permission(name='accounting.entries.delete', name_ar='حذف قيد', module='accounting'),

                    # Reports
                    Permission(name='reports.view', name_ar='عرض التقارير', module='reports'),
                    Permission(name='reports.sales', name_ar='تقارير المبيعات', module='reports'),
                    Permission(name='reports.purchases', name_ar='تقارير المشتريات', module='reports'),
                    Permission(name='reports.inventory', name_ar='تقارير المخزون', module='reports'),
                    Permission(name='reports.accounting', name_ar='تقارير المحاسبة', module='reports'),

                    # Settings
                    Permission(name='settings.view', name_ar='عرض الإعدادات', module='settings'),
                    Permission(name='settings.company.view', name_ar='عرض بيانات الشركة', module='settings'),
                    Permission(name='settings.company.edit', name_ar='تعديل بيانات الشركة', module='settings'),
                    Permission(name='settings.branches.view', name_ar='عرض الفروع', module='settings'),
                    Permission(name='settings.branches.manage', name_ar='إدارة الفروع', module='settings'),
                    Permission(name='settings.users.view', name_ar='عرض المستخدمين', module='settings'),
                    Permission(name='settings.users.manage', name_ar='إدارة المستخدمين', module='settings'),
                    Permission(name='settings.roles.view', name_ar='عرض الأدوار', module='settings'),
                    Permission(name='settings.roles.manage', name_ar='إدارة الأدوار', module='settings'),
                    Permission(name='settings.permissions.view', name_ar='عرض الصلاحيات', module='settings'),
                    Permission(name='settings.permissions.manage', name_ar='إدارة الصلاحيات', module='settings'),
                ]
                db.session.add_all(permissions)
                db.session.flush()  # Flush to get permission IDs

                # Create default roles
                admin_role = Role(name='admin', name_ar='مدير النظام', description='Full system access')
                admin_role.permissions = permissions  # Admin gets all permissions

                manager_role = Role(name='manager', name_ar='مدير', description='Manager access')
                # Manager gets most permissions except settings
                manager_permissions = [p for p in permissions if not p.module == 'settings' or p.name == 'settings.view']
                manager_role.permissions = manager_permissions

                user_role = Role(name='user', name_ar='مستخدم', description='Basic user access')
                # User gets only view permissions
                user_permissions = [p for p in permissions if '.view' in p.name]
                user_role.permissions = user_permissions

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
    # Check if SSL certificates exist
    import os
    ssl_dir = os.path.join(os.path.dirname(__file__), 'ssl')
    cert_file = os.path.join(ssl_dir, 'cert.pem')
    key_file = os.path.join(ssl_dir, 'key.pem')

    # Use HTTPS if certificates exist, otherwise HTTP
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("\n" + "=" * 100)
        print("🔒 Starting server with HTTPS (SSL enabled)")
        print("🔒 بدء الخادم مع HTTPS (SSL مفعل)")
        print("=" * 100)
        print(f"📁 Certificate: {cert_file}")
        print(f"🔑 Private Key: {key_file}")
        print(f"🌐 URL: https://127.0.0.1:5000")
        print(f"🌐 URL: https://localhost:5000")
        print("\n⚠️  Note: Browser will show security warning for self-signed certificate")
        print("⚠️  ملاحظة: المتصفح سيظهر تحذير أمان للشهادة ذاتية التوقيع")
        print("   Click 'Advanced' → 'Proceed to localhost' to continue")
        print("   اضغط 'متقدم' ← 'المتابعة إلى localhost' للاستمرار")
        print("=" * 100 + "\n")

        # Create SSL context
        ssl_context = (cert_file, key_file)
        app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=ssl_context)
    else:
        print("\n" + "=" * 100)
        print("⚠️  SSL certificates not found - Starting with HTTP")
        print("⚠️  شهادات SSL غير موجودة - بدء الخادم مع HTTP")
        print("=" * 100)
        print(f"💡 To enable HTTPS, run: python generate_ssl_cert.py")
        print(f"💡 لتفعيل HTTPS، شغّل: python generate_ssl_cert.py")
        print(f"🌐 URL: http://127.0.0.1:5000")
        print("=" * 100 + "\n")

        app.run(debug=True, host='0.0.0.0', port=5000)

