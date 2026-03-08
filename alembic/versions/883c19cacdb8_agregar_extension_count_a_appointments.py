"""agregar_extension_count_a_appointments

Revision ID: 883c19cacdb8
Revises: 797e775404f4
Create Date: 2026-03-06 12:48:29.743755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '883c19cacdb8'
down_revision: Union[str, Sequence[str], None] = '797e775404f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('appointments', sa.Column('extension_count', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('appointments', 'extension_count')
