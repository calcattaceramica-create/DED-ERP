from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from app.billing import bp
from app.models_license import License


@bp.route('/upgrade')
@login_required
def upgrade():
    """License upgrade / expired license page"""
    license = License.query.filter_by(tenant_id=current_user.tenant_id).first()
    return render_template('billing/upgrade.html', license=license)


@bp.route('/activate/<plan>')
@login_required
def activate_plan(plan):
    """Activate or extend a license plan — admin only"""
    # Only admins can activate plans
    if not current_user.is_admin and not current_user.is_super_admin:
        abort(403)

    if plan not in ('monthly', 'yearly'):
        flash('الخطة غير معروفة.', 'danger')
        return redirect(url_for('billing.upgrade'))

    # Fetch license via tenant_id (no direct company relationship on User)
    lic = License.query.filter_by(tenant_id=current_user.tenant_id).first()

    if not lic:
        flash('لا توجد رخصة مرتبطة بهذا الحساب. تواصل مع الدعم الفني.', 'danger')
        return redirect(url_for('billing.upgrade'))

    if plan == 'monthly':
        lic.plan = 'monthly'
        lic.end_date = datetime.utcnow() + timedelta(days=30)
    elif plan == 'yearly':
        lic.plan = 'yearly'
        lic.end_date = datetime.utcnow() + timedelta(days=365)

    lic.status = 'active'
    db.session.commit()

    flash('تم تفعيل الخطة بنجاح! 🎉', 'success')
    return redirect(url_for('main.index'))

