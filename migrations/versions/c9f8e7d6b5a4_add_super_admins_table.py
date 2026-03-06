"""Add super_admins table

Revision ID: c9f8e7d6b5a4
Revises: a1b2c3d4e5f6, add_fields_bank_acc
Create Date: 2026-03-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9f8e7d6b5a4'
down_revision = ('a1b2c3d4e5f6', 'add_fields_bank_acc')
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    if 'super_admins' in inspector.get_table_names():
        return

    op.create_table(
        'super_admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )


def downgrade():
    inspector = sa.inspect(op.get_bind())
    if 'super_admins' in inspector.get_table_names():
        op.drop_table('super_admins')