"""
Bank account helper functions
دوال مساعدة للحسابات البنكية
"""
from app import db
from app.models_accounting import BankAccount, BankTransaction, Account
from datetime import datetime
from flask_login import current_user

def create_bank_transaction(bank_account_id, transaction_type, amount, reference_type, reference_id, description):
    """
    Create a bank transaction and update bank balance
    
    Args:
        bank_account_id: ID of the bank account
        transaction_type: 'deposit' or 'withdrawal'
        amount: Transaction amount
        reference_type: Type of source transaction (sales_invoice, purchase_invoice, etc.)
        reference_id: ID of source transaction
        description: Transaction description
    
    Returns:
        BankTransaction object or None if failed
    """
    try:
        bank_account = BankAccount.query.get(bank_account_id)
        if not bank_account:
            print(f"Bank account {bank_account_id} not found")
            return None
        
        # Update bank account balance
        if transaction_type == 'deposit':
            bank_account.current_balance += amount
        elif transaction_type == 'withdrawal':
            bank_account.current_balance -= amount
        else:
            print(f"Invalid transaction type: {transaction_type}")
            return None

        # Update linked accounting account balance if exists
        if bank_account.account_id:
            accounting_account = Account.query.get(bank_account.account_id)
            if accounting_account:
                if transaction_type == 'deposit':
                    # Bank accounts are assets, so debit increases balance
                    accounting_account.debit_balance += amount
                    accounting_account.current_balance = accounting_account.debit_balance - accounting_account.credit_balance
                elif transaction_type == 'withdrawal':
                    # Withdrawal decreases debit balance (or increases credit)
                    accounting_account.debit_balance -= amount
                    accounting_account.current_balance = accounting_account.debit_balance - accounting_account.credit_balance

                print(f"Updated accounting account {accounting_account.code}: Debit={accounting_account.debit_balance}, Credit={accounting_account.credit_balance}, Balance={accounting_account.current_balance}")
        
        # Generate transaction number
        today = datetime.utcnow()
        prefix = f'BT{today.year}{today.month:02d}{today.day:02d}'
        
        last_trans = BankTransaction.query.filter(
            BankTransaction.transaction_number.like(f'{prefix}%')
        ).order_by(BankTransaction.id.desc()).first()
        
        if last_trans:
            last_num = int(last_trans.transaction_number[-4:])
            trans_number = f'{prefix}{(last_num + 1):04d}'
        else:
            trans_number = f'{prefix}0001'
        
        # Create transaction record
        transaction = BankTransaction(
            transaction_number=trans_number,
            transaction_date=today.date(),
            bank_account_id=bank_account_id,
            transaction_type=transaction_type,
            amount=amount,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
            balance_after=bank_account.current_balance,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        
        db.session.add(transaction)
        
        print(f"Bank transaction created: {trans_number}, Type: {transaction_type}, Amount: {amount}, New Balance: {bank_account.current_balance}")
        
        return transaction
        
    except Exception as e:
        print(f"Error creating bank transaction: {str(e)}")
        return None

def reverse_bank_transaction(reference_type, reference_id):
    """
    Reverse a bank transaction (for cancellations/deletions)

    Args:
        reference_type: Type of source transaction
        reference_id: ID of source transaction

    Returns:
        True if successful, False otherwise
    """
    try:
        # Find the original transaction
        transaction = BankTransaction.query.filter_by(
            reference_type=reference_type,
            reference_id=reference_id
        ).first()

        if not transaction:
            print(f"No bank transaction found for {reference_type} #{reference_id}")
            return False

        bank_account = transaction.bank_account

        # Reverse the bank account balance
        if transaction.transaction_type == 'deposit':
            # Reverse deposit = withdrawal
            bank_account.current_balance -= transaction.amount
            reverse_type = 'withdrawal'
        else:
            # Reverse withdrawal = deposit
            bank_account.current_balance += transaction.amount
            reverse_type = 'deposit'

        # Reverse linked accounting account balance if exists
        if bank_account.account_id:
            accounting_account = Account.query.get(bank_account.account_id)
            if accounting_account:
                if transaction.transaction_type == 'deposit':
                    # Reverse deposit: decrease debit balance
                    accounting_account.debit_balance -= transaction.amount
                    accounting_account.current_balance = accounting_account.debit_balance - accounting_account.credit_balance
                else:
                    # Reverse withdrawal: increase debit balance
                    accounting_account.debit_balance += transaction.amount
                    accounting_account.current_balance = accounting_account.debit_balance - accounting_account.credit_balance

                print(f"Reversed accounting account {accounting_account.code}: Debit={accounting_account.debit_balance}, Credit={accounting_account.credit_balance}, Balance={accounting_account.current_balance}")

        # Create reverse transaction
        today = datetime.utcnow()
        prefix = f'BT{today.year}{today.month:02d}{today.day:02d}'

        last_trans = BankTransaction.query.filter(
            BankTransaction.transaction_number.like(f'{prefix}%')
        ).order_by(BankTransaction.id.desc()).first()

        if last_trans:
            last_num = int(last_trans.transaction_number[-4:])
            trans_number = f'{prefix}{(last_num + 1):04d}'
        else:
            trans_number = f'{prefix}0001'

        reverse_transaction = BankTransaction(
            transaction_number=trans_number,
            transaction_date=today.date(),
            bank_account_id=bank_account.id,
            transaction_type=reverse_type,
            amount=transaction.amount,
            reference_type=f'{reference_type}_reversal',
            reference_id=reference_id,
            description=f'عكس: {transaction.description}',
            balance_after=bank_account.current_balance,
            user_id=current_user.id if current_user.is_authenticated else None
        )

        db.session.add(reverse_transaction)

        print(f"Bank transaction reversed: {trans_number}, New Balance: {bank_account.current_balance}")

        return True

    except Exception as e:
        print(f"Error reversing bank transaction: {str(e)}")
        return False


def sync_bank_accounts_with_accounting():
    """
    Synchronize all bank accounts with their linked accounting accounts
    This function recalculates accounting account balances based on bank account balances

    Returns:
        dict: Summary of synchronization results
    """
    try:
        synced_count = 0
        skipped_count = 0
        error_count = 0
        results = []

        # Get all active bank accounts that are linked to accounting accounts
        bank_accounts = BankAccount.query.filter(
            BankAccount.is_active == True,
            BankAccount.account_id.isnot(None)
        ).all()

        for bank_account in bank_accounts:
            try:
                accounting_account = Account.query.get(bank_account.account_id)

                if not accounting_account:
                    skipped_count += 1
                    results.append({
                        'bank_account': bank_account.account_name,
                        'status': 'skipped',
                        'reason': 'Linked accounting account not found'
                    })
                    continue

                # Calculate the difference
                old_balance = accounting_account.current_balance

                # For bank accounts (assets), the balance should equal debit_balance - credit_balance
                # We need to adjust debit_balance to match bank account balance
                # Assuming credit_balance should remain unchanged
                required_debit = bank_account.current_balance + accounting_account.credit_balance

                accounting_account.debit_balance = required_debit
                accounting_account.current_balance = accounting_account.debit_balance - accounting_account.credit_balance

                synced_count += 1
                results.append({
                    'bank_account': bank_account.account_name,
                    'accounting_account': accounting_account.code,
                    'status': 'synced',
                    'old_balance': old_balance,
                    'new_balance': accounting_account.current_balance,
                    'bank_balance': bank_account.current_balance
                })

                print(f"Synced: {bank_account.account_name} -> {accounting_account.code}: {old_balance} -> {accounting_account.current_balance}")

            except Exception as e:
                error_count += 1
                results.append({
                    'bank_account': bank_account.account_name,
                    'status': 'error',
                    'error': str(e)
                })
                print(f"Error syncing {bank_account.account_name}: {str(e)}")

        db.session.commit()

        summary = {
            'total': len(bank_accounts),
            'synced': synced_count,
            'skipped': skipped_count,
            'errors': error_count,
            'results': results
        }

        print(f"\nSync Summary: Total={summary['total']}, Synced={summary['synced']}, Skipped={summary['skipped']}, Errors={summary['errors']}")

        return summary

    except Exception as e:
        db.session.rollback()
        print(f"Error in sync_bank_accounts_with_accounting: {str(e)}")
        return {
            'total': 0,
            'synced': 0,
            'skipped': 0,
            'errors': 1,
            'error': str(e)
        }

