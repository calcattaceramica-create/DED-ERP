from datetime import datetime
from app import db


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

    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)

    # Relationships
    # NOTE: 'company' back-ref is defined on Company.license (uselist=False)
    tenant = db.relationship("Tenant", foreign_keys=[tenant_id], backref="licenses")

    def is_active(self):
        if self.status != "active":
            return False
        if self.end_date and self.end_date < datetime.utcnow():
            self.status = "expired"
            db.session.commit()
            return False
        return True

    def __repr__(self):
        return f"<License tenant={self.tenant_id} plan={self.plan} status={self.status}>"

