from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin privileges (is_admin=True)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def super_admin_required(f):
    """
    Decorator to require super-admin privileges (is_super_admin=True).
    Use this for system-wide operations that cross tenant boundaries:
    - Tenant management
    - License management
    - Global system settings
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
            return redirect(url_for('auth.login'))
        if not getattr(current_user, 'is_super_admin', False):
            flash('هذه الصفحة محجوزة للمسؤول العام فقط', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission_name):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
                return redirect(url_for('auth.login'))
            if not current_user.has_permission(permission_name):
                flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def any_permission_required(*permission_names):
    """Decorator to require any of the specified permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
                return redirect(url_for('auth.login'))
            if not current_user.has_any_permission(*permission_names):
                flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def all_permissions_required(*permission_names):
    """Decorator to require all of the specified permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
                return redirect(url_for('auth.login'))
            if not current_user.has_all_permissions(*permission_names):
                flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

