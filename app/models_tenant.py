from datetime import datetime
from app import db

class Tenant(db.Model):
    """
    Multi-Tenant Model - Each tenant represents a separate company/organization
    نموذج متعدد المستأجرين - كل مستأجر يمثل شركة/منظمة منفصلة
    """
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Tenant Identification
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)  # Unique tenant code
    subdomain = db.Column(db.String(63), unique=True, nullable=False, index=True)  # For subdomain-based access
    
    # Company Information
    name = db.Column(db.String(128), nullable=False)
    name_en = db.Column(db.String(128))
    
    # Business Details
    tax_number = db.Column(db.String(64))
    commercial_register = db.Column(db.String(64))
    
    # Contact Information
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(64))
    country = db.Column(db.String(64), default='السعودية')
    
    # Branding
    logo = db.Column(db.String(256))
    primary_color = db.Column(db.String(7), default='#3b82f6')  # Hex color
    
    # Settings
    currency = db.Column(db.String(3), default='SAR')
    tax_rate = db.Column(db.Float, default=15.0)
    language = db.Column(db.String(5), default='ar')
    timezone = db.Column(db.String(50), default='Asia/Riyadh')
    
    # Subscription & Limits
    plan = db.Column(db.String(20), default='basic')  # basic, professional, enterprise
    max_users = db.Column(db.Integer, default=5)
    max_branches = db.Column(db.Integer, default=1)
    max_products = db.Column(db.Integer, default=100)
    max_invoices_per_month = db.Column(db.Integer, default=50)
    
    # Features Enabled
    features_enabled = db.Column(db.JSON, default=dict)  # {'pos': True, 'hr': False, ...}
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_trial = db.Column(db.Boolean, default=True)
    trial_ends_at = db.Column(db.DateTime)
    subscription_ends_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Database Schema (for future schema-based multi-tenancy if needed)
    db_schema = db.Column(db.String(63))  # Optional: for PostgreSQL schema-based isolation
    
    # Admin User (First user created for this tenant)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<Tenant {self.code}: {self.name}>'
    
    def is_feature_enabled(self, feature_name):
        """Check if a specific feature is enabled for this tenant"""
        if not self.features_enabled:
            return False
        return self.features_enabled.get(feature_name, False)
    
    def can_add_user(self):
        """Check if tenant can add more users"""
        from app.models import User
        current_users = User.query.filter_by(tenant_id=self.id, is_active=True).count()
        return current_users < self.max_users
    
    def can_add_branch(self):
        """Check if tenant can add more branches"""
        from app.models import Branch
        current_branches = Branch.query.filter_by(tenant_id=self.id, is_active=True).count()
        return current_branches < self.max_branches
    
    def can_add_product(self):
        """Check if tenant can add more products"""
        from app.models_inventory import Product
        current_products = Product.query.filter_by(tenant_id=self.id, is_active=True).count()
        return current_products < self.max_products
    
    def is_subscription_active(self):
        """Check if subscription is active"""
        if not self.is_active:
            return False
        
        if self.is_trial:
            if self.trial_ends_at and datetime.utcnow() > self.trial_ends_at:
                return False
            return True
        
        if self.subscription_ends_at and datetime.utcnow() > self.subscription_ends_at:
            return False
        
        return True
    
    @staticmethod
    def get_default_features():
        """Get default features for new tenant"""
        return {
            'inventory': True,
            'sales': True,
            'purchases': True,
            'accounting': True,
            'pos': False,
            'hr': False,
            'crm': False,
            'banking': True,
            'reports': True,
        }
    
    @staticmethod
    def generate_subdomain(name):
        """Generate subdomain from company name"""
        import re
        # Remove special characters and spaces
        subdomain = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        # Limit to 63 characters (DNS limit)
        return subdomain[:63]

