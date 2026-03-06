import stripe
from flask import redirect, url_for, flash, current_app, request, jsonify
from flask_login import login_required, current_user
from datetime import timedelta

from app import db
from app.payment import bp
from app.models_license import License
from app.utils.datetime_helper import utcfromtimestamp, utcnow


StripeSignatureVerificationError = (
    getattr(getattr(stripe, 'error', None), 'SignatureVerificationError', None)
    or getattr(getattr(stripe, 'errors', None), 'SignatureVerificationError', ValueError)
)


def _get_local_license_end_date(plan):
    """Fallback local expiry window used until Stripe webhooks confirm the cycle."""
    if plan == 'yearly':
        return utcnow() + timedelta(days=366)
    return utcnow() + timedelta(days=32)


@bp.route('/checkout/<plan>')
@login_required
def checkout(plan):
    """Create a Stripe Checkout session and redirect the user to it."""

    # Validate plan name against configured price IDs
    price_ids = current_app.config.get('STRIPE_PLAN_PRICE_IDS', {})
    if plan not in price_ids:
        flash('الخطة المطلوبة غير موجودة.', 'danger')
        return redirect(url_for('billing.upgrade'))

    price_id = price_ids[plan]

    # Guard: price ID must be a real Stripe ID (not empty placeholder)
    if not price_id or not price_id.startswith('price_'):
        flash('لم يتم تهيئة أسعار Stripe بعد. تواصل مع الدعم الفني.', 'warning')
        return redirect(url_for('billing.upgrade'))

    # Retrieve (or create) the Stripe customer linked to this tenant's license
    lic = License.query.filter_by(tenant_id=current_user.tenant_id).first()
    customer_id = lic.stripe_customer_id if lic else None

    try:
        session_params = {
            'payment_method_types': ['card'],
            'line_items': [{
                'price': price_id,
                'quantity': 1,
            }],
            'mode': 'subscription',
            'success_url': url_for('payment.success', _external=True)
                           + '?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': url_for('payment.cancel', _external=True),
            'metadata': {
                'tenant_id': str(current_user.tenant_id),
                'plan': plan,
            },
        }

        # Pre-fill customer if we already have one in Stripe
        if customer_id:
            session_params['customer'] = customer_id

        checkout_session = stripe.checkout.Session.create(**session_params)

    except stripe.StripeError as e:
        current_app.logger.error(f'Stripe error during checkout: {e}')
        flash('حدث خطأ أثناء الاتصال بـ Stripe. حاول مرة أخرى.', 'danger')
        return redirect(url_for('billing.upgrade'))

    return redirect(checkout_session.url, code=303)


@bp.route('/success')
@login_required
def success():
    """Landing page after successful Stripe payment."""
    session_id = request.args.get('session_id')

    if session_id:
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            customer_id = checkout_session.get('customer')
            subscription_id = checkout_session.get('subscription')
            plan = checkout_session.get('metadata', {}).get('plan')

            # Persist Stripe IDs on the license record
            lic = License.query.filter_by(tenant_id=current_user.tenant_id).first()
            if lic:
                if customer_id:
                    lic.stripe_customer_id = customer_id
                if subscription_id:
                    lic.stripe_subscription_id = subscription_id
                if plan:
                    lic.plan = plan
                lic.status = 'active'
                lic.start_date = utcnow()
                lic.end_date = _get_local_license_end_date(plan or lic.plan)
                db.session.commit()

        except stripe.StripeError as e:
            current_app.logger.error(f'Stripe session retrieval error: {e}')

    flash('تم الدفع بنجاح! تم تفعيل اشتراكك. 🎉', 'success')
    return redirect(url_for('main.index'))


@bp.route('/cancel')
@login_required
def cancel():
    """Landing page when the user cancels the Stripe checkout."""
    flash('تم إلغاء عملية الدفع.', 'info')
    return redirect(url_for('billing.upgrade'))


# ─────────────────────────────────────────────────────────────────────────────
# Stripe Webhook
# ─────────────────────────────────────────────────────────────────────────────

def _handle_successful_payment(session):
    """
    Called when checkout.session.completed fires.
    Activates (or renews) the tenant license and saves Stripe IDs.
    """
    tenant_id     = session.get('metadata', {}).get('tenant_id')
    plan          = session.get('metadata', {}).get('plan') or 'monthly'
    customer_id   = session.get('customer')
    subscription_id = session.get('subscription')

    if not tenant_id:
        current_app.logger.warning('Webhook: checkout.session.completed missing tenant_id in metadata')
        return

    lic = License.query.filter_by(tenant_id=int(tenant_id)).first()
    if not lic:
        # Create a new license record if none exists yet
        lic = License(tenant_id=int(tenant_id))
        db.session.add(lic)

    lic.plan               = plan
    lic.status             = 'active'
    lic.stripe_customer_id    = customer_id
    lic.stripe_subscription_id = subscription_id
    lic.start_date         = utcnow()

    # Set end_date based on plan (Stripe handles actual billing cycle;
    # this is a local safety expiry in case webhooks are missed)
    lic.end_date = _get_local_license_end_date(plan)

    db.session.commit()
    current_app.logger.info(
        f'Webhook: License activated — tenant={tenant_id} plan={plan} '
        f'customer={customer_id} subscription={subscription_id}'
    )


def _handle_failed_payment(event):
    """
    Called when invoice.payment_failed fires.
    Looks up the license by stripe_subscription_id (primary) with a
    fallback to stripe_customer_id, then suspends it so the tenant
    sees the upgrade page on their next request.
    """
    invoice             = event['data']['object']
    subscription_id     = invoice.get('subscription')
    customer_id         = invoice.get('customer')
    attempt_count       = invoice.get('attempt_count', '?')

    # ── 1. Find license by subscription_id (most precise) ────────────────────
    lic = None
    if subscription_id:
        lic = License.query.filter_by(stripe_subscription_id=subscription_id).first()

    # ── 2. Fallback: find by customer_id ─────────────────────────────────────
    if not lic and customer_id:
        lic = License.query.filter_by(stripe_customer_id=customer_id).first()

    if not lic:
        current_app.logger.warning(
            f'Webhook: invoice.payment_failed — no license found for '
            f'subscription={subscription_id} customer={customer_id}'
        )
        return

    lic.status = 'suspended'
    db.session.commit()
    current_app.logger.warning(
        f'Webhook: Payment failed (attempt #{attempt_count}) — '
        f'subscription={subscription_id} customer={customer_id} '
        f'tenant={lic.tenant_id}. License suspended.'
    )


def _handle_payment_succeeded(event):
    """
    Called when invoice.payment_succeeded fires (recurring renewal).
    Extends the license end_date so the tenant keeps access for another cycle.
    """
    invoice         = event['data']['object']
    subscription_id = invoice.get('subscription')
    customer_id     = invoice.get('customer')
    period_end      = invoice.get('lines', {}).get('data', [{}])[0] \
                             .get('period', {}).get('end')   # Unix timestamp

    # Find license — prefer subscription_id for precision
    lic = None
    if subscription_id:
        lic = License.query.filter_by(stripe_subscription_id=subscription_id).first()
    if not lic and customer_id:
        lic = License.query.filter_by(stripe_customer_id=customer_id).first()

    if not lic:
        current_app.logger.warning(
            f'Webhook: invoice.payment_succeeded — no license found for '
            f'subscription={subscription_id} customer={customer_id}'
        )
        return

    # Use Stripe's period_end as the new end_date (+ 1 day buffer)
    if period_end:
        new_end = utcfromtimestamp(period_end) + timedelta(days=1)
    else:
        # Fallback: extend locally based on the current plan
        new_end = _get_local_license_end_date(lic.plan)

    lic.status   = 'active'
    lic.end_date = new_end
    db.session.commit()
    current_app.logger.info(
        f'Webhook: Payment succeeded — subscription={subscription_id} '
        f'tenant={lic.tenant_id}. License renewed until {new_end.date()}.'
    )


def _handle_subscription_deleted(event):
    """
    Called when customer.subscription.deleted fires.
    Marks the license as expired.
    """
    subscription = event['data']['object']
    subscription_id = subscription.get('id')
    customer_id  = subscription.get('customer')

    lic = None
    if subscription_id:
        lic = License.query.filter_by(stripe_subscription_id=subscription_id).first()
    if not lic and customer_id:
        lic = License.query.filter_by(stripe_customer_id=customer_id).first()

    if lic:
        lic.status = 'expired'
        db.session.commit()
        current_app.logger.info(
            f'Webhook: Subscription cancelled — '
            f'subscription={subscription_id} customer={customer_id} tenant={lic.tenant_id}.'
        )


@bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """
    Stripe webhook endpoint — called directly by Stripe (no login, no CSRF).
    Authentication is done via the Stripe-Signature header.
    """
    payload    = request.data          # raw bytes — MUST NOT use request.get_json()
    sig_header = request.headers.get('Stripe-Signature')
    secret     = current_app.config.get('STRIPE_WEBHOOK_SECRET')

    if not secret:
        current_app.logger.error('Webhook: STRIPE_WEBHOOK_SECRET is not configured.')
        return jsonify({'error': 'Webhook secret not configured'}), 500

    # ── Verify Stripe signature ───────────────────────────────────────────────
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret)
    except StripeSignatureVerificationError as e:
        current_app.logger.warning(f'Webhook: Invalid signature — {e}')
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        current_app.logger.error(f'Webhook: Malformed payload — {e}')
        return jsonify({'error': 'Bad payload'}), 400

    # ── Route event types ─────────────────────────────────────────────────────
    event_type = event.get('type')
    current_app.logger.info(f'Webhook: Received event type={event_type}')

    try:
        if event_type == 'checkout.session.completed':
            _handle_successful_payment(event['data']['object'])

        elif event_type == 'invoice.payment_succeeded':
            _handle_payment_succeeded(event)

        elif event_type == 'invoice.payment_failed':
            _handle_failed_payment(event)

        elif event_type == 'customer.subscription.deleted':
            _handle_subscription_deleted(event)

    except Exception as e:
        current_app.logger.error(f'Webhook: Handler error for {event_type} — {e}')
        return jsonify({'error': 'Handler error'}), 500

    # Always return 200 so Stripe does not keep retrying
    return jsonify({'status': 'ok'}), 200

