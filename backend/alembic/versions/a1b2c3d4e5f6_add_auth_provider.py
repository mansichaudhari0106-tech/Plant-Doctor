"""add auth_provider to users

Revision ID: a1b2c3d4e5f6
Revises: bd2603273147
Create Date: 2026-06-29 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'bd2603273147'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('auth_provider', sa.String(), nullable=True))
    # Set default value for existing rows
    op.execute("UPDATE users SET auth_provider = 'email' WHERE auth_provider IS NULL")


def downgrade() -> None:
    op.drop_column('users', 'auth_provider')
