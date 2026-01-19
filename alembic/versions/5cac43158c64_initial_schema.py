"""initial schema

Revision ID: 5cac43158c64
Revises:
Create Date: 2026-01-19 23:27:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5cac43158c64'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create contacts table
    op.create_table('contacts',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('odoo_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('phone', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('street', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('city', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('country', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('is_deleted', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('contacts_pkey'))
    )
    op.create_index(op.f('ix_contacts_odoo_id'), 'contacts', ['odoo_id'], unique=True)

    # Create invoices table
    op.create_table('invoices',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('odoo_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('invoice_number', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('partner_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('partner_name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('invoice_date', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('due_date', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('amount_total', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    sa.Column('state', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('is_deleted', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('invoices_pkey'))
    )
    op.create_index(op.f('ix_invoices_odoo_id'), 'invoices', ['odoo_id'], unique=True)

    # Create users table
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('hashed_password', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('disabled', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='users_pkey')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    # Drop users table
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')

    # Drop invoices table
    op.drop_index(op.f('ix_invoices_odoo_id'), table_name='invoices')
    op.drop_table('invoices')

    # Drop contacts table
    op.drop_index(op.f('ix_contacts_odoo_id'), table_name='contacts')
    op.drop_table('contacts')
