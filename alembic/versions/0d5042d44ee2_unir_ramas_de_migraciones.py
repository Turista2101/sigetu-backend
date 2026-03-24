"""Unir ramas de migraciones

Revision ID: 0d5042d44ee2
Revises: 20260315_permitir_student_id_nulo, e6b1a2c3d4f5
Create Date: 2026-03-15 20:56:39.010400

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d5042d44ee2'
down_revision: Union[str, Sequence[str], None] = ('20260315_permitir_student_id_nulo', 'e6b1a2c3d4f5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
