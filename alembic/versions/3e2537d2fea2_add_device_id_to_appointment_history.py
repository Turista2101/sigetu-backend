"""add_device_id_to_appointment_history

Revision ID: 3e2537d2fea2
Revises: 9340e874e2da
Create Date: 2026-03-18 11:54:14.408393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e2537d2fea2'
down_revision: Union[str, Sequence[str], None] = '9340e874e2da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('appointment_history', sa.Column('device_id', sa.String(length=36), nullable=True))
    op.create_index(op.f('ix_appointment_history_device_id'), 'appointment_history', ['device_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_appointment_history_device_id'), table_name='appointment_history')
    op.drop_column('appointment_history', 'device_id')
