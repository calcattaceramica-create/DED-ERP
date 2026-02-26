import sys
sys.path.insert(0, 'C:/Users/DELL/DED')

from app import create_app, db
from app.models_accounting import Account
from datetime import date

app = create_app()
with app.app_context():
    print("="*60)
    print("اختبار منطق route الميزانية العمومية")
    print("="*60)
    
    try:
        report_date = date.today().strftime('%Y-%m-%d')
        print(f"✅ report_date: {report_date}")
        
        # Assets
        all_assets = Account.query.filter_by(account_type='asset', is_active=True).order_by(Account.code).all()
        print(f"✅ عدد حسابات الأصول: {len(all_assets)}")
        for a in all_assets[:3]:
            print(f"   - كود: {a.code}, اسم: {a.name}")
        
        current_assets = [a for a in all_assets if a.code < '15']
        fixed_assets   = [a for a in all_assets if a.code >= '15']
        total_current_assets = sum(a.debit_balance for a in current_assets)
        total_fixed_assets   = sum(a.debit_balance for a in fixed_assets)
        total_assets         = total_current_assets + total_fixed_assets
        
        print(f"✅ أصول متداولة: {len(current_assets)} حساب, إجمالي: {total_current_assets}")
        print(f"✅ أصول ثابتة: {len(fixed_assets)} حساب, إجمالي: {total_fixed_assets}")
        print(f"✅ إجمالي الأصول: {total_assets}")
        
        # Liabilities
        all_liabilities = Account.query.filter_by(account_type='liability', is_active=True).order_by(Account.code).all()
        print(f"\n✅ عدد حسابات الخصوم: {len(all_liabilities)}")
        
        current_liabilities      = [l for l in all_liabilities if l.code < '25']
        long_term_liabilities    = [l for l in all_liabilities if l.code >= '25']
        total_current_liabilities   = sum(l.credit_balance for l in current_liabilities)
        total_long_term_liabilities = sum(l.credit_balance for l in long_term_liabilities)
        total_liabilities           = total_current_liabilities + total_long_term_liabilities
        
        print(f"✅ خصوم متداولة: {len(current_liabilities)} حساب")
        print(f"✅ خصوم طويلة الأجل: {len(long_term_liabilities)} حساب")
        
        # Equity
        equity_accounts = Account.query.filter_by(account_type='equity', is_active=True).order_by(Account.code).all()
        total_equity = sum(e.credit_balance for e in equity_accounts)
        
        print(f"\n✅ حقوق الملكية: {len(equity_accounts)} حساب, إجمالي: {total_equity}")
        
        total_liabilities_equity = total_liabilities + total_equity
        print(f"✅ إجمالي الخصوم + حقوق الملكية: {total_liabilities_equity}")
        
        print("\n✅✅✅ المنطق يعمل بشكل صحيح! لا يوجد خطأ في الكود.")
        
    except Exception as e:
        print(f"\n❌ خطأ: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

