"""cascade delete appointments on user delete

Revision ID: c31b6e2f8a44
Revises: 9a4d2e7b1c30
Create Date: 2026-02-25 01:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c31b6e2f8a44"
down_revision: Union[str, Sequence[str], None] = "9a4d2e7b1c30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("appointments_student_id_fkey", "appointments", type_="foreignkey")
    op.create_foreign_key(
        "appointments_student_id_fkey",
        "appointments",
        "users",
        ["student_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("appointments_student_id_fkey", "appointments", type_="foreignkey")
    op.create_foreign_key(
        "appointments_student_id_fkey",
        "appointments",
        "users",
        ["student_id"],
        ["id"],
    )
