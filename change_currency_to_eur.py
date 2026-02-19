#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Change currency from SAR to EUR
"""

from app import create_app, db
from app.models import Company

app = create_app()

with app.app_context():
    print('='*80)
    print('Changing currency to EUR (Euro)...')
    print('='*80)
    print()
    
    # Get company
    company = Company.query.first()
    
    if not company:
        print('❌ No company found in database!')
        print('Creating default company...')
        company = Company(
            name='شركة تجارية',
            name_en='Trading Company',
            currency='EUR',
            tax_rate=15.0
        )
        db.session.add(company)
        db.session.commit()
        print('✅ Company created with EUR currency')
    else:
        print(f'Current company: {company.name}')
        print(f'Current currency: {company.currency}')
        print()
        
        # Change to EUR
        company.currency = 'EUR'
        db.session.commit()
        
        print('✅ Currency changed to EUR (Euro)')
    
    print()
    print('='*80)
    print('Verification:')
    print('='*80)
    
    # Verify
    company = Company.query.first()
    print(f'Company: {company.name}')
    print(f'Currency: {company.currency}')
    print(f'Currency Symbol: €')
    print(f'Currency Name: يورو')
    
    print()
    print('='*80)
    print('Done! Please refresh the browser to see the changes.')
    print('='*80)

