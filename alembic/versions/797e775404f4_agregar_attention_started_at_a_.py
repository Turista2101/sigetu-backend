"""agregar_attention_started_at_a_appointments

Revision ID: 797e775404f4
Revises: fa07559ca85f
Create Date: 2026-03-06 12:04:26.584871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '797e775404f4'
down_revision: Union[str, Sequence[str], None] = 'fa07559ca85f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('appointments', sa.Column('attention_started_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('appointments', 'attention_started_at')
