from flask import render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from app.auth.decorators import permission_required
from app.banking import bp
from app import db
from app.models import BankAccount, BankTransaction, Company
from datetime import datetime, timedelta
from sqlalchemy import func, or_
import json

@bp.route('/add-bank', methods=['GET', 'POST'])
@login_required
@permission_required('accounting.view')
def add_bank():
    """Add new bank account"""
    if request.method == 'POST':
        try:
            # Generate account number if not provided
            account_number = request.form.get('account_number')
            if not account_number:
                # Auto-generate account number
                last_account = BankAccount.query.order_by(BankAccount.id.desc()).first()
                if last_account and last_account.account_number:
                    try:
                        last_num = int(last_account.account_number)
                        account_number = str(last_num + 1).zfill(10)
                    except:
                        account_number = '1000000001'
                else:
                    account_number = '1000000001'
            
            opening_balance = float(request.form.get('opening_balance', 0))

            bank_account = BankAccount(
                account_name=request.form.get('account_name'),
                account_number=account_number,
                bank_name=request.form.get('bank_name'),
                branch=request.form.get('branch_name'),
                iban=request.form.get('iban'),
                swift_code=request.form.get('swift_code'),
                account_type=request.form.get('account_type', 'current'),
                currency=request.form.get('currency', 'SAR'),
                opening_balance=opening_balance,
                current_balance=opening_balance,
                is_active=True if request.form.get('is_active') == 'on' else False,
                notes=request.form.get('notes')
            )
            
            db.session.add(bank_account)
            db.session.flush()
            
            # Create opening balance transaction if > 0
            if opening_balance > 0:
                # Generate transaction number
                today = datetime.utcnow()
                prefix = f'BT{today.year}{today.month:02d}{today.day:02d}'
                last_transaction = BankTransaction.query.filter(
                    BankTransaction.transaction_number.like(f'{prefix}%')
                ).order_by(BankTransaction.id.desc()).first()
                
                if last_transaction:
                    last_num = int(last_transaction.transaction_number[-4:])
                    transaction_number = f'{prefix}{(last_num + 1):04d}'
                else:
                    transaction_number = f'{prefix}0001'
                
                opening_transaction = BankTransaction(
                    transaction_number=transaction_number,
                    transaction_date=datetime.utcnow().date(),
                    bank_account_id=bank_account.id,
                    transaction_type='deposit',
                    amount=opening_balance,
                    reference_type='opening_balance',
                    description='الرصيد الافتتاحي - Opening Balance',
                    balance_after=opening_balance,
                    user_id=current_user.id
                )
                db.session.add(opening_transaction)
            
            db.session.commit()
            flash('تم إضافة الحساب البنكي بنجاح - Bank account added successfully', 'success')
            return redirect(url_for('banking.bank_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في إضافة الحساب البنكي - Error: {str(e)}', 'error')
    
    # Get company for currency
    company = Company.query.first()
    currency = company.currency if company else 'SAR'
    
    return render_template('banking/add_bank.html', currency=currency)

@bp.route('/bank-list')
@login_required
@permission_required('accounting.view')
def bank_list():
    """List all bank accounts"""
    banks = BankAccount.query.order_by(BankAccount.created_at.desc()).all()
    
    # Calculate total balance
    total_balance = sum(bank.current_balance for bank in banks if bank.is_active)
    
    return render_template('banking/bank_list.html', banks=banks, total_balance=total_balance)

@bp.route('/bank/<int:id>')
@login_required
@permission_required('accounting.view')
def bank_details(id):
    """View bank account details with transactions"""
    bank = BankAccount.query.get_or_404(id)
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transaction_type = request.args.get('transaction_type')
    
    # Build query
    query = BankTransaction.query.filter_by(bank_account_id=id)
    
    if start_date:
        query = query.filter(BankTransaction.transaction_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(BankTransaction.transaction_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    if transaction_type and transaction_type != 'all':
        query = query.filter_by(transaction_type=transaction_type)
    
    transactions = query.order_by(BankTransaction.transaction_date.desc(), BankTransaction.created_at.desc()).all()
    
    # Calculate totals
    total_deposits = sum(t.amount for t in transactions if t.transaction_type == 'deposit')
    total_withdrawals = sum(t.amount for t in transactions if t.transaction_type == 'withdrawal')
    
    return render_template('banking/bank_details.html',
                         bank=bank,
                         transactions=transactions,
                         total_deposits=total_deposits,
                         total_withdrawals=total_withdrawals,
                         start_date=start_date,
                         end_date=end_date,
                         transaction_type=transaction_type)

@bp.route('/add-manual-transaction', methods=['GET', 'POST'])
@login_required
@permission_required('accounting.view')
def add_manual_transaction():
    """Add manual bank transaction"""
    if request.method == 'POST':
        try:
            bank_account_id = int(request.form.get('bank_account_id'))
            transaction_type = request.form.get('transaction_type')
            amount = float(request.form.get('amount'))

            bank_account = BankAccount.query.get_or_404(bank_account_id)

            # Generate transaction number
            today = datetime.utcnow()
            prefix = f'BT{today.year}{today.month:02d}{today.day:02d}'
            last_transaction = BankTransaction.query.filter(
                BankTransaction.transaction_number.like(f'{prefix}%')
            ).order_by(BankTransaction.id.desc()).first()

            if last_transaction:
                last_num = int(last_transaction.transaction_number[-4:])
                transaction_number = f'{prefix}{(last_num + 1):04d}'
            else:
                transaction_number = f'{prefix}0001'

            # Update bank balance
            if transaction_type == 'deposit':
                bank_account.current_balance += amount
            else:  # withdrawal
                bank_account.current_balance -= amount

            # Create transaction
            transaction = BankTransaction(
                transaction_number=transaction_number,
                transaction_date=datetime.strptime(request.form.get('transaction_date'), '%Y-%m-%d').date(),
                bank_account_id=bank_account_id,
                transaction_type=transaction_type,
                amount=amount,
                reference_type='manual',
                description=request.form.get('description'),
                notes=request.form.get('notes'),
                balance_after=bank_account.current_balance,
                user_id=current_user.id
            )

            db.session.add(transaction)
            db.session.commit()

            flash('تم إضافة الحركة بنجاح - Transaction added successfully', 'success')
            return redirect(url_for('banking.bank_details', id=bank_account_id))

        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في إضافة الحركة - Error: {str(e)}', 'error')

    banks = BankAccount.query.filter_by(is_active=True).all()
    today = datetime.utcnow().date().strftime('%Y-%m-%d')

    return render_template('banking/add_manual_transaction.html', banks=banks, today=today)

@bp.route('/edit-bank/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('accounting.view')
def edit_bank(id):
    """Edit bank account"""
    bank = BankAccount.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Update bank account details
            bank.account_name = request.form.get('account_name')
            bank.account_number = request.form.get('account_number')
            bank.bank_name = request.form.get('bank_name')
            bank.branch = request.form.get('branch_name')
            bank.iban = request.form.get('iban')
            bank.swift_code = request.form.get('swift_code')
            bank.account_type = request.form.get('account_type', 'current')
            bank.currency = request.form.get('currency', 'SAR')
            bank.is_active = True if request.form.get('is_active') == 'on' else False
            bank.notes = request.form.get('notes')

            db.session.commit()
            flash('تم تحديث الحساب البنكي بنجاح - Bank account updated successfully', 'success')
            return redirect(url_for('banking.bank_details', id=id))

        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في تحديث الحساب البنكي - Error: {str(e)}', 'error')

    # Get company for currency
    company = Company.query.first()
    currency = company.currency if company else 'SAR'

    return render_template('banking/edit_bank.html', bank=bank, currency=currency)

@bp.route('/delete-bank/<int:id>', methods=['POST'])
@login_required
@permission_required('accounting.accounts.delete')
def delete_bank(id):
    """Delete bank account and all related records"""
    from app.models_pos import POSSession
    from app.models_accounting import Payment, Expense
    from app.models_settings import AccountingSettings
    from sqlalchemy import text

    bank = BankAccount.query.get_or_404(id)

    try:
        # Step 1: Remove bank_account_id from POS sessions (set to NULL)
        db.session.execute(
            text("UPDATE pos_sessions SET bank_account_id = NULL WHERE bank_account_id = :id"),
            {"id": id}
        )

        # Step 2: Remove bank_account_id from payments (set to NULL)
        db.session.execute(
            text("UPDATE payments SET bank_account_id = NULL WHERE bank_account_id = :id"),
            {"id": id}
        )

        # Step 3: Remove bank_account_id from expenses (set to NULL)
        db.session.execute(
            text("UPDATE expenses SET bank_account_id = NULL WHERE bank_account_id = :id"),
            {"id": id}
        )

        # Step 4: Remove bank_account_id from sales_invoices (set to NULL)
        db.session.execute(
            text("UPDATE sales_invoices SET bank_account_id = NULL WHERE bank_account_id = :id"),
            {"id": id}
        )

        # Step 5: Remove bank_account_id from purchase_invoices (set to NULL)
        db.session.execute(
            text("UPDATE purchase_invoices SET bank_account_id = NULL WHERE bank_account_id = :id"),
            {"id": id}
        )

        # Step 6: Remove from accounting settings if it's the default
        db.session.execute(
            text("UPDATE accounting_settings SET default_bank_account_id = NULL WHERE default_bank_account_id = :id"),
            {"id": id}
        )

        # Step 7: Delete all bank transactions for this account
        BankTransaction.query.filter_by(bank_account_id=id).delete()

        # Step 8: Delete the bank account
        db.session.delete(bank)
        db.session.commit()

        flash('تم حذف الحساب البنكي وجميع ارتباطاته بنجاح - Bank account and all its references deleted successfully', 'success')
        return redirect(url_for('banking.bank_list'))

    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في حذف الحساب البنكي - Error: {str(e)}', 'error')
        return redirect(url_for('banking.bank_details', id=id))

@bp.route('/bank-statement')
@login_required
@permission_required('accounting.view')
def bank_statement():
    """Bank statement with filters and export"""
    # Get filter parameters
    bank_id = request.args.get('bank_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transaction_type = request.args.get('transaction_type')

    # Build query
    query = BankTransaction.query

    if bank_id:
        query = query.filter_by(bank_account_id=bank_id)
    if start_date:
        query = query.filter(BankTransaction.transaction_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(BankTransaction.transaction_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    if transaction_type and transaction_type != 'all':
        query = query.filter_by(transaction_type=transaction_type)

    transactions = query.order_by(BankTransaction.transaction_date.desc(), BankTransaction.created_at.desc()).all()

    # Calculate totals
    total_deposits = sum(t.amount for t in transactions if t.transaction_type == 'deposit')
    total_withdrawals = sum(t.amount for t in transactions if t.transaction_type == 'withdrawal')
    net_change = total_deposits - total_withdrawals

    # Get all banks for filter
    banks = BankAccount.query.filter_by(is_active=True).all()

    return render_template('banking/bank_statement.html',
                         transactions=transactions,
                         banks=banks,
                         total_deposits=total_deposits,
                         total_withdrawals=total_withdrawals,
                         net_change=net_change,
                         bank_id=bank_id,
                         start_date=start_date,
                         end_date=end_date,
                         transaction_type=transaction_type)

