"""add appointment checks and queue index

Revision ID: e4f1a9c2d7b8
Revises: c31b6e2f8a44
Create Date: 2026-02-28 10:20:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e4f1a9c2d7b8"
down_revision: Union[str, Sequence[str], None] = "c31b6e2f8a44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


STATUS_CHECK = (
    "status IN ('pendiente','llamando','en_atencion','atendido','no_asistio','finalizada','cancelada')"
)
CATEGORY_CHECK = "category IN ('academico','administrativo','financiero','otro')"


def upgrade() -> None:
    with op.batch_alter_table("appointments") as batch_op:
        batch_op.create_check_constraint("ck_appointments_status_valid", STATUS_CHECK)
        batch_op.create_check_constraint("ck_appointments_category_valid", CATEGORY_CHECK)

    op.create_index(
        "ix_appointments_sede_status_created_at",
        "appointments",
        ["sede", "status", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_appointments_sede_status_created_at", table_name="appointments")

    with op.batch_alter_table("appointments") as batch_op:
        batch_op.drop_constraint("ck_appointments_category_valid", type_="check")
        batch_op.drop_constraint("ck_appointments_status_valid", type_="check")
