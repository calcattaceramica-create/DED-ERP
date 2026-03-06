import unittest
import warnings
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import stripe
from sqlalchemy.exc import SAWarning

from app import create_app, db
from app.auth.routes import _generate_company_code
from app.models import Company, User
from app.models_license import License
from app.models_tenant import Tenant
from app.utils.datetime_helper import utcnow


class AuthAndBillingFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.config.update(
            BASE_DOMAIN='calcatta-ceramica.sbs',
            STRIPE_WEBHOOK_SECRET='whsec_test',
        )
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        with warnings.catch_warnings():
            warnings.filterwarnings(
                'ignore',
                message="Can't sort tables for DROP; an unresolvable foreign key dependency exists.*",
                category=SAWarning,
            )
            db.drop_all()
        self.ctx.pop()

    def _create_tenant_user_and_license(self, subdomain='alpha'):
        tenant = Tenant(
            code=f'COMP{subdomain.upper()[:3]}',
            subdomain=subdomain,
            name=f'{subdomain} company',
            email=f'{subdomain}@example.com',
            is_active=True,
            is_trial=True,
            trial_ends_at=utcnow() + timedelta(days=30),
            currency='SAR',
            tax_rate=15.0,
            language='ar',
        )
        db.session.add(tenant)
        db.session.flush()

        company = Company(
            tenant_id=tenant.id,
            name=f'{subdomain} company',
            email=f'{subdomain}@example.com',
            currency='SAR',
            tax_rate=15.0,
        )
        db.session.add(company)
        db.session.flush()

        user = User(
            tenant_id=tenant.id,
            username='admin',
            email=f'admin-{subdomain}@example.com',
            is_active=True,
            is_admin=True,
            language='ar',
        )
        user.set_password('Admin123!')
        db.session.add(user)
        db.session.flush()

        tenant.admin_user_id = user.id
        license_record = License(
            tenant_id=tenant.id,
            company_id=company.id,
            plan='trial',
            status='active',
            start_date=utcnow(),
            end_date=utcnow() + timedelta(days=14),
        )
        db.session.add(license_record)
        db.session.commit()
        return tenant, user, license_record

    def test_register_prefers_english_name_for_subdomain(self):
        response = self.client.post(
            '/auth/register?plan=monthly',
            data={
                'company_name': 'شركة ألفا',
                'company_name_en': 'Alpha One!',
                'company_email': 'alpha@example.com',
                'company_phone': '123456789',
                'admin_username': 'alpha_admin',
                'admin_email': 'admin@alpha.example.com',
                'admin_password': 'Admin123!',
                'admin_full_name': 'Alpha Admin',
                'plan': 'monthly',
            },
            headers={'Host': 'calcatta-ceramica.sbs'},
            follow_redirects=False,
        )

        tenant = Tenant.query.filter_by(email='alpha@example.com').first()
        self.assertIsNotNone(tenant)
        self.assertEqual(tenant.subdomain, 'alphaone')
        self.assertTrue(
            response.headers['Location'].endswith(
                'alphaone.calcatta-ceramica.sbs/auth/login?next=/payment/checkout/monthly'
            )
        )

    def test_register_generates_next_company_code_even_if_latest_tenant_is_not_comp(self):
        db.session.add_all([
            Tenant(
                code='COMP001',
                subdomain='alpha',
                name='Alpha',
                email='alpha@example.com',
                is_active=True,
                is_trial=True,
                trial_ends_at=utcnow() + timedelta(days=30),
                currency='SAR',
                tax_rate=15.0,
                language='ar',
            ),
            Tenant(
                code='DEFAULT',
                subdomain='default',
                name='Default Tenant',
                email='default@example.com',
                is_active=True,
                is_trial=True,
                trial_ends_at=utcnow() + timedelta(days=30),
                currency='SAR',
                tax_rate=15.0,
                language='ar',
            ),
        ])
        db.session.commit()

        response = self.client.post(
            '/auth/register',
            data={
                'company_name': 'شركة بيتا',
                'company_name_en': 'Beta',
                'company_email': 'beta@example.com',
                'company_phone': '123456789',
                'admin_username': 'beta_admin',
                'admin_email': 'admin@beta.example.com',
                'admin_password': 'Admin123!',
                'admin_full_name': 'Beta Admin',
            },
            headers={'Host': 'calcatta-ceramica.sbs'},
            follow_redirects=False,
        )

        tenant = Tenant.query.filter_by(email='beta@example.com').first()
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(tenant)
        self.assertEqual(tenant.code, 'COMP002')

    def test_generate_company_code_ignores_non_comp_and_malformed_codes(self):
        db.session.add_all([
            Tenant(
                code='COMP001',
                subdomain='alpha',
                name='Alpha',
                email='alpha@example.com',
                is_active=True,
                is_trial=True,
                trial_ends_at=utcnow() + timedelta(days=30),
                currency='SAR',
                tax_rate=15.0,
                language='ar',
            ),
            Tenant(
                code='COMP026',
                subdomain='omega',
                name='Omega',
                email='omega@example.com',
                is_active=True,
                is_trial=True,
                trial_ends_at=utcnow() + timedelta(days=30),
                currency='SAR',
                tax_rate=15.0,
                language='ar',
            ),
            Tenant(
                code='DEFAULT',
                subdomain='default',
                name='Default Tenant',
                email='default@example.com',
                is_active=True,
                is_trial=True,
                trial_ends_at=utcnow() + timedelta(days=30),
                currency='SAR',
                tax_rate=15.0,
                language='ar',
            ),
            Tenant(
                code='COMPABC',
                subdomain='legacy',
                name='Legacy Tenant',
                email='legacy@example.com',
                is_active=True,
                is_trial=True,
                trial_ends_at=utcnow() + timedelta(days=30),
                currency='SAR',
                tax_rate=15.0,
                language='ar',
            ),
        ])
        db.session.commit()

        self.assertEqual(_generate_company_code(), 'COMP027')

    def test_login_does_not_fail_when_session_log_insert_fails(self):
        tenant, _, _ = self._create_tenant_user_and_license('safe')
        original_commit = db.session.commit
        commit_calls = {'count': 0}

        def flaky_commit():
            commit_calls['count'] += 1
            if commit_calls['count'] == 1:
                raise RuntimeError('session_logs table unavailable')
            return original_commit()

        with patch.object(db.session, 'commit', side_effect=flaky_commit):
            response = self.client.post(
                '/auth/login',
                data={'username': 'admin', 'password': 'Admin123!'},
                headers={'Host': f'{tenant.subdomain}.calcatta-ceramica.sbs'},
                follow_redirects=False,
            )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/dashboard'))

    def test_billing_dashboard_links_to_monthly_and_yearly_checkout(self):
        tenant, _, _ = self._create_tenant_user_and_license('billing')
        self.client.post(
            '/auth/login',
            data={'username': 'admin', 'password': 'Admin123!'},
            headers={'Host': f'{tenant.subdomain}.calcatta-ceramica.sbs'},
            follow_redirects=False,
        )

        response = self.client.get(
            '/billing/dashboard',
            headers={'Host': f'{tenant.subdomain}.calcatta-ceramica.sbs'},
        )
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('/payment/checkout/monthly', html)
        self.assertIn('/payment/checkout/yearly', html)
        self.assertNotIn('/payment/checkout/basic', html)

    @patch('app.payment.routes.stripe.checkout.Session.retrieve')
    def test_payment_success_updates_license_dates_without_webhook(self, mock_retrieve):
        tenant, _, license_record = self._create_tenant_user_and_license('paid')
        self.client.post(
            '/auth/login',
            data={'username': 'admin', 'password': 'Admin123!'},
            headers={'Host': f'{tenant.subdomain}.calcatta-ceramica.sbs'},
            follow_redirects=False,
        )

        license_record.status = 'expired'
        license_record.end_date = utcnow() - timedelta(days=1)
        db.session.commit()

        mock_retrieve.return_value = {
            'customer': 'cus_test_123',
            'subscription': 'sub_test_123',
            'metadata': {'plan': 'yearly'},
        }

        response = self.client.get(
            '/payment/success?session_id=cs_test_123',
            headers={'Host': f'{tenant.subdomain}.calcatta-ceramica.sbs'},
            follow_redirects=False,
        )

        db.session.refresh(license_record)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(license_record.status, 'active')
        self.assertEqual(license_record.plan, 'yearly')
        self.assertEqual(license_record.stripe_customer_id, 'cus_test_123')
        self.assertEqual(license_record.stripe_subscription_id, 'sub_test_123')
        self.assertIsNotNone(license_record.start_date)
        self.assertGreater(license_record.end_date, utcnow() + timedelta(days=360))

    @patch('app.payment.routes.stripe.Webhook.construct_event')
    def test_webhook_checkout_session_completed_activates_license(self, mock_construct_event):
        tenant, _, license_record = self._create_tenant_user_and_license('hookstart')
        license_record.status = 'expired'
        license_record.end_date = utcnow() - timedelta(days=2)
        db.session.commit()

        mock_construct_event.return_value = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'customer': 'cus_webhook_123',
                    'subscription': 'sub_webhook_123',
                    'metadata': {
                        'tenant_id': str(tenant.id),
                        'plan': 'monthly',
                    },
                }
            },
        }

        response = self.client.post(
            '/payment/stripe-webhook',
            data=b'{}',
            headers={'Stripe-Signature': 'sig_test'},
        )

        db.session.refresh(license_record)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(license_record.status, 'active')
        self.assertEqual(license_record.plan, 'monthly')
        self.assertEqual(license_record.stripe_customer_id, 'cus_webhook_123')
        self.assertEqual(license_record.stripe_subscription_id, 'sub_webhook_123')
        self.assertGreater(license_record.end_date, utcnow() + timedelta(days=30))

    @patch('app.payment.routes.stripe.Webhook.construct_event')
    def test_webhook_invoice_payment_failed_suspends_license(self, mock_construct_event):
        _, _, license_record = self._create_tenant_user_and_license('hookfail')
        license_record.status = 'active'
        license_record.stripe_customer_id = 'cus_fail_123'
        license_record.stripe_subscription_id = 'sub_fail_123'
        db.session.commit()

        mock_construct_event.return_value = {
            'type': 'invoice.payment_failed',
            'data': {
                'object': {
                    'customer': 'cus_fail_123',
                    'subscription': 'sub_fail_123',
                    'attempt_count': 2,
                }
            },
        }

        response = self.client.post(
            '/payment/stripe-webhook',
            data=b'{}',
            headers={'Stripe-Signature': 'sig_test'},
        )

        db.session.refresh(license_record)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(license_record.status, 'suspended')

    @patch('app.payment.routes.stripe.Webhook.construct_event')
    def test_webhook_invoice_payment_succeeded_renews_license(self, mock_construct_event):
        _, _, license_record = self._create_tenant_user_and_license('hooksuccess')
        target_period_end = int((datetime.now(UTC) + timedelta(days=45)).timestamp())
        license_record.status = 'suspended'
        license_record.plan = 'yearly'
        license_record.stripe_customer_id = 'cus_success_123'
        license_record.stripe_subscription_id = 'sub_success_123'
        license_record.end_date = utcnow() - timedelta(days=1)
        db.session.commit()

        mock_construct_event.return_value = {
            'type': 'invoice.payment_succeeded',
            'data': {
                'object': {
                    'customer': 'cus_success_123',
                    'subscription': 'sub_success_123',
                    'lines': {
                        'data': [
                            {
                                'period': {
                                    'end': target_period_end,
                                }
                            }
                        ]
                    },
                }
            },
        }

        response = self.client.post(
            '/payment/stripe-webhook',
            data=b'{}',
            headers={'Stripe-Signature': 'sig_test'},
        )

        db.session.refresh(license_record)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(license_record.status, 'active')
        self.assertGreater(license_record.end_date, utcnow() + timedelta(days=44))

    @patch('app.payment.routes.stripe.Webhook.construct_event')
    def test_webhook_subscription_deleted_expires_license_by_subscription_id(self, mock_construct_event):
        _, _, license_record = self._create_tenant_user_and_license('hookcancel')
        license_record.status = 'active'
        license_record.stripe_customer_id = 'cus_cancel_123'
        license_record.stripe_subscription_id = 'sub_cancel_123'
        db.session.commit()

        mock_construct_event.return_value = {
            'type': 'customer.subscription.deleted',
            'data': {
                'object': {
                    'id': 'sub_cancel_123',
                }
            },
        }

        response = self.client.post(
            '/payment/stripe-webhook',
            data=b'{}',
            headers={'Stripe-Signature': 'sig_test'},
        )

        db.session.refresh(license_record)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(license_record.status, 'expired')

    @patch('app.payment.routes.stripe.Webhook.construct_event')
    def test_webhook_invalid_signature_returns_400(self, mock_construct_event):
        mock_construct_event.side_effect = stripe.error.SignatureVerificationError(
            'bad signature',
            'sig_test',
        )

        response = self.client.post(
            '/payment/stripe-webhook',
            data=b'{}',
            headers={'Stripe-Signature': 'sig_test'},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid signature', response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()