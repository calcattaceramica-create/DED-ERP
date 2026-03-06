from app import db
from app.utils.datetime_helper import utcnow


class License(db.Model):
    __tablename__ = "licenses"

    id = db.Column(db.Integer, primary_key=True)

    # Multi-Tenant Support (consistent with all other models in this project)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=True, index=True)

    # NOTE: table name is 'companies' (not 'company') — fixed from original spec
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), unique=True)

    plan = db.Column(db.String(50), default="trial")
    # trial / monthly / yearly

    status = db.Column(db.String(50), default="active")
    # active / expired / suspended

    start_date = db.Column(db.DateTime, default=utcnow)
    end_date = db.Column(db.DateTime)

    # Stripe Integration
    stripe_customer_id = db.Column(db.String(255), nullable=True, index=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True, index=True)

    # Relationships
    # NOTE: 'company' back-ref is defined on Company.license (uselist=False)
    tenant = db.relationship("Tenant", foreign_keys=[tenant_id], backref="licenses")

    def is_active(self):
        if self.status != "active":
            return False
        if self.end_date and self.end_date < utcnow():
            self.status = "expired"
            db.session.commit()
            return False
        return True

    def __repr__(self):
        return f"<License tenant={self.tenant_id} plan={self.plan} status={self.status}>"


# ─────────────────────────────────────────────────────────────────────────────
# Standalone utility — importable from anywhere in the app
# ─────────────────────────────────────────────────────────────────────────────

def check_license(tenant_id):
    """
    Returns True only when the tenant has a License record that is both
    active (status == 'active') and not yet expired (end_date in the future
    or not set).

    Usage:
        from app.models_license import check_license
        if not check_license(user.tenant_id):
            return redirect(url_for('billing.upgrade'))
    """
    if not tenant_id:
        return False

    lic = License.query.filter_by(tenant_id=tenant_id).first()

    if not lic:
        return False

    # is_active() also auto-marks the license as 'expired' when end_date passes
    return lic.is_active()

