"""agregar_unicidad_scheduled_at_citas

Revision ID: 5fedfbdef732
Revises: d4b7e1a9c2f6
Create Date: 2026-03-06 09:36:57.949643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5fedfbdef732'
down_revision: Union[str, Sequence[str], None] = 'd4b7e1a9c2f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('appointment_history_appointment_id_key', 'appointment_history', type_='unique')
    op.drop_index('ix_appointment_history_appointment_id', table_name='appointment_history')
    op.create_index('ix_appointment_history_appointment_id', 'appointment_history', ['appointment_id'], unique=True)
    op.create_unique_constraint('uq_appointments_scheduled_at', 'appointments', ['scheduled_at'])
    op.drop_constraint('uq_revoked_tokens_jti', 'revoked_tokens', type_='unique')
    op.drop_index('ix_revoked_tokens_jti', table_name='revoked_tokens')
    op.create_index('ix_revoked_tokens_jti', 'revoked_tokens', ['jti'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_revoked_tokens_jti', table_name='revoked_tokens')
    op.create_index('ix_revoked_tokens_jti', 'revoked_tokens', ['jti'], unique=False)
    op.create_unique_constraint('uq_revoked_tokens_jti', 'revoked_tokens', ['jti'])
    op.drop_constraint('uq_appointments_scheduled_at', 'appointments', type_='unique')
    op.drop_index('ix_appointment_history_appointment_id', table_name='appointment_history')
    op.create_index('ix_appointment_history_appointment_id', 'appointment_history', ['appointment_id'], unique=False)
    op.create_unique_constraint('appointment_history_appointment_id_key', 'appointment_history', ['appointment_id'])
