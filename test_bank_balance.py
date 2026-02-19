"""
Test bank balance after invoice operations
اختبار رصيد البنك بعد عمليات الفواتير
"""
import sqlite3

# Connect to database
conn = sqlite3.connect('erp_system.db')
cursor = conn.cursor()

print("=" * 80)
print("🏦 فحص رصيد الحسابات البنكية")
print("🏦 Checking Bank Account Balances")
print("=" * 80)

# Get all bank accounts
cursor.execute("""
    SELECT id, account_name, account_number, current_balance
    FROM bank_accounts
""")

banks = cursor.fetchall()

if banks:
    for bank in banks:
        print(f"\n{'='*60}")
        print(f"🏦 Bank ID: {bank[0]}")
        print(f"   Name: {bank[1]}")
        print(f"   Account Number: {bank[2]}")
        print(f"   Current Balance: {bank[3]}€")
        print(f"{'='*60}")
        
        # Get recent transactions
        cursor.execute("""
            SELECT transaction_number, transaction_date, transaction_type, 
                   amount, description, balance_after
            FROM bank_transactions
            WHERE bank_account_id = ?
            ORDER BY transaction_date DESC, id DESC
            LIMIT 10
        """, (bank[0],))
        
        transactions = cursor.fetchall()
        
        if transactions:
            print(f"\n   📋 آخر 10 معاملات:")
            print(f"   {'='*56}")
            for trans in transactions:
                trans_type = "إيداع" if trans[2] == 'deposit' else "سحب"
                print(f"   {trans[0]} | {trans[1]} | {trans_type}")
                print(f"   المبلغ: {trans[3]}€ | الوصف: {trans[4]}")
                print(f"   الرصيد بعد: {trans[5]}€")
                print(f"   {'-'*56}")
        else:
            print(f"\n   ℹ️  لا توجد معاملات")

# Get sales invoices with bank accounts
print("\n" + "=" * 80)
print("📄 فواتير المبيعات المرتبطة بحسابات بنكية:")
print("=" * 80)

cursor.execute("""
    SELECT si.id, si.invoice_number, si.status, si.payment_status, 
           si.total_amount, si.bank_account_id, ba.account_name
    FROM sales_invoices si
    LEFT JOIN bank_accounts ba ON si.bank_account_id = ba.id
    WHERE si.bank_account_id IS NOT NULL
    ORDER BY si.id DESC
    LIMIT 5
""")

invoices = cursor.fetchall()

if invoices:
    for inv in invoices:
        print(f"\n   Invoice #{inv[1]}")
        print(f"   Status: {inv[2]} | Payment: {inv[3]}")
        print(f"   Amount: {inv[4]}€ | Bank: {inv[6]}")
        
        # Check if bank transaction exists
        cursor.execute("""
            SELECT COUNT(*) FROM bank_transactions
            WHERE reference_type = 'sales_invoice' AND reference_id = ?
        """, (inv[0],))
        
        trans_count = cursor.fetchone()[0]
        if trans_count > 0:
            print(f"   ✅ Bank transaction exists ({trans_count})")
        else:
            print(f"   ❌ No bank transaction found!")
else:
    print("\n   ℹ️  لا توجد فواتير مبيعات مرتبطة بحسابات بنكية")

conn.close()

print("\n" + "=" * 80)
print("✅ تم الانتهاء!")
print("=" * 80)

