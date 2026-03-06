import unittest

from sqlalchemy import inspect

from app import create_app, db


class CompanySubscriptionFieldsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_companies_table_has_subscription_columns(self):
        inspector = inspect(db.engine)
        columns = {col['name'] for col in inspector.get_columns('companies')}
        expected = {
            'plan',
            'status',
            'subscription_end',
            'stripe_customer_id',
            'stripe_subscription_id',
        }
        self.assertTrue(expected.issubset(columns))


if __name__ == '__main__':
    unittest.main()