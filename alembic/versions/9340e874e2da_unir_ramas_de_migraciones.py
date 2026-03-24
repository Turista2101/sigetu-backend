"""Unir ramas de migraciones

Revision ID: 9340e874e2da
Revises: permitir_user_id_nulo_fcm, babc25964f91
Create Date: 2026-03-17 00:39:14.688780

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9340e874e2da'
down_revision: Union[str, Sequence[str], None] = ('permitir_user_id_nulo_fcm', 'babc25964f91')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
