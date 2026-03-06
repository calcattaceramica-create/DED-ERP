import stripe
from flask import render_template, redirect, url_for, flash, abort, current_app
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


# ─────────────────────────────────────────────────────────────────────────────
# Billing Dashboard
# ─────────────────────────────────────────────────────────────────────────────

@bp.route('/dashboard')
@login_required
def billing_dashboard():
    """Professional billing dashboard — plan info, renewal, invoices."""
    lic = License.query.filter_by(tenant_id=current_user.tenant_id).first()

    stripe_sub    = None
    invoices_data = []

    if lic:
        # ── Fetch Stripe subscription details ─────────────────────────────
        if lic.stripe_subscription_id:
            try:
                stripe_sub = stripe.Subscription.retrieve(
                    lic.stripe_subscription_id,
                    expand=['default_payment_method']
                )
            except stripe.StripeError as e:
                current_app.logger.warning(f'Billing dashboard: Stripe sub error — {e}')

        # ── Fetch last 12 invoices from Stripe ────────────────────────────
        if lic.stripe_customer_id:
            try:
                result = stripe.Invoice.list(
                    customer=lic.stripe_customer_id,
                    limit=12
                )
                invoices_data = result.get('data', [])
            except stripe.StripeError as e:
                current_app.logger.warning(f'Billing dashboard: Stripe invoices error — {e}')

    return render_template(
        'billing/dashboard.html',
        lic=lic,
        stripe_sub=stripe_sub,
        invoices=invoices_data,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Upgrade / Downgrade Plan
# ─────────────────────────────────────────────────────────────────────────────

@bp.route('/change-plan/<new_plan>', methods=['POST'])
@login_required
def change_plan(new_plan):
    """
    Modify an existing Stripe subscription to a different plan (immediate effect).
    Uses proration so the customer is charged/credited fairly.

    Requires an active stripe_subscription_id on the license.
    If no subscription exists yet → redirect to /payment/checkout/<new_plan>.
    """
    if not current_user.is_admin and not getattr(current_user, 'is_super_admin', False):
        abort(403)

    # ── Validate plan name ────────────────────────────────────────────────────
    price_ids = current_app.config.get('STRIPE_PLAN_PRICE_IDS', {})
    if new_plan not in price_ids:
        flash('الخطة المطلوبة غير موجودة.', 'danger')
        return redirect(url_for('billing.billing_dashboard'))

    new_price_id = price_ids[new_plan]
    if not new_price_id or not new_price_id.startswith('price_'):
        flash('لم يتم تهيئة أسعار Stripe بعد. تواصل مع الدعم الفني.', 'warning')
        return redirect(url_for('billing.billing_dashboard'))

    # ── Fetch license ─────────────────────────────────────────────────────────
    lic = License.query.filter_by(tenant_id=current_user.tenant_id).first()

    if not lic:
        flash('لا توجد رخصة مرتبطة بهذا الحساب.', 'danger')
        return redirect(url_for('billing.upgrade'))

    # ── Guard: same plan ──────────────────────────────────────────────────────
    if lic.plan == new_plan:
        flash('أنت مشترك بهذه الخطة بالفعل.', 'info')
        return redirect(url_for('billing.billing_dashboard'))

    # ── No existing Stripe subscription → send to checkout ───────────────────
    if not lic.stripe_subscription_id:
        return redirect(url_for('payment.checkout', plan=new_plan))

    # ── Modify existing Stripe subscription ───────────────────────────────────
    try:
        # Retrieve the current subscription to get the subscription item ID
        current_sub = stripe.Subscription.retrieve(lic.stripe_subscription_id)
        item_id = current_sub['items']['data'][0].id

        stripe.Subscription.modify(
            lic.stripe_subscription_id,
            items=[{
                'id': item_id,
                'price': new_price_id,
            }],
            proration_behavior='create_prorations',   # fair billing credit/charge
        )

    except stripe.StripeError as e:
        current_app.logger.error(
            f'change_plan error — tenant={lic.tenant_id} '
            f'plan={new_plan} error={e}'
        )
        flash('حدث خطأ أثناء تغيير الخطة. حاول مرة أخرى أو تواصل مع الدعم.', 'danger')
        return redirect(url_for('billing.billing_dashboard'))

    # ── Update local license record ───────────────────────────────────────────
    old_plan = lic.plan
    lic.plan = new_plan
    db.session.commit()

    current_app.logger.info(
        f'Plan changed — tenant={lic.tenant_id} '
        f'{old_plan} → {new_plan}'
    )
    flash(f'تم تغيير الخطة بنجاح إلى {new_plan}! 🎉', 'success')
    return redirect(url_for('billing.billing_dashboard'))


# ─────────────────────────────────────────────────────────────────────────────
# Cancel Subscription
# ─────────────────────────────────────────────────────────────────────────────

@bp.route('/cancel-subscription', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel the Stripe subscription at period end — admin only."""
    if not current_user.is_admin and not getattr(current_user, 'is_super_admin', False):
        abort(403)

    lic = License.query.filter_by(tenant_id=current_user.tenant_id).first()

    if not lic or not lic.stripe_subscription_id:
        flash('لا يوجد اشتراك نشط للإلغاء.', 'warning')
        return redirect(url_for('billing.billing_dashboard'))

    try:
        # cancel_at_period_end=True: keeps access until the end of the paid period
        stripe.Subscription.modify(
            lic.stripe_subscription_id,
            cancel_at_period_end=True
        )
        flash('تم جدولة إلغاء الاشتراك. ستحتفظ بالوصول حتى نهاية الفترة الحالية.', 'info')
        current_app.logger.info(
            f'Subscription cancellation scheduled — '
            f'tenant={lic.tenant_id} sub={lic.stripe_subscription_id}'
        )
    except stripe.StripeError as e:
        current_app.logger.error(f'Cancel subscription error: {e}')
        flash('حدث خطأ أثناء إلغاء الاشتراك. حاول مرة أخرى أو تواصل مع الدعم.', 'danger')

    return redirect(url_for('billing.billing_dashboard'))

