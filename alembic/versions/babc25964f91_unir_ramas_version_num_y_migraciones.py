"""Unir ramas version_num y migraciones

Revision ID: babc25964f91
Revises: 0d5042d44ee2, ampliar_version_num_a_128
Create Date: 2026-03-15 21:06:02.578123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'babc25964f91'
down_revision: Union[str, Sequence[str], None] = ('0d5042d44ee2', 'ampliar_version_num_a_128')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
