from datetime import datetime
from app import db

# Accounting Models
class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)

    # Multi-Tenant Support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)

    code = db.Column(db.String(20), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)
    name_en = db.Column(db.String(128))

    account_type = db.Column(db.String(20), nullable=False)  # asset, liability, equity, revenue, expense
    parent_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))

    # Balance
    debit_balance = db.Column(db.Float, default=0.0)
    credit_balance = db.Column(db.Float, default=0.0)
    current_balance = db.Column(db.Float, default=0.0)

    # Flags
    is_active = db.Column(db.Boolean, default=True)
    is_system = db.Column(db.Boolean, default=False)  # System accounts cannot be deleted

    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint: code + tenant_id
    __table_args__ = (
        db.UniqueConstraint('code', 'tenant_id', name='uq_account_code_tenant'),
    )

    # Self-referential relationship
    children = db.relationship('Account', backref=db.backref('parent', remote_side=[id]))

    def __repr__(self):
        return f'<Account {self.code} - {self.name}>'

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'

    id = db.Column(db.Integer, primary_key=True)

    # Multi-Tenant Support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)

    entry_number = db.Column(db.String(64), nullable=False, index=True)
    entry_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    entry_type = db.Column(db.String(20), default='manual')  # manual, auto, opening, closing
    reference_type = db.Column(db.String(50))  # sales_invoice, purchase_invoice, payment, etc.
    reference_id = db.Column(db.Integer)

    description = db.Column(db.Text)
    total_debit = db.Column(db.Float, default=0.0)
    total_credit = db.Column(db.Float, default=0.0)

    status = db.Column(db.String(20), default='draft')  # draft, posted, cancelled

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    posted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    posted_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: entry_number + tenant_id
    __table_args__ = (
        db.UniqueConstraint('entry_number', 'tenant_id', name='uq_journal_entry_number_tenant'),
    )

    user = db.relationship('User', foreign_keys=[user_id])
    items = db.relationship('JournalEntryItem', backref='journal_entry', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<JournalEntry {self.entry_number}>'

class JournalEntryItem(db.Model):
    __tablename__ = 'journal_entry_items'

    id = db.Column(db.Integer, primary_key=True)

    # Multi-Tenant Support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)

    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)

    description = db.Column(db.String(256))
    debit = db.Column(db.Float, default=0.0)
    credit = db.Column(db.Float, default=0.0)

    account = db.relationship('Account')

    def __repr__(self):
        return f'<JournalEntryItem Account:{self.account_id}>'

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)

    # Multi-Tenant Support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)

    payment_number = db.Column(db.String(64), nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    payment_type = db.Column(db.String(20), nullable=False)  # receipt, payment
    party_type = db.Column(db.String(20))  # customer, supplier
    party_id = db.Column(db.Integer)  # customer_id or supplier_id

    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20))  # cash, bank, check, card

    # Bank/Check details
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))
    check_number = db.Column(db.String(64))
    check_date = db.Column(db.Date)

    reference_number = db.Column(db.String(64))
    notes = db.Column(db.Text)

    status = db.Column(db.String(20), default='draft')  # draft, posted, cancelled

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint: payment_number + tenant_id
    __table_args__ = (
        db.UniqueConstraint('payment_number', 'tenant_id', name='uq_payment_number_tenant'),
    )

    bank_account = db.relationship('BankAccount')
    user = db.relationship('User')

    def __repr__(self):
        return f'<Payment {self.payment_number}>'

class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'

    id = db.Column(db.Integer, primary_key=True)

    # Multi-Tenant Support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)

    account_name = db.Column(db.String(128), nullable=False)
    account_number = db.Column(db.String(64))
    bank_name = db.Column(db.String(128))
    branch = db.Column(db.String(128))
    iban = db.Column(db.String(64))
    swift_code = db.Column(db.String(20))

    account_type = db.Column(db.String(20), default='current')  # current, savings, investment
    currency = db.Column(db.String(3), default='SAR')
    opening_balance = db.Column(db.Float, default=0.0)
    current_balance = db.Column(db.Float, default=0.0)

    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))  # Link to chart of accounts

    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint: account_number + tenant_id
    __table_args__ = (
        db.UniqueConstraint('account_number', 'tenant_id', name='uq_bank_account_number_tenant'),
    )

    account = db.relationship('Account')

    def __repr__(self):
        return f'<BankAccount {self.account_name}>'

class CostCenter(db.Model):
    __tablename__ = 'cost_centers'

    id = db.Column(db.Integer, primary_key=True)

    # Multi-Tenant Support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)

    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    name_en = db.Column(db.String(128))

    parent_id = db.Column(db.Integer, db.ForeignKey('cost_centers.id'))

    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint: code + tenant_id
    __table_args__ = (
        db.UniqueConstraint('code', 'tenant_id', name='uq_cost_center_code_tenant'),
    )

    children = db.relationship('CostCenter', backref=db.backref('parent', remote_side=[id]))

    def __repr__(self):
        return f'<CostCenter {self.name}>'

class BankTransaction(db.Model):
    """Bank account transactions - حركات الحساب البنكي"""
    __tablename__ = 'bank_transactions'

    id = db.Column(db.Integer, primary_key=True)

    # Multi-Tenant Support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)

    transaction_number = db.Column(db.String(64), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)

    transaction_type = db.Column(db.String(20), nullable=False)  # deposit (إيداع), withdrawal (سحب)
    amount = db.Column(db.Float, nullable=False)

    # Reference to source transaction
    reference_type = db.Column(db.String(50))  # sales_invoice, purchase_invoice, expense, payment, manual
    reference_id = db.Column(db.Integer)

    description = db.Column(db.Text)
    notes = db.Column(db.Text)

    # Balance after transaction
    balance_after = db.Column(db.Float, default=0.0)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint: transaction_number + tenant_id
    __table_args__ = (
        db.UniqueConstraint('transaction_number', 'tenant_id', name='uq_bank_transaction_number_tenant'),
    )

    bank_account = db.relationship('BankAccount', backref='transactions')
    user = db.relationship('User')

    def __repr__(self):
        return f'<BankTransaction {self.transaction_number}>'

class Expense(db.Model):
    """Expenses - المصروفات"""
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)

    # Multi-Tenant Support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)

    expense_number = db.Column(db.String(64), nullable=False)
    expense_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    expense_category = db.Column(db.String(50), nullable=False)  # rent, utilities, salaries, maintenance, etc.
    description = db.Column(db.String(256), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    # Payment details
    payment_method = db.Column(db.String(20), default='cash')  # cash, bank
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))

    # Accounting
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))  # Expense account

    notes = db.Column(db.Text)
    attachment = db.Column(db.String(256))  # File path for receipt/invoice

    status = db.Column(db.String(20), default='posted')  # draft, posted, cancelled

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: expense_number + tenant_id
    __table_args__ = (
        db.UniqueConstraint('expense_number', 'tenant_id', name='uq_expense_number_tenant'),
    )

    bank_account = db.relationship('BankAccount')
    account = db.relationship('Account')
    user = db.relationship('User')

    def __repr__(self):
        return f'<Expense {self.expense_number}>'

