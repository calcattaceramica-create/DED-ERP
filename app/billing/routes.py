from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.billing import bp
from app.models_license import License


@bp.route('/upgrade')
@login_required
def upgrade():
    """License upgrade / expired license page"""
    license = License.query.filter_by(tenant_id=current_user.tenant_id).first()
    return render_template('billing/upgrade.html', license=license)

