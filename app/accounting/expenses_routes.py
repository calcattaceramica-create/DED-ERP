"""
Expenses routes - مسارات المصروفات
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app.accounting import bp
from app import db
from app.models_accounting import Expense, BankAccount, Account, BankTransaction
from app.auth.decorators import permission_required
from app.utils.bank_helper import create_bank_transaction
from datetime import datetime

@bp.route('/expenses')
@login_required
@permission_required('accounting.view')
def expenses():
    """List expenses - قائمة المصروفات"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', 'all')
    
    query = Expense.query
    
    if category != 'all':
        query = query.filter_by(expense_category=category)
    
    expenses = query.order_by(Expense.expense_date.desc(), Expense.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    # Calculate total
    total_expenses = sum(exp.amount for exp in query.all())
    
    return render_template('accounting/expenses.html',
                         expenses=expenses,
                         current_category=category,
                         total_expenses=total_expenses)

@bp.route('/expenses/add', methods=['GET', 'POST'])
@login_required
@permission_required('accounting.expenses.create')
def add_expense():
    """Add new expense - إضافة مصروف جديد"""
    if request.method == 'POST':
        try:
            # Generate expense number
            today = datetime.utcnow()
            prefix = f'EXP{today.year}{today.month:02d}'
            
            last_expense = Expense.query.filter(
                Expense.expense_number.like(f'{prefix}%')
            ).order_by(Expense.id.desc()).first()
            
            if last_expense:
                last_num = int(last_expense.expense_number[-4:])
                expense_number = f'{prefix}{(last_num + 1):04d}'
            else:
                expense_number = f'{prefix}0001'
            
            payment_method = request.form.get('payment_method')
            bank_account_id = request.form.get('bank_account_id', type=int) if payment_method == 'bank' else None
            amount = float(request.form.get('amount'))
            
            expense = Expense(
                expense_number=expense_number,
                expense_date=datetime.strptime(request.form.get('expense_date'), '%Y-%m-%d').date(),
                expense_category=request.form.get('expense_category'),
                description=request.form.get('description'),
                amount=amount,
                payment_method=payment_method,
                bank_account_id=bank_account_id,
                account_id=request.form.get('account_id', type=int) if request.form.get('account_id') else None,
                notes=request.form.get('notes'),
                status='posted',
                user_id=current_user.id
            )
            
            db.session.add(expense)
            db.session.flush()
            
            # Update bank account balance if paid by bank
            if payment_method == 'bank' and bank_account_id:
                try:
                    bank_transaction = create_bank_transaction(
                        bank_account_id=bank_account_id,
                        transaction_type='withdrawal',
                        amount=amount,
                        reference_type='expense',
                        reference_id=expense.id,
                        description=f'مصروف: {expense.description}'
                    )
                    if not bank_transaction:
                        flash(_('Warning: Bank transaction was not created'), 'warning')
                except Exception as be:
                    flash(_('Warning: Bank transaction error: %(error)s', error=str(be)), 'warning')
            
            db.session.commit()
            
            flash(_('Expense added successfully'), 'success')
            return redirect(url_for('accounting.expenses'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    # Get data for dropdowns
    bank_accounts = BankAccount.query.filter_by(is_active=True).all()
    expense_accounts = Account.query.filter_by(account_type='expense', is_active=True).order_by(Account.code).all()
    
    # Expense categories
    categories = [
        ('rent', 'إيجار'),
        ('utilities', 'مرافق (كهرباء، ماء، إنترنت)'),
        ('salaries', 'رواتب'),
        ('maintenance', 'صيانة'),
        ('transportation', 'مواصلات'),
        ('office_supplies', 'مستلزمات مكتبية'),
        ('marketing', 'تسويق وإعلان'),
        ('insurance', 'تأمين'),
        ('taxes', 'ضرائب ورسوم'),
        ('other', 'أخرى')
    ]
    
    return render_template('accounting/add_expense.html',
                         bank_accounts=bank_accounts,
                         expense_accounts=expense_accounts,
                         categories=categories,
                         today=datetime.utcnow().strftime('%Y-%m-%d'))

@bp.route('/expenses/<int:id>')
@login_required
@permission_required('accounting.view')
def expense_details(id):
    """View expense details - تفاصيل المصروف"""
    expense = Expense.query.get_or_404(id)
    return render_template('accounting/expense_details.html', expense=expense)

@bp.route('/expenses/<int:id>/delete', methods=['POST', 'GET'])
@login_required
@permission_required('accounting.expenses.delete')
def delete_expense(id):
    """Delete expense - حذف المصروف"""
    try:
        expense = Expense.query.get_or_404(id)

        # Check if expense is posted
        if expense.status == 'posted':
            # If paid by bank, reverse the bank transaction
            if expense.payment_method == 'bank' and expense.bank_account_id:
                bank_account = BankAccount.query.get(expense.bank_account_id)
                if bank_account:
                    # Add back to bank balance
                    bank_account.current_balance += expense.amount

                    # Delete related bank transaction
                    BankTransaction.query.filter_by(
                        reference_type='expense',
                        reference_id=expense.id
                    ).delete()

        # Delete the expense
        db.session.delete(expense)
        db.session.commit()

        flash('تم حذف المصروف بنجاح', 'success')
        return redirect(url_for('accounting.expenses'))

    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف المصروف: {str(e)}', 'danger')
        return redirect(url_for('accounting.expense_details', id=id))

