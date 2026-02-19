"""add account_type, opening_balance, notes to bank_accounts

Revision ID: add_fields_bank_acc
Revises: fe0d67f122a6
Create Date: 2026-02-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_fields_bank_acc'
down_revision = 'fe0d67f122a6'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to bank_accounts table
    with op.batch_alter_table('bank_accounts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_type', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('opening_balance', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))
    
    # Set default values for existing records
    op.execute("UPDATE bank_accounts SET account_type = 'current' WHERE account_type IS NULL")
    op.execute("UPDATE bank_accounts SET opening_balance = current_balance WHERE opening_balance IS NULL")


def downgrade():
    # Remove columns from bank_accounts table
    with op.batch_alter_table('bank_accounts', schema=None) as batch_op:
        batch_op.drop_column('notes')
        batch_op.drop_column('opening_balance')
        batch_op.drop_column('account_type')

