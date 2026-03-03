"""create appointments table

Revision ID: 1f2c3d4e5f6a
Revises: bd65e13f9cbb
Create Date: 2026-02-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1f2c3d4e5f6a"
down_revision: Union[str, Sequence[str], None] = "bd65e13f9cbb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("sede", sa.String(length=80), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("context", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("turn_number", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_appointments_id"), "appointments", ["id"], unique=False)
    op.create_index(op.f("ix_appointments_student_id"), "appointments", ["student_id"], unique=False)
    op.create_index(op.f("ix_appointments_category"), "appointments", ["category"], unique=False)
    op.create_index(op.f("ix_appointments_status"), "appointments", ["status"], unique=False)
    op.create_index(op.f("ix_appointments_turn_number"), "appointments", ["turn_number"], unique=True)
    op.create_index(op.f("ix_appointments_created_at"), "appointments", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_appointments_created_at"), table_name="appointments")
    op.drop_index(op.f("ix_appointments_turn_number"), table_name="appointments")
    op.drop_index(op.f("ix_appointments_status"), table_name="appointments")
    op.drop_index(op.f("ix_appointments_category"), table_name="appointments")
    op.drop_index(op.f("ix_appointments_student_id"), table_name="appointments")
    op.drop_index(op.f("ix_appointments_id"), table_name="appointments")
    op.drop_table("appointments")
