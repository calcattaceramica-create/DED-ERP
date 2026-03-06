from flask import Blueprint, render_template, request, redirect, url_for, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

from app import db
from app.models import Company, SuperAdmin


super_admin_bp = Blueprint('super_admin', __name__, url_prefix='/super-admin')


def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("super_admin"):
            return redirect(url_for("super_admin.login"))
        return f(*args, **kwargs)
    return decorated_function


@super_admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        admin = SuperAdmin.query.filter_by(email=request.form['email']).first()
        if admin and check_password_hash(admin.password_hash, request.form['password']):
            session['super_admin'] = admin.id
            return redirect(url_for('super_admin.dashboard'))
    return render_template('super_admin/login.html')


@super_admin_bp.route('/logout')
def logout():
    session.pop('super_admin', None)
    return redirect(url_for('super_admin.login'))


@super_admin_bp.route('/dashboard')
@super_admin_required
def dashboard():
    companies = Company.query.all()
    return render_template('super_admin/dashboard.html', companies=companies)


@super_admin_bp.route('/activate/<int:id>')
@super_admin_required
def activate(id):
    company = Company.query.get(id)
    company.status = "active"
    company.subscription_end = datetime.utcnow() + timedelta(days=30)
    db.session.commit()
    return redirect(url_for('super_admin.dashboard'))


@super_admin_bp.route('/cancel/<int:id>')
@super_admin_required
def cancel(id):
    company = Company.query.get(id)
    company.status = "cancelled"
    db.session.commit()
    return redirect(url_for('super_admin.dashboard'))


@super_admin_bp.route('/extend/<int:id>')
@super_admin_required
def extend(id):
    company = Company.query.get(id)
    if company.subscription_end:
        company.subscription_end += timedelta(days=30)
    else:
        company.subscription_end = datetime.utcnow() + timedelta(days=30)
    db.session.commit()
    return redirect(url_for('super_admin.dashboard'))