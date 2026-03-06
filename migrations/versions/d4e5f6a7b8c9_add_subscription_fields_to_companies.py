"""Add subscription fields to companies

Revision ID: d4e5f6a7b8c9
Revises: c9f8e7d6b5a4
Create Date: 2026-03-05 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = 'c9f8e7d6b5a4'
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    columns = {col['name'] for col in inspector.get_columns('companies')}

    with op.batch_alter_table('companies', schema=None) as batch_op:
        if 'plan' not in columns:
            batch_op.add_column(sa.Column('plan', sa.String(length=50), nullable=True, server_default='trial'))
        if 'status' not in columns:
            batch_op.add_column(sa.Column('status', sa.String(length=50), nullable=True, server_default='trial'))
        if 'subscription_end' not in columns:
            batch_op.add_column(sa.Column('subscription_end', sa.DateTime(), nullable=True))
        if 'stripe_customer_id' not in columns:
            batch_op.add_column(sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
        if 'stripe_subscription_id' not in columns:
            batch_op.add_column(sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True))


def downgrade():
    inspector = sa.inspect(op.get_bind())
    columns = {col['name'] for col in inspector.get_columns('companies')}

    with op.batch_alter_table('companies', schema=None) as batch_op:
        if 'stripe_subscription_id' in columns:
            batch_op.drop_column('stripe_subscription_id')
        if 'stripe_customer_id' in columns:
            batch_op.drop_column('stripe_customer_id')
        if 'subscription_end' in columns:
            batch_op.drop_column('subscription_end')
        if 'status' in columns:
            batch_op.drop_column('status')
        if 'plan' in columns:
            batch_op.drop_column('plan')