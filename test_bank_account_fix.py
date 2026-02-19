"""
Test script to verify BankAccount model fix
اختبار للتحقق من إصلاح نموذج BankAccount
"""

from app import create_app, db
from app.models import BankAccount

def test_bank_account_creation():
    """Test creating a bank account with all fields"""
    app = create_app()
    
    with app.app_context():
        # Test data
        test_data = {
            'account_name': 'حساب اختبار - Test Account',
            'account_number': '1234567890',
            'bank_name': 'بنك الراجحي',
            'branch': 'فرع الرياض الرئيسي',
            'iban': 'SA0000000000000000000000',
            'swift_code': 'RIBLSARI',
            'account_type': 'current',
            'currency': 'SAR',
            'opening_balance': 10000.00,
            'current_balance': 10000.00,
            'is_active': True,
            'notes': 'هذا حساب اختبار'
        }
        
        try:
            # Create bank account
            bank_account = BankAccount(**test_data)
            
            # Verify all fields are set correctly
            assert bank_account.account_name == test_data['account_name']
            assert bank_account.account_number == test_data['account_number']
            assert bank_account.bank_name == test_data['bank_name']
            assert bank_account.branch == test_data['branch']
            assert bank_account.iban == test_data['iban']
            assert bank_account.swift_code == test_data['swift_code']
            assert bank_account.account_type == test_data['account_type']
            assert bank_account.currency == test_data['currency']
            assert bank_account.opening_balance == test_data['opening_balance']
            assert bank_account.current_balance == test_data['current_balance']
            assert bank_account.is_active == test_data['is_active']
            assert bank_account.notes == test_data['notes']
            
            print("✅ جميع الحقول تم تعيينها بشكل صحيح - All fields set correctly")
            print("✅ اختبار إنشاء الحساب البنكي نجح - Bank account creation test passed")
            
            # Try to add to database (rollback to avoid actual save)
            db.session.add(bank_account)
            db.session.flush()
            
            print("✅ يمكن إضافة الحساب إلى قاعدة البيانات - Can add to database")
            
            # Rollback to avoid saving test data
            db.session.rollback()
            
            return True
            
        except Exception as e:
            print(f"❌ فشل الاختبار - Test failed: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("اختبار إصلاح نموذج BankAccount")
    print("Testing BankAccount Model Fix")
    print("=" * 60)
    
    success = test_bank_account_creation()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ جميع الاختبارات نجحت - All tests passed!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ فشلت بعض الاختبارات - Some tests failed!")
        print("=" * 60)

