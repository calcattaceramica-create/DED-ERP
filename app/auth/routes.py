from flask import render_template, redirect, url_for, flash, request, session, current_app, make_response
from flask_login import login_user, logout_user, current_user
from flask_babel import gettext as _
from app import db
from app.auth import bp
from app.models import User, SecurityLog, SessionLog
from app.models_tenant import Tenant
from datetime import datetime, timedelta
import uuid

def get_client_ip():
    """Get client IP address"""
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For')
        # Ensure it's a string, not bytes
        if isinstance(ip, bytes):
            ip = ip.decode('utf-8', errors='ignore')
        return ip.split(',')[0].strip()
    return request.remote_addr or '0.0.0.0'

def get_user_agent():
    """Get user agent string safely"""
    user_agent = request.headers.get('User-Agent', '')
    # Ensure it's a string, not bytes
    if isinstance(user_agent, bytes):
        user_agent = user_agent.decode('utf-8', errors='ignore')
    return user_agent[:256]

def log_security_event(user_id, event_type, details=None, severity='info'):
    """Log security event"""
    try:
        log = SecurityLog(
            user_id=user_id,
            event_type=event_type,
            ip_address=get_client_ip(),
            user_agent=get_user_agent(),
            details=details,
            severity=severity
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging security event: {e}")

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            log_security_event(None, 'failed_login',
                             f'Failed login attempt for username: {username}', 'warning')
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            log_security_event(user.id, 'inactive_login_attempt',
                             'Inactive user tried to login', 'warning')
            flash('هذا الحساب غير نشط. يرجى التواصل مع المسؤول', 'danger')
            return redirect(url_for('auth.login'))

        # Login successful
        login_user(user, remember=remember)
        
        # Create session log
        session_id = str(uuid.uuid4())
        session_log = SessionLog(
            user_id=user.id,
            session_id=session_id,
            ip_address=get_client_ip(),
            user_agent=get_user_agent(),
            is_active=True
        )
        db.session.add(session_log)
        db.session.commit()

        # Store session info
        session['session_log_id'] = session_log.id

        log_security_event(user.id, 'successful_login', 'User logged in successfully', 'info')
        
        flash(f'مرحباً {user.username}!', 'success')
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        log_security_event(current_user.id, 'logout', 'User logged out', 'info')
        
        # Mark session as inactive
        session_log_id = session.get('session_log_id')
        if session_log_id:
            session_log = SessionLog.query.get(session_log_id)
            if session_log:
                session_log.is_active = False
                session_log.logout_at = datetime.utcnow()
                db.session.commit()
    
    logout_user()
    session.clear()
    
    # Create response and explicitly delete cookies
    response = make_response(redirect(url_for('auth.login')))
    response.set_cookie('session', '', expires=0)
    response.set_cookie('remember_token', '', expires=0)
    
    flash('تم تسجيل الخروج بنجاح', 'info')
    return response

@bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('كلمة المرور الحالية غير صحيحة', 'danger')
            return redirect(url_for('auth.change_password'))
        
        if new_password != confirm_password:
            flash('كلمة المرور الجديدة غير متطابقة', 'danger')
            return redirect(url_for('auth.change_password'))
        
        current_user.set_password(new_password)
        db.session.commit()
        
        log_security_event(current_user.id, 'password_change', 'User changed password', 'info')
        flash('تم تغيير كلمة المرور بنجاح', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/change_password.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register new company with admin user - تسجيل شركة جديدة مع مستخدم مدير"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            # Company Information
            company_name = request.form.get('company_name')
            company_name_en = request.form.get('company_name_en')
            company_email = request.form.get('company_email')
            company_phone = request.form.get('company_phone')
            company_address = request.form.get('company_address')
            company_city = request.form.get('company_city')
            tax_number = request.form.get('tax_number')
            commercial_register = request.form.get('commercial_register')

            # Admin User Information
            admin_username = request.form.get('admin_username')
            admin_email = request.form.get('admin_email')
            admin_password = request.form.get('admin_password')
            admin_full_name = request.form.get('admin_full_name')
            admin_phone = request.form.get('admin_phone')

            # Validation
            if not all([company_name, company_email, admin_username, admin_email, admin_password]):
                flash('الرجاء ملء جميع الحقول المطلوبة', 'danger')
                return redirect(url_for('auth.register'))

            # Generate unique company code and subdomain
            import random
            import string

            # Generate company code (e.g., COMP001)
            last_tenant = Tenant.query.order_by(Tenant.id.desc()).first()
            if last_tenant:
                last_num = int(last_tenant.code.replace('COMP', '')) if last_tenant.code.startswith('COMP') else 0
                company_code = f'COMP{(last_num + 1):03d}'
            else:
                company_code = 'COMP001'

            # Generate subdomain from company name (remove spaces and special chars)
            subdomain_base = ''.join(c for c in company_name.lower() if c.isalnum())[:20]
            subdomain = subdomain_base

            # Check if subdomain exists, add random suffix if needed
            counter = 1
            while Tenant.query.filter_by(subdomain=subdomain).first():
                subdomain = f'{subdomain_base}{counter}'
                counter += 1

            # Check if admin username or email already exists
            if User.query.filter_by(username=admin_username).first():
                flash('اسم المستخدم موجود مسبقاً', 'danger')
                return redirect(url_for('auth.register'))

            if User.query.filter_by(email=admin_email).first():
                flash('البريد الإلكتروني موجود مسبقاً', 'danger')
                return redirect(url_for('auth.register'))

            # Create new tenant (company)
            tenant = Tenant(
                code=company_code,
                subdomain=subdomain,
                name=company_name,
                name_en=company_name_en,
                email=company_email,
                phone=company_phone,
                address=company_address,
                city=company_city,
                tax_number=tax_number,
                commercial_register=commercial_register,
                plan='basic',  # Default plan
                max_users=5,
                max_branches=1,
                max_products=100,
                max_invoices_per_month=50,
                is_active=True,
                is_trial=True,
                trial_ends_at=datetime.utcnow() + timedelta(days=30),  # 30 days trial
                currency='SAR',
                tax_rate=15.0,
                language='ar'
            )

            db.session.add(tenant)
            db.session.flush()  # Get tenant.id

            # Create admin user for this tenant
            admin_user = User(
                tenant_id=tenant.id,
                username=admin_username,
                email=admin_email,
                full_name=admin_full_name,
                phone=admin_phone,
                is_active=True,
                is_admin=True,
                is_super_admin=False,
                language='ar'
            )
            admin_user.set_password(admin_password)

            db.session.add(admin_user)
            db.session.flush()  # Get admin_user.id

            # Link admin user to tenant
            tenant.admin_user_id = admin_user.id

            db.session.commit()

            # Log the registration
            log_security_event(admin_user.id, 'company_registration',
                             f'New company registered: {company_name} (Code: {company_code})', 'info')

            # Auto-login the admin user
            login_user(admin_user, remember=False)

            # Store tenant_id in session
            session['tenant_id'] = tenant.id

            # Create session log
            session_id = str(uuid.uuid4())
            session_log = SessionLog(
                user_id=admin_user.id,
                session_id=session_id,
                ip_address=get_client_ip(),
                user_agent=get_user_agent(),
                is_active=True
            )
            db.session.add(session_log)
            db.session.commit()

            session['session_log_id'] = session_log.id

            flash(f'مرحباً بك! تم إنشاء شركتك "{company_name}" بنجاح. لديك فترة تجريبية مجانية لمدة 30 يوم.', 'success')
            flash(f'رمز الشركة: {company_code} | النطاق الفرعي: {subdomain}', 'info')

            return redirect(url_for('main.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء التسجيل: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')
