"""Permitir user_id nulo en tokens FCM para invitados

Revision ID: permitir_user_id_nulo_fcm
Revises: babc25964f91
Create Date: 2026-03-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'permitir_user_id_nulo_fcm'
down_revision: Union[str, Sequence[str], None] = 'e6b1a2c3d4f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.alter_column('fcm_device_tokens', 'user_id', existing_type=sa.Integer(), nullable=True)

def downgrade():
    op.alter_column('fcm_device_tokens', 'user_id', existing_type=sa.Integer(), nullable=False)
