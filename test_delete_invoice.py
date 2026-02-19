"""
Test delete invoice bank reversal
اختبار عكس المعاملة البنكية عند حذف الفاتورة
"""
import sqlite3

# Connect to database
conn = sqlite3.connect('erp_system.db')
cursor = conn.cursor()

print("=" * 80)
print("🔍 فحص المعاملات البنكية لفواتير المبيعات")
print("🔍 Checking bank transactions for sales invoices")
print("=" * 80)

# Get all sales invoices with bank accounts
cursor.execute("""
    SELECT id, invoice_number, status, payment_status, total_amount, bank_account_id
    FROM sales_invoices
    WHERE bank_account_id IS NOT NULL
    ORDER BY id DESC
    LIMIT 5
""")

invoices = cursor.fetchall()

if invoices:
    print(f"\n📋 فواتير المبيعات المرتبطة بحسابات بنكية:")
    for inv in invoices:
        print(f"\n   Invoice ID: {inv[0]}")
        print(f"   Invoice Number: {inv[1]}")
        print(f"   Status: {inv[2]}")
        print(f"   Payment Status: {inv[3]}")
        print(f"   Total Amount: {inv[4]}")
        print(f"   Bank Account ID: {inv[5]}")
        
        # Check bank transactions
        cursor.execute("""
            SELECT id, transaction_number, transaction_type, amount, description
            FROM bank_transactions
            WHERE reference_type = 'sales_invoice' AND reference_id = ?
        """, (inv[0],))
        
        trans = cursor.fetchall()
        if trans:
            print(f"   ✅ Bank Transactions:")
            for t in trans:
                print(f"      - {t[1]}: {t[2]} {t[3]} - {t[4]}")
        else:
            print(f"   ❌ No bank transactions found!")
else:
    print("\n❌ لا توجد فواتير مبيعات مرتبطة بحسابات بنكية")

# Check bank accounts
print("\n" + "=" * 80)
print("🏦 الحسابات البنكية:")
cursor.execute("""
    SELECT id, account_name, account_number, current_balance
    FROM bank_accounts
""")

banks = cursor.fetchall()
for bank in banks:
    print(f"\n   Bank ID: {bank[0]}")
    print(f"   Name: {bank[1]}")
    print(f"   Account Number: {bank[2]}")
    print(f"   Current Balance: {bank[3]}")

conn.close()

print("\n" + "=" * 80)
print("✅ تم الانتهاء!")
print("=" * 80)

