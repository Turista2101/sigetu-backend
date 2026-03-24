"""fix_fcm_device_tokens_user_id_nullable

Revision ID: 500661c9de15
Revises: 3e2537d2fea2
Create Date: 2026-03-18 12:24:51.513993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '500661c9de15'
down_revision: Union[str, Sequence[str], None] = '3e2537d2fea2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('fcm_device_tokens', 'user_id', existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('fcm_device_tokens', 'user_id', existing_type=sa.Integer(), nullable=False)
