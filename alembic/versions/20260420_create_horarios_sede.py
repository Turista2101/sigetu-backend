"""Create horarios_sede table

Revision ID: 20260420_create_horarios_sede
Revises: 20260420_drop_cargo_from_staff
Create Date: 2026-04-20 00:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260420_create_horarios_sede"
down_revision: Union[str, Sequence[str], None] = "20260420_drop_cargo_from_staff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "horarios_sede",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sede_id", sa.Integer(), nullable=False),
        sa.Column("dia_semana", sa.Integer(), nullable=False),
        sa.Column("hora_inicio", sa.Time(), nullable=False),
        sa.Column("hora_fin", sa.Time(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("dia_semana BETWEEN 0 AND 6", name="ck_horarios_sede_dia_semana"),
        sa.CheckConstraint("hora_inicio < hora_fin", name="ck_horarios_sede_rango_horas"),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_horarios_sede_id"), "horarios_sede", ["id"], unique=False)
    op.create_index(op.f("ix_horarios_sede_sede_id"), "horarios_sede", ["sede_id"], unique=False)
    op.create_index(op.f("ix_horarios_sede_dia_semana"), "horarios_sede", ["dia_semana"], unique=False)
    op.create_index(op.f("ix_horarios_sede_activo"), "horarios_sede", ["activo"], unique=False)
    op.create_index("ix_horarios_sede_sede_dia", "horarios_sede", ["sede_id", "dia_semana"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_horarios_sede_sede_dia", table_name="horarios_sede")
    op.drop_index(op.f("ix_horarios_sede_activo"), table_name="horarios_sede")
    op.drop_index(op.f("ix_horarios_sede_dia_semana"), table_name="horarios_sede")
    op.drop_index(op.f("ix_horarios_sede_sede_id"), table_name="horarios_sede")
    op.drop_index(op.f("ix_horarios_sede_id"), table_name="horarios_sede")
    op.drop_table("horarios_sede")
