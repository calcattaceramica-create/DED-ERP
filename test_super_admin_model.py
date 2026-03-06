import unittest

from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app import create_app, db
from app.models import SuperAdmin


class SuperAdminModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_super_admins_table_is_created_with_expected_columns(self):
        inspector = inspect(db.engine)
        self.assertIn('super_admins', inspector.get_table_names())

        columns = {col['name'] for col in inspector.get_columns('super_admins')}
        self.assertTrue({'id', 'email', 'password_hash', 'created_at'}.issubset(columns))

    def test_super_admin_email_is_unique(self):
        first = SuperAdmin(email='owner@example.com')
        first.set_password('Admin123!')
        db.session.add(first)
        db.session.commit()

        second = SuperAdmin(email='owner@example.com')
        second.set_password('Admin456!')
        db.session.add(second)

        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()


if __name__ == '__main__':
    unittest.main()