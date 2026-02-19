from app import db
from datetime import datetime

class Currency(db.Model):
    """Currency model"""
    __tablename__ = 'currencies'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3), unique=True, nullable=False)  # SAR, USD, EUR, etc.
    name = db.Column(db.String(100), nullable=False)  # Saudi Riyal, US Dollar, etc.
    name_ar = db.Column(db.String(100))  # ريال سعودي، دولار أمريكي، إلخ
    symbol = db.Column(db.String(10), nullable=False)  # ر.س, $, €, etc.
    exchange_rate = db.Column(db.Float, default=1.0)  # Exchange rate to base currency
    is_base = db.Column(db.Boolean, default=False)  # Is this the base currency?
    is_active = db.Column(db.Boolean, default=True)
    decimal_places = db.Column(db.Integer, default=2)  # Number of decimal places
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exchange_rates = db.relationship('ExchangeRate', backref='currency', lazy='dynamic', 
                                    foreign_keys='ExchangeRate.from_currency_id')
    
    def __repr__(self):
        return f'<Currency {self.code}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'name_ar': self.name_ar,
            'symbol': self.symbol,
            'exchange_rate': self.exchange_rate,
            'is_base': self.is_base,
            'is_active': self.is_active,
            'decimal_places': self.decimal_places
        }

class ExchangeRate(db.Model):
    """Exchange rate history model"""
    __tablename__ = 'exchange_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    from_currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'), nullable=False)
    to_currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'), nullable=False)
    rate = db.Column(db.Float, nullable=False)
    effective_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    source = db.Column(db.String(50))  # manual, api, bank, etc.
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    from_currency = db.relationship('Currency', foreign_keys=[from_currency_id])
    to_currency = db.relationship('Currency', foreign_keys=[to_currency_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<ExchangeRate {self.from_currency.code}/{self.to_currency.code}: {self.rate}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'from_currency': self.from_currency.code if self.from_currency else None,
            'to_currency': self.to_currency.code if self.to_currency else None,
            'rate': self.rate,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'source': self.source,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

