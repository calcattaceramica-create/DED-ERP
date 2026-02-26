from flask import render_template, redirect, url_for, flash, request, jsonify, current_app, send_file, session
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app.settings import bp
from app import db
from app.models import Company, Branch, User, Role, Permission, RolePermission
from app.models_settings import AccountingSettings
from app.models_accounting import Account, BankAccount
from app.models_currency import Currency, ExchangeRate
from app.auth.decorators import admin_required, permission_required, any_permission_required
import os
import shutil
import zipfile
import json
from datetime import datetime, date
from werkzeug.utils import secure_filename

@bp.route('/')
@login_required
def index():
    """Settings dashboard"""
    return render_template('settings/index.html')

@bp.route('/company')
@login_required
@permission_required('settings.company.view')
def company():
    """Company settings"""
    company = Company.query.first()
    return render_template('settings/company.html', company=company)

@bp.route('/company/update', methods=['POST'])
@login_required
@permission_required('settings.company.edit')
def update_company():
    """Update company information"""
    try:
        company = Company.query.first()

        if not company:
            flash('لم يتم العثور على بيانات الشركة', 'danger')
            return redirect(url_for('settings.company'))

        company.name = request.form.get('name')
        company.name_en = request.form.get('name_en')
        company.tax_number = request.form.get('tax_number')
        company.commercial_register = request.form.get('commercial_register')
        company.phone = request.form.get('phone')
        company.email = request.form.get('email')
        company.website = request.form.get('website')
        company.address = request.form.get('address')
        company.city = request.form.get('city')
        company.country = request.form.get('country')
        company.currency = request.form.get('currency', 'SAR')
        company.tax_rate = float(request.form.get('tax_rate', 15.0))

        # Handle logo upload
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename:
                # Secure the filename
                filename = secure_filename(logo_file.filename)

                # Create uploads directory if it doesn't exist
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)

                # Save the file
                file_path = os.path.join(upload_folder, filename)
                logo_file.save(file_path)

                # Update company logo
                company.logo = filename

        db.session.commit()
        flash('تم تحديث بيانات الشركة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.company'))

@bp.route('/company/create', methods=['POST'])
@login_required
@permission_required('settings.company.edit')
def create_company():
    """Create company information"""
    try:
        # Check if company already exists
        existing_company = Company.query.first()
        if existing_company:
            flash('بيانات الشركة موجودة بالفعل', 'warning')
            return redirect(url_for('settings.company'))

        company = Company(
            name=request.form.get('name'),
            name_en=request.form.get('name_en'),
            tax_number=request.form.get('tax_number'),
            phone=request.form.get('phone'),
            currency='SAR',
            tax_rate=15.0
        )

        db.session.add(company)
        db.session.commit()
        flash('تم إنشاء بيانات الشركة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.company'))

@bp.route('/invoice-templates')
@login_required
@permission_required('settings.company.view')
def invoice_templates():
    """Invoice templates settings"""
    company = Company.query.first()
    return render_template('settings/invoice_templates.html', company=company)

@bp.route('/invoice-templates/update', methods=['POST'])
@login_required
@permission_required('settings.company.edit')
def update_invoice_template():
    """Update invoice template"""
    try:
        company = Company.query.first()

        if not company:
            flash('لم يتم العثور على بيانات الشركة', 'danger')
            return redirect(url_for('settings.company'))

        template = request.form.get('template', 'modern')

        # Validate template
        valid_templates = ['modern', 'classic', 'minimal', 'elegant', 'dark', 'ocean', 'sunset', 'corporate']
        if template not in valid_templates:
            flash('شكل الفاتورة غير صحيح', 'danger')
            return redirect(url_for('settings.invoice_templates'))

        company.invoice_template = template
        db.session.commit()

        template_names = {
            'modern':    'عصري (Modern)',
            'classic':   'كلاسيكي (Classic)',
            'minimal':   'بسيط (Minimal)',
            'elegant':   'أنيق (Elegant)',
            'dark':      'داكن (Dark)',
            'ocean':     'محيطي (Ocean)',
            'sunset':    'غروب (Sunset)',
            'corporate': 'مؤسسي (Corporate)',
        }

        flash(f'تم تحديث شكل الفاتورة إلى: {template_names.get(template, template)}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.invoice_templates'))

@bp.route('/branches')
@login_required
@permission_required('settings.branches.view')
def branches():
    """Branches management"""
    branches = Branch.query.all()
    return render_template('settings/branches.html', branches=branches)

@bp.route('/branches/add', methods=['POST'])
@login_required
@permission_required('settings.branches.add')
def add_branch():
    """Add new branch"""
    try:
        branch = Branch(
            name=request.form.get('name'),
            name_en=request.form.get('name_en'),
            code=request.form.get('code'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            phone=request.form.get('phone'),
            manager_id=request.form.get('manager_id') if request.form.get('manager_id') else None,
            is_active=request.form.get('is_active') == 'on'
        )

        db.session.add(branch)
        db.session.commit()
        flash('تم إضافة الفرع بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.branches'))

@bp.route('/branches/edit/<int:id>', methods=['POST'])
@login_required
@permission_required('settings.branches.edit')
def edit_branch(id):
    """Edit branch"""
    try:
        branch = Branch.query.get_or_404(id)

        branch.name = request.form.get('name')
        branch.name_en = request.form.get('name_en')
        branch.code = request.form.get('code')
        branch.address = request.form.get('address')
        branch.city = request.form.get('city')
        branch.phone = request.form.get('phone')
        branch.manager_id = request.form.get('manager_id') if request.form.get('manager_id') else None
        branch.is_active = request.form.get('is_active') == 'on'

        db.session.commit()
        flash('تم تحديث الفرع بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.branches'))

@bp.route('/branches/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('settings.branches.delete')
def delete_branch(id):
    """Delete branch"""
    try:
        branch = Branch.query.get_or_404(id)
        db.session.delete(branch)
        db.session.commit()
        flash('تم حذف الفرع بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.branches'))

@bp.route('/users')
@login_required
@permission_required('settings.users.view')
def users():
    """Users management"""
    users = User.query.all()
    roles = Role.query.all()
    branches = Branch.query.all()
    return render_template('settings/users.html', users=users, roles=roles, branches=branches)

@bp.route('/users/add', methods=['POST'])
@login_required
@permission_required('settings.users.add')
def add_user():
    """Add new user"""
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        role_id = request.form.get('role_id')
        branch_id = request.form.get('branch_id')
        is_active = request.form.get('is_active') == 'on'

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('اسم المستخدم موجود مسبقاً', 'danger')
            return redirect(url_for('settings.users'))

        if User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني موجود مسبقاً', 'danger')
            return redirect(url_for('settings.users'))

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role_id=role_id if role_id else None,
            branch_id=branch_id if branch_id else None,
            is_active=is_active
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('تم إضافة المستخدم بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.users'))

@bp.route('/users/edit/<int:id>', methods=['POST'])
@login_required
@permission_required('settings.users.edit')
def edit_user(id):
    """Edit user"""
    try:
        user = User.query.get_or_404(id)

        user.full_name = request.form.get('full_name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.role_id = request.form.get('role_id') if request.form.get('role_id') else None
        user.branch_id = request.form.get('branch_id') if request.form.get('branch_id') else None
        user.is_active = request.form.get('is_active') == 'on'

        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)

        db.session.commit()
        flash('تم تحديث المستخدم بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.users'))

@bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('settings.users.delete')
def delete_user(id):
    """Delete user"""
    try:
        user = User.query.get_or_404(id)

        # Prevent deleting yourself
        if user.id == current_user.id:
            flash('لا يمكنك حذف حسابك الخاص', 'danger')
            return redirect(url_for('settings.users'))

        db.session.delete(user)
        db.session.commit()
        flash('تم حذف المستخدم بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.users'))

@bp.route('/users/<int:id>/permissions')
@login_required
@permission_required('settings.users.view')
def get_user_permissions(id):
    """Get user permissions as JSON"""
    from flask import jsonify

    user = User.query.get_or_404(id)

    if user.is_admin:
        return jsonify({
            'is_admin': True,
            'permissions': []
        })

    if not user.role:
        return jsonify({
            'is_admin': False,
            'permissions': []
        })

    permissions_list = []
    for perm in user.role.permissions:
        permissions_list.append({
            'id': perm.id,
            'name': perm.name,
            'name_ar': perm.name_ar,
            'module': perm.module or 'general'
        })

    return jsonify({
        'is_admin': False,
        'permissions': permissions_list
    })

@bp.route('/roles')
@login_required
@permission_required('settings.roles.view')
def roles():
    """Roles management"""
    roles = Role.query.all()
    permissions = Permission.query.all()
    return render_template('settings/roles.html', roles=roles, permissions=permissions)

@bp.route('/roles/add', methods=['POST'])
@login_required
@permission_required('settings.roles.add')
def add_role():
    """Add new role"""
    try:
        name = request.form.get('name')
        name_ar = request.form.get('name_ar')
        description = request.form.get('description')

        # Check if role already exists
        if Role.query.filter_by(name=name).first():
            flash('الدور موجود مسبقاً', 'danger')
            return redirect(url_for('settings.roles'))

        role = Role(
            name=name,
            name_ar=name_ar,
            description=description
        )

        db.session.add(role)
        db.session.commit()

        flash('تم إضافة الدور بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.roles'))

@bp.route('/roles/edit/<int:id>', methods=['POST'])
@login_required
@permission_required('settings.roles.edit')
def edit_role(id):
    """Edit role"""
    try:
        role = Role.query.get_or_404(id)

        role.name_ar = request.form.get('name_ar')
        role.description = request.form.get('description')

        db.session.commit()
        flash('تم تحديث الدور بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.roles'))

@bp.route('/roles/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('settings.roles.delete')
def delete_role(id):
    """Delete role"""
    try:
        role = Role.query.get_or_404(id)

        # Check if role is in use
        if role.users:
            flash('لا يمكن حذف الدور لأنه مستخدم من قبل مستخدمين', 'danger')
            return redirect(url_for('settings.roles'))

        db.session.delete(role)
        db.session.commit()
        flash('تم حذف الدور بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.roles'))

@bp.route('/roles/<int:id>/permissions', methods=['POST'])
@login_required
@permission_required('settings.roles.edit')
def update_role_permissions(id):
    """Update role permissions"""
    try:
        role = Role.query.get_or_404(id)

        # Get selected permissions
        permission_ids = request.form.getlist('permissions')

        # Log the update for debugging
        current_app.logger.info(f'Updating permissions for role {role.name} (ID: {role.id})')
        current_app.logger.info(f'Selected permission IDs: {permission_ids}')

        # Clear existing permissions
        deleted_count = RolePermission.query.filter_by(role_id=role.id).delete()
        current_app.logger.info(f'Deleted {deleted_count} existing permissions')

        # Add new permissions
        added_count = 0
        for permission_id in permission_ids:
            role_permission = RolePermission(
                role_id=role.id,
                permission_id=int(permission_id)
            )
            db.session.add(role_permission)
            added_count += 1

        db.session.commit()

        current_app.logger.info(f'Added {added_count} new permissions')

        # Success message with details
        if session.get('language') == 'en':
            flash(f'Successfully updated permissions for role "{role.name}". Total permissions: {added_count}', 'success')
        else:
            flash(f'تم تحديث صلاحيات الدور "{role.name_ar}" بنجاح. إجمالي الصلاحيات: {added_count}', 'success')

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating role permissions: {str(e)}')

        if session.get('language') == 'en':
            flash(f'Error updating permissions: {str(e)}', 'danger')
        else:
            flash(f'حدث خطأ أثناء تحديث الصلاحيات: {str(e)}', 'danger')

    return redirect(url_for('settings.roles'))

@bp.route('/permissions')
@login_required
@permission_required('settings.permissions.view')
def permissions():
    """Permissions management"""
    permissions = Permission.query.all()
    return render_template('settings/permissions.html', permissions=permissions)

@bp.route('/permissions/add', methods=['POST'])
@login_required
@permission_required('settings.permissions.add')
def add_permission():
    """Add new permission"""
    try:
        name = request.form.get('name')
        name_ar = request.form.get('name_ar')
        module = request.form.get('module')

        # Check if permission already exists
        if Permission.query.filter_by(name=name).first():
            flash('الصلاحية موجودة مسبقاً', 'danger')
            return redirect(url_for('settings.permissions'))

        permission = Permission(
            name=name,
            name_ar=name_ar,
            module=module
        )

        db.session.add(permission)
        db.session.commit()

        flash('تم إضافة الصلاحية بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.permissions'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile"""
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.full_name_en = request.form.get('full_name_en') or None
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')
        current_user.language = request.form.get('language', 'ar')

        # Update session language
        from flask import session
        session['language'] = current_user.language

        # Change password if provided
        new_password = request.form.get('new_password')
        if new_password:
            current_user.set_password(new_password)

        db.session.commit()
        flash('تم تحديث الملف الشخصي بنجاح', 'success')
        return redirect(url_for('settings.profile'))

    return render_template('settings/profile.html')

@bp.route('/language')
@login_required
def language_settings():
    """Language settings page"""
    from flask import current_app
    available_languages = current_app.config.get('LANGUAGES', ['ar', 'en'])
    return render_template('settings/language.html', available_languages=available_languages)

@bp.route('/language/change', methods=['POST', 'GET'])
@login_required
def change_language():
    """Change application language"""
    try:
        # Get language from POST or GET
        language = request.form.get('language') or request.args.get('lang', 'ar')

        # Validate language
        from flask import current_app, session
        available_languages = current_app.config.get('LANGUAGES', {})

        if language not in available_languages:
            flash(_('Selected language is not supported'), 'danger')
            return redirect(request.referrer or url_for('main.index'))

        # Update user language
        current_user.language = language

        # Update session
        session['language'] = language
        session.modified = True

        db.session.commit()

        # Success message based on language
        if language == 'ar':
            flash('تم تغيير اللغة بنجاح', 'success')
        else:
            flash('Language changed successfully', 'success')

    except Exception as e:
        db.session.rollback()
        flash(_('An error occurred: %(error)s', error=str(e)), 'danger')

    # Redirect back to previous page or home with cache-busting parameter
    import time
    redirect_url = request.referrer or url_for('main.index')
    # Add timestamp to force reload
    separator = '&' if '?' in redirect_url else '?'
    redirect_url = f"{redirect_url}{separator}_t={int(time.time())}"
    return redirect(redirect_url)

@bp.route('/accounting-settings')
@login_required
def accounting_settings():
    """Accounting settings page"""
    settings = AccountingSettings.query.first()

    # Get accounts by type
    asset_accounts = Account.query.filter_by(account_type='asset', is_active=True).all()
    liability_accounts = Account.query.filter_by(account_type='liability', is_active=True).all()
    revenue_accounts = Account.query.filter_by(account_type='revenue', is_active=True).all()
    expense_accounts = Account.query.filter_by(account_type='expense', is_active=True).all()

    return render_template('settings/accounting_settings.html',
                         settings=settings,
                         asset_accounts=asset_accounts,
                         liability_accounts=liability_accounts,
                         revenue_accounts=revenue_accounts,
                         expense_accounts=expense_accounts)

@bp.route('/accounting-settings/save', methods=['POST'])
@login_required
def save_accounting_settings():
    """Save accounting settings"""
    try:
        settings = AccountingSettings.query.first()

        if not settings:
            settings = AccountingSettings()
            db.session.add(settings)

        # Sales accounts
        settings.sales_revenue_account_id = request.form.get('sales_revenue_account_id', type=int)
        settings.sales_tax_account_id = request.form.get('sales_tax_account_id', type=int)
        settings.sales_discount_account_id = request.form.get('sales_discount_account_id', type=int)
        settings.accounts_receivable_account_id = request.form.get('accounts_receivable_account_id', type=int)
        settings.sales_cost_account_id = request.form.get('sales_cost_account_id', type=int)

        # Purchase accounts
        settings.purchase_expense_account_id = request.form.get('purchase_expense_account_id', type=int)
        settings.purchase_tax_account_id = request.form.get('purchase_tax_account_id', type=int)
        settings.purchase_discount_account_id = request.form.get('purchase_discount_account_id', type=int)
        settings.accounts_payable_account_id = request.form.get('accounts_payable_account_id', type=int)

        # Inventory accounts
        settings.inventory_account_id = request.form.get('inventory_account_id', type=int)
        settings.inventory_adjustment_account_id = request.form.get('inventory_adjustment_account_id', type=int)

        # Cash accounts
        settings.cash_account_id = request.form.get('cash_account_id', type=int)

        # POS accounts
        settings.pos_cash_account_id = request.form.get('pos_cash_account_id', type=int)
        settings.pos_card_account_id = request.form.get('pos_card_account_id', type=int)

        # Automation settings
        settings.auto_create_journal_entries = 'auto_create_journal_entries' in request.form
        settings.auto_post_journal_entries = 'auto_post_journal_entries' in request.form

        db.session.commit()
        flash('تم حفظ إعدادات الحسابات المحاسبية بنجاح', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.accounting_settings'))

@bp.route('/tax-settings')
@login_required
def tax_settings():
    """Tax settings page"""
    company = Company.query.first()
    return render_template('settings/tax_settings.html', company=company)

@bp.route('/tax-settings/save', methods=['POST'])
@login_required
def save_tax_settings():
    """Save tax settings"""
    try:
        company = Company.query.first()

        if not company:
            flash('لم يتم العثور على بيانات الشركة', 'danger')
            return redirect(url_for('settings.tax_settings'))

        # Update tax settings
        tax_rate = request.form.get('default_tax_rate')
        tax_number = request.form.get('tax_number', '')

        if tax_rate:
            company.tax_rate = float(tax_rate)
        company.tax_number = tax_number

        db.session.commit()
        flash('تم حفظ إعدادات الضرائب بنجاح', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.tax_settings'))

# ============================================================================
# Backup Routes
# ============================================================================

@bp.route('/backup')
@login_required
@permission_required('settings.manage')
def backup():
    """Backup management page"""
    basedir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    backup_dir = os.path.join(basedir, 'backups')

    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Get list of existing backups
    backups = []
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.endswith('.zip'):
                filepath = os.path.join(backup_dir, filename)
                file_stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'size_mb': round(file_stat.st_size / (1024 * 1024), 2),
                    'created_at': datetime.fromtimestamp(file_stat.st_ctime),
                    'path': filepath
                })

    # Sort by creation date (newest first)
    backups.sort(key=lambda x: x['created_at'], reverse=True)

    return render_template('settings/backup.html', backups=backups)

@bp.route('/backup/create', methods=['POST'])
@login_required
@permission_required('settings.manage')
def create_backup():
    """Create a new backup"""
    try:
        basedir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        backup_dir = os.path.join(basedir, 'backups')

        # Create backup directory if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.zip'
        backup_path = os.path.join(backup_dir, backup_filename)

        # Create zip file
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Backup database
            db_path = os.path.join(basedir, 'erp_system.db')
            if os.path.exists(db_path):
                zipf.write(db_path, 'erp_system.db')

            # Backup uploads folder
            uploads_dir = os.path.join(basedir, 'uploads')
            if os.path.exists(uploads_dir):
                for root, dirs, files in os.walk(uploads_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, basedir)
                        zipf.write(file_path, arcname)

            # Backup config file
            config_path = os.path.join(basedir, 'config.py')
            if os.path.exists(config_path):
                zipf.write(config_path, 'config.py')

            # Create backup info file
            backup_info = {
                'created_at': datetime.now().isoformat(),
                'created_by': current_user.username,
                'database': 'erp_system.db',
                'version': '1.0'
            }
            zipf.writestr('backup_info.json', json.dumps(backup_info, indent=2, ensure_ascii=False))

        flash(f'✅ تم إنشاء النسخة الاحتياطية بنجاح: {backup_filename}', 'success')

    except Exception as e:
        flash(f'❌ حدث خطأ أثناء إنشاء النسخة الاحتياطية: {str(e)}', 'danger')

    return redirect(url_for('settings.backup'))

@bp.route('/backup/download/<filename>')
@login_required
@permission_required('settings.manage')
def download_backup(filename):
    """Download a backup file"""
    try:
        basedir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        backup_dir = os.path.join(basedir, 'backups')
        backup_path = os.path.join(backup_dir, filename)

        if not os.path.exists(backup_path):
            flash('❌ الملف غير موجود', 'danger')
            return redirect(url_for('settings.backup'))

        return send_file(backup_path, as_attachment=True, download_name=filename)

    except Exception as e:
        flash(f'❌ حدث خطأ أثناء تحميل النسخة الاحتياطية: {str(e)}', 'danger')
        return redirect(url_for('settings.backup'))

@bp.route('/backup/delete/<filename>', methods=['POST'])
@login_required
@permission_required('settings.manage')
def delete_backup(filename):
    """Delete a backup file"""
    try:
        basedir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        backup_dir = os.path.join(basedir, 'backups')
        backup_path = os.path.join(backup_dir, filename)

        if os.path.exists(backup_path):
            os.remove(backup_path)
            flash(f'✅ تم حذف النسخة الاحتياطية: {filename}', 'success')
        else:
            flash('❌ الملف غير موجود', 'danger')

    except Exception as e:
        flash(f'❌ حدث خطأ أثناء حذف النسخة الاحتياطية: {str(e)}', 'danger')

    return redirect(url_for('settings.backup'))

# ============================================================================
# Currency Management Routes
# ============================================================================

@bp.route('/currencies')
@login_required
@permission_required('settings.manage')
def currencies():
    """Currency management page"""
    currencies = Currency.query.all()
    return render_template('settings/currencies.html', currencies=currencies)

@bp.route('/currencies/add', methods=['POST'])
@login_required
@permission_required('settings.manage')
def add_currency():
    """Add new currency"""
    try:
        # Check if currency code already exists
        existing = Currency.query.filter_by(code=request.form.get('code')).first()
        if existing:
            flash('❌ رمز العملة موجود بالفعل', 'danger')
            return redirect(url_for('settings.currencies'))

        currency = Currency(
            code=request.form.get('code').upper(),
            name=request.form.get('name'),
            name_ar=request.form.get('name_ar'),
            symbol=request.form.get('symbol'),
            exchange_rate=float(request.form.get('exchange_rate', 1.0)),
            is_base='is_base' in request.form,
            is_active='is_active' in request.form,
            decimal_places=int(request.form.get('decimal_places', 2))
        )

        # If this is set as base currency, unset all others
        if currency.is_base:
            Currency.query.update({'is_base': False})
            currency.exchange_rate = 1.0

        db.session.add(currency)
        db.session.commit()

        flash(f'✅ تم إضافة العملة {currency.code} بنجاح', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'❌ حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.currencies'))

@bp.route('/currencies/edit/<int:id>', methods=['POST'])
@login_required
@permission_required('settings.manage')
def edit_currency(id):
    """Edit currency"""
    try:
        currency = Currency.query.get_or_404(id)

        currency.name = request.form.get('name')
        currency.name_ar = request.form.get('name_ar')
        currency.symbol = request.form.get('symbol')
        currency.exchange_rate = float(request.form.get('exchange_rate', 1.0))
        currency.is_active = 'is_active' in request.form
        currency.decimal_places = int(request.form.get('decimal_places', 2))

        # Handle base currency
        is_base = 'is_base' in request.form
        if is_base and not currency.is_base:
            # Unset all other base currencies
            Currency.query.update({'is_base': False})
            currency.is_base = True
            currency.exchange_rate = 1.0
        elif not is_base and currency.is_base:
            currency.is_base = False

        db.session.commit()
        flash(f'✅ تم تحديث العملة {currency.code} بنجاح', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'❌ حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.currencies'))

@bp.route('/currencies/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('settings.manage')
def delete_currency(id):
    """Delete currency"""
    try:
        currency = Currency.query.get_or_404(id)

        if currency.is_base:
            flash('❌ لا يمكن حذف العملة الأساسية', 'danger')
            return redirect(url_for('settings.currencies'))

        db.session.delete(currency)
        db.session.commit()

        flash(f'✅ تم حذف العملة {currency.code} بنجاح', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'❌ حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.currencies'))

@bp.route('/exchange-rates')
@login_required
@permission_required('settings.manage')
def exchange_rates():
    """Exchange rates management page"""
    rates = ExchangeRate.query.order_by(ExchangeRate.effective_date.desc()).limit(100).all()
    currencies = Currency.query.filter_by(is_active=True).all()
    return render_template('settings/exchange_rates.html', rates=rates, currencies=currencies)

@bp.route('/exchange-rates/add', methods=['POST'])
@login_required
@permission_required('settings.manage')
def add_exchange_rate():
    """Add new exchange rate"""
    try:
        from_currency_id = request.form.get('from_currency_id', type=int)
        to_currency_id = request.form.get('to_currency_id', type=int)

        if from_currency_id == to_currency_id:
            flash('❌ لا يمكن إضافة سعر صرف للعملة نفسها', 'danger')
            return redirect(url_for('settings.exchange_rates'))

        rate = ExchangeRate(
            from_currency_id=from_currency_id,
            to_currency_id=to_currency_id,
            rate=float(request.form.get('rate')),
            effective_date=datetime.strptime(request.form.get('effective_date'), '%Y-%m-%d').date(),
            source=request.form.get('source', 'manual'),
            notes=request.form.get('notes'),
            created_by=current_user.id
        )

        db.session.add(rate)

        # Update currency exchange rate if this is the latest rate
        from_currency = Currency.query.get(from_currency_id)
        if from_currency and rate.effective_date >= date.today():
            from_currency.exchange_rate = rate.rate

        db.session.commit()

        flash('✅ تم إضافة سعر الصرف بنجاح', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'❌ حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('settings.exchange_rates'))

