"""agregar_attention_timestamps_a_historial

Revision ID: 0ef4a793bf9c
Revises: 883c19cacdb8
Create Date: 2026-03-06 13:39:27.696941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ef4a793bf9c'
down_revision: Union[str, Sequence[str], None] = '883c19cacdb8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('appointment_history', sa.Column('attention_started_at', sa.DateTime(), nullable=True))
    op.add_column('appointment_history', sa.Column('attention_ended_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('appointment_history', 'attention_ended_at')
    op.drop_column('appointment_history', 'attention_started_at')
