"""اختبار صفحة الميزانية العمومية مباشرة"""
import traceback
from app import create_app, db
from app.models import User

app = create_app('development')

with app.app_context():
    try:
        # Test the balance sheet logic directly
        from app.models_accounting import Account

        # Assets
        all_assets = Account.query.filter_by(account_type='asset', is_active=True).order_by(Account.code).all()
        print(f"Total assets accounts: {len(all_assets)}")

        current_assets = [a for a in all_assets if a.code < '15']
        fixed_assets   = [a for a in all_assets if a.code >= '15']

        print(f"Current assets: {len(current_assets)}")
        print(f"Fixed assets: {len(fixed_assets)}")

        total_current_assets = sum(a.debit_balance for a in current_assets)
        total_fixed_assets   = sum(a.debit_balance for a in fixed_assets)
        total_assets         = total_current_assets + total_fixed_assets

        print(f"Total current assets: {total_current_assets}")
        print(f"Total fixed assets: {total_fixed_assets}")
        print(f"Total assets: {total_assets}")

        # Liabilities
        all_liabilities = Account.query.filter_by(account_type='liability', is_active=True).order_by(Account.code).all()
        print(f"\nTotal liability accounts: {len(all_liabilities)}")

        current_liabilities   = [l for l in all_liabilities if l.code < '25']
        long_term_liabilities = [l for l in all_liabilities if l.code >= '25']

        total_current_liabilities   = sum(l.credit_balance for l in current_liabilities)
        total_long_term_liabilities = sum(l.credit_balance for l in long_term_liabilities)
        total_liabilities           = total_current_liabilities + total_long_term_liabilities

        print(f"Current liabilities: {len(current_liabilities)}")
        print(f"Long-term liabilities: {len(long_term_liabilities)}")

        # Equity
        equity_accounts = Account.query.filter_by(account_type='equity', is_active=True).order_by(Account.code).all()
        total_equity = sum(e.credit_balance for e in equity_accounts)
        total_liabilities_equity = total_liabilities + total_equity

        print(f"\nEquity accounts: {len(equity_accounts)}")
        print(f"Total equity: {total_equity}")
        print(f"Total liabilities + equity: {total_liabilities_equity}")

        print("\n✅ Logic completed successfully - no errors!")
        print("Rendering template test...")

        # Try rendering the template
        from flask import render_template
        from datetime import date
        report_date = date.today().strftime('%Y-%m-%d')

        html = render_template('accounting/balance_sheet.html',
            report_date=report_date,
            current_assets=current_assets,
            fixed_assets=fixed_assets,
            total_current_assets=total_current_assets,
            total_fixed_assets=total_fixed_assets,
            total_assets=total_assets,
            current_liabilities=current_liabilities,
            long_term_liabilities=long_term_liabilities,
            total_current_liabilities=total_current_liabilities,
            total_long_term_liabilities=total_long_term_liabilities,
            total_liabilities=total_liabilities,
            equity_accounts=equity_accounts,
            total_equity=total_equity,
            total_liabilities_equity=total_liabilities_equity
        )
        print(f"✅ Template rendered successfully! ({len(html)} bytes)")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        traceback.print_exc()

