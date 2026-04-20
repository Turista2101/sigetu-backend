"""Drop legacy cargo column from staff

Revision ID: 20260420_drop_cargo_from_staff
Revises: 20260418_clean_schema
Create Date: 2026-04-20 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260420_drop_cargo_from_staff"
down_revision: Union[str, Sequence[str], None] = "20260418_clean_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Legacy databases may still have this column as NOT NULL.
    op.execute("ALTER TABLE staff DROP COLUMN IF EXISTS cargo")


def downgrade() -> None:
    op.add_column("staff", sa.Column("cargo", sa.String(length=120), nullable=True))
