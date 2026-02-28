from flask import render_template, redirect, url_for
from flask_login import current_user
from app.public import bp


@bp.route('/')
def landing():
    """Public landing page — shown at the root domain for unauthenticated visitors."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('public/landing.html')

