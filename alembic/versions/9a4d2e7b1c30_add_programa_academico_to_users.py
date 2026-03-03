"""add programa_academico to users

Revision ID: 9a4d2e7b1c30
Revises: 1f2c3d4e5f6a
Create Date: 2026-02-25 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9a4d2e7b1c30"
down_revision: Union[str, Sequence[str], None] = "1f2c3d4e5f6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("programa_academico", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "programa_academico")
