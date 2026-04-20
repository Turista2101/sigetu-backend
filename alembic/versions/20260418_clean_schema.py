"""clean consolidated schema

Revision ID: 20260418_clean_schema
Revises: None
Create Date: 2026-04-18 15:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260418_clean_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


STATUS_VALID = "status IN ('pendiente','llamando','en_atencion','atendido','no_asistio','cancelada')"
HISTORY_STATUS_VALID = "status IN ('atendido','no_asistio','cancelada')"


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )

    op.create_table(
        "programas_academicos",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("codigo", name="uq_programas_academicos_codigo"),
        sa.UniqueConstraint("nombre", name="uq_programas_academicos_nombre"),
    )
    op.create_index("ix_programas_academicos_activo", "programas_academicos", ["activo"], unique=False)

    op.create_table(
        "sedes",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("ubicacion", sa.String(length=255), nullable=True),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("es_publica", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("filtrar_citas_por_programa", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("codigo", name="uq_sedes_codigo"),
        sa.UniqueConstraint("nombre", name="uq_sedes_nombre"),
    )
    op.create_index("ix_sedes_codigo", "sedes", ["codigo"], unique=True)
    op.create_index("ix_sedes_es_publica", "sedes", ["es_publica"], unique=False)
    op.create_index("ix_sedes_filtrar_citas_por_programa", "sedes", ["filtrar_citas_por_programa"], unique=False)
    op.create_index("ix_sedes_activo", "sedes", ["activo"], unique=False)

    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("sede_id", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("sede_id", "codigo", name="uq_categorias_sede_codigo"),
        sa.UniqueConstraint("sede_id", "nombre", name="uq_categorias_sede_nombre"),
    )
    op.create_index("ix_categorias_sede_id", "categorias", ["sede_id"], unique=False)
    op.create_index("ix_categorias_activo", "categorias", ["activo"], unique=False)

    op.create_table(
        "contextos",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("categoria_id", "codigo", name="uq_contextos_categoria_codigo"),
        sa.UniqueConstraint("categoria_id", "nombre", name="uq_contextos_categoria_nombre"),
    )
    op.create_index("ix_contextos_categoria_id", "contextos", ["categoria_id"], unique=False)
    op.create_index("ix_contextos_activo", "contextos", ["activo"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("programa_academico_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["programa_academico_id"], ["programas_academicos.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_programa_academico_id", "users", ["programa_academico_id"], unique=False)

    op.create_table(
        "staff",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("sede_id", sa.Integer(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_staff_user_id"),
    )
    op.create_index("ix_staff_user_id", "staff", ["user_id"], unique=True)
    op.create_index("ix_staff_sede_id", "staff", ["sede_id"], unique=False)
    op.create_index("ix_staff_activo", "staff", ["activo"], unique=False)

    op.create_table(
        "revoked_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("jti", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("jti", name="uq_revoked_tokens_jti"),
    )
    op.create_index("ix_revoked_tokens_jti", "revoked_tokens", ["jti"], unique=True)
    op.create_index("ix_revoked_tokens_expires_at", "revoked_tokens", ["expires_at"], unique=False)

    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=True),
        sa.Column("device_id", sa.String(length=36), nullable=True),
        sa.Column("secretaria_id", sa.Integer(), nullable=True),
        sa.Column("contexto_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'pendiente'")),
        sa.Column("turn_number", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("attention_started_at", sa.DateTime(), nullable=True),
        sa.Column("extension_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.CheckConstraint(STATUS_VALID, name="ck_appointments_status_valid"),
        sa.CheckConstraint("(student_id IS NULL) != (device_id IS NULL)", name="ck_appointments_owner"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["secretaria_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["contexto_id"], ["contextos.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("contexto_id", "scheduled_at", name="uq_appointments_contexto_id_scheduled_at"),
        sa.UniqueConstraint("turn_number", name="uq_appointments_turn_number"),
    )
    op.create_index("ix_appointments_student_id", "appointments", ["student_id"], unique=False)
    op.create_index("ix_appointments_device_id", "appointments", ["device_id"], unique=False)
    op.create_index("ix_appointments_secretaria_id", "appointments", ["secretaria_id"], unique=False)
    op.create_index("ix_appointments_contexto_id", "appointments", ["contexto_id"], unique=False)
    op.create_index("ix_appointments_contexto_id_status_created_at", "appointments", ["contexto_id", "status", "created_at"], unique=False)
    op.create_index("ix_appointments_status", "appointments", ["status"], unique=False)
    op.create_index("ix_appointments_turn_number", "appointments", ["turn_number"], unique=True)
    op.create_index("ix_appointments_created_at", "appointments", ["created_at"], unique=False)

    op.create_table(
        "appointment_history",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("appointment_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=True),
        sa.Column("secretaria_id", sa.Integer(), nullable=True),
        sa.Column("device_id", sa.String(length=36), nullable=True),
        sa.Column("contexto_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("turn_number", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("attention_started_at", sa.DateTime(), nullable=True),
        sa.Column("attention_ended_at", sa.DateTime(), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(HISTORY_STATUS_VALID, name="ck_appointment_history_status_valid"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["secretaria_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["contexto_id"], ["contextos.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("appointment_id", name="uq_appointment_history_appointment_id"),
    )
    op.create_index("ix_appointment_history_student_id_archived_at", "appointment_history", ["student_id", "archived_at"], unique=False)
    op.create_index("ix_appointment_history_contexto_id", "appointment_history", ["contexto_id"], unique=False)
    op.create_index("ix_appointment_history_contexto_id_status_archived_at", "appointment_history", ["contexto_id", "status", "archived_at"], unique=False)
    op.create_index("ix_appointment_history_appointment_id", "appointment_history", ["appointment_id"], unique=True)
    op.create_index("ix_appointment_history_archived_at", "appointment_history", ["archived_at"], unique=False)

    op.create_table(
        "fcm_device_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("device_id", sa.String(length=128), nullable=False),
        sa.Column("token", sa.String(length=512), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("token", name="uq_fcm_device_tokens_token"),
        sa.UniqueConstraint("user_id", "device_id", name="uq_fcm_device_tokens_user_device"),
    )
    op.create_index("ix_fcm_device_tokens_user_id", "fcm_device_tokens", ["user_id"], unique=False)
    op.create_index("ix_fcm_device_tokens_device_id", "fcm_device_tokens", ["device_id"], unique=False)
    op.create_index("ix_fcm_device_tokens_token", "fcm_device_tokens", ["token"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_fcm_device_tokens_token", table_name="fcm_device_tokens")
    op.drop_index("ix_fcm_device_tokens_device_id", table_name="fcm_device_tokens")
    op.drop_index("ix_fcm_device_tokens_user_id", table_name="fcm_device_tokens")
    op.drop_table("fcm_device_tokens")

    op.drop_index("ix_appointment_history_archived_at", table_name="appointment_history")
    op.drop_index("ix_appointment_history_appointment_id", table_name="appointment_history")
    op.drop_index("ix_appointment_history_contexto_id", table_name="appointment_history")
    op.drop_index("ix_appointment_history_contexto_id_status_archived_at", table_name="appointment_history")
    op.drop_index("ix_appointment_history_student_id_archived_at", table_name="appointment_history")
    op.drop_table("appointment_history")

    op.drop_index("ix_appointments_created_at", table_name="appointments")
    op.drop_index("ix_appointments_turn_number", table_name="appointments")
    op.drop_index("ix_appointments_status", table_name="appointments")
    op.drop_index("ix_appointments_contexto_id", table_name="appointments")
    op.drop_index("ix_appointments_contexto_id_status_created_at", table_name="appointments")
    op.drop_index("ix_appointments_secretaria_id", table_name="appointments")
    op.drop_index("ix_appointments_device_id", table_name="appointments")
    op.drop_index("ix_appointments_student_id", table_name="appointments")
    op.drop_table("appointments")

    op.drop_index("ix_revoked_tokens_expires_at", table_name="revoked_tokens")
    op.drop_index("ix_revoked_tokens_jti", table_name="revoked_tokens")
    op.drop_table("revoked_tokens")

    op.drop_index("ix_staff_activo", table_name="staff")
    op.drop_index("ix_staff_sede_id", table_name="staff")
    op.drop_index("ix_staff_user_id", table_name="staff")
    op.drop_table("staff")

    op.drop_index("ix_users_programa_academico_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_contextos_activo", table_name="contextos")
    op.drop_index("ix_contextos_categoria_id", table_name="contextos")
    op.drop_table("contextos")

    op.drop_index("ix_categorias_activo", table_name="categorias")
    op.drop_index("ix_categorias_sede_id", table_name="categorias")
    op.drop_table("categorias")

    op.drop_index("ix_sedes_activo", table_name="sedes")
    op.drop_index("ix_sedes_filtrar_citas_por_programa", table_name="sedes")
    op.drop_index("ix_sedes_es_publica", table_name="sedes")
    op.drop_index("ix_sedes_codigo", table_name="sedes")
    op.drop_table("sedes")

    op.drop_index("ix_programas_academicos_activo", table_name="programas_academicos")
    op.drop_table("programas_academicos")

    op.drop_index("ix_roles_is_staff", table_name="roles")
    op.drop_table("roles")
