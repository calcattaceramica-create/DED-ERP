from flask import render_template, redirect, url_for, flash, request, session, current_app, make_response
from flask_login import login_user, logout_user, current_user
from flask_babel import gettext as _
from app import db
from app.auth import bp
from app.models import User, SecurityLog, SessionLog
from datetime import datetime
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
