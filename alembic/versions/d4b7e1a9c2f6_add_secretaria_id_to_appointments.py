"""add secretaria_id to appointments

Revision ID: d4b7e1a9c2f6
Revises: c8a1e3f4b7d2
Create Date: 2026-03-02 18:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4b7e1a9c2f6"
down_revision: Union[str, Sequence[str], None] = "c8a1e3f4b7d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("appointments", sa.Column("secretaria_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_appointments_secretaria_id"), "appointments", ["secretaria_id"], unique=False)
    op.create_foreign_key(
        "fk_appointments_secretaria_id_users",
        "appointments",
        "users",
        ["secretaria_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_appointments_secretaria_id_users", "appointments", type_="foreignkey")
    op.drop_index(op.f("ix_appointments_secretaria_id"), table_name="appointments")
    op.drop_column("appointments", "secretaria_id")
