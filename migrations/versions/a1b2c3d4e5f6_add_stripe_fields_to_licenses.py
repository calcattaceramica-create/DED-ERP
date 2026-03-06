"""add stripe_customer_id and stripe_subscription_id to licenses

Revision ID: a1b2c3d4e5f6
Revises: 07bf4700b3a4
Create Date: 2026-03-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '07bf4700b3a4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('licenses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stripe_customer_id', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('stripe_subscription_id', sa.String(255), nullable=True))
        batch_op.create_index('ix_licenses_stripe_customer_id', ['stripe_customer_id'])
        batch_op.create_index('ix_licenses_stripe_subscription_id', ['stripe_subscription_id'])


def downgrade():
    with op.batch_alter_table('licenses', schema=None) as batch_op:
        batch_op.drop_index('ix_licenses_stripe_subscription_id')
        batch_op.drop_index('ix_licenses_stripe_customer_id')
        batch_op.drop_column('stripe_subscription_id')
        batch_op.drop_column('stripe_customer_id')

