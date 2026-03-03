"""create appointment history and remove finalizada

Revision ID: b9f3c1d8a7e2
Revises: d2c7a1f3b8e9
Create Date: 2026-03-01 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b9f3c1d8a7e2"
down_revision: Union[str, Sequence[str], None] = "d2c7a1f3b8e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NEW_STATUS_CHECK = "status IN ('pendiente','llamando','en_atencion','atendido','no_asistio','cancelada')"
OLD_STATUS_CHECK = "status IN ('pendiente','llamando','en_atencion','atendido','no_asistio','finalizada','cancelada')"


def upgrade() -> None:
    op.execute("UPDATE appointments SET status = 'atendido' WHERE status = 'finalizada'")

    with op.batch_alter_table("appointments") as batch_op:
        batch_op.drop_constraint("ck_appointments_status_valid", type_="check")
        batch_op.create_check_constraint("ck_appointments_status_valid", NEW_STATUS_CHECK)

    op.create_table(
        "appointment_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("appointment_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("secretaria_id", sa.Integer(), nullable=True),
        sa.Column("sede", sa.String(length=80), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("context", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("turn_number", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["secretaria_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("appointment_id"),
        sa.CheckConstraint("status IN ('atendido','no_asistio','cancelada')", name="ck_appointment_history_status_valid"),
        sa.CheckConstraint(
            "category IN ('academico','administrativo','financiero','otro')",
            name="ck_appointment_history_category_valid",
        ),
    )

    op.create_index(op.f("ix_appointment_history_id"), "appointment_history", ["id"], unique=False)
    op.create_index(op.f("ix_appointment_history_appointment_id"), "appointment_history", ["appointment_id"], unique=False)
    op.create_index(op.f("ix_appointment_history_student_id"), "appointment_history", ["student_id"], unique=False)
    op.create_index(op.f("ix_appointment_history_secretaria_id"), "appointment_history", ["secretaria_id"], unique=False)
    op.create_index(op.f("ix_appointment_history_category"), "appointment_history", ["category"], unique=False)
    op.create_index(op.f("ix_appointment_history_status"), "appointment_history", ["status"], unique=False)
    op.create_index(op.f("ix_appointment_history_turn_number"), "appointment_history", ["turn_number"], unique=False)
    op.create_index(op.f("ix_appointment_history_archived_at"), "appointment_history", ["archived_at"], unique=False)
    op.create_index(
        "ix_appointment_history_student_id_archived_at",
        "appointment_history",
        ["student_id", "archived_at"],
        unique=False,
    )
    op.create_index(
        "ix_appointment_history_sede_status_archived_at",
        "appointment_history",
        ["sede", "status", "archived_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_appointment_history_sede_status_archived_at", table_name="appointment_history")
    op.drop_index("ix_appointment_history_student_id_archived_at", table_name="appointment_history")
    op.drop_index(op.f("ix_appointment_history_archived_at"), table_name="appointment_history")
    op.drop_index(op.f("ix_appointment_history_turn_number"), table_name="appointment_history")
    op.drop_index(op.f("ix_appointment_history_status"), table_name="appointment_history")
    op.drop_index(op.f("ix_appointment_history_category"), table_name="appointment_history")
    op.drop_index(op.f("ix_appointment_history_secretaria_id"), table_name="appointment_history")
    op.drop_index(op.f("ix_appointment_history_student_id"), table_name="appointment_history")
    op.drop_index(op.f("ix_appointment_history_appointment_id"), table_name="appointment_history")
    op.drop_index(op.f("ix_appointment_history_id"), table_name="appointment_history")
    op.drop_table("appointment_history")

    with op.batch_alter_table("appointments") as batch_op:
        batch_op.drop_constraint("ck_appointments_status_valid", type_="check")
        batch_op.create_check_constraint("ck_appointments_status_valid", OLD_STATUS_CHECK)
