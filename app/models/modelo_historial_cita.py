"""Modelo ORM de citas archivadas con resultado final de atención."""

from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class AppointmentHistory(Base):
    """Representa una cita finalizada o cancelada movida fuera de la cola activa."""
    __tablename__ = "appointment_history"
    __table_args__ = (
        CheckConstraint(
            "status IN ('atendido','no_asistio','cancelada')",
            name="ck_appointment_history_status_valid",
        ),
        CheckConstraint(
            (
                "category IN "
                "('academico','administrativo','financiero','otro',"
                "'pagos_facturacion','recibos_certificados','creditos_financiacion',"
                "'problemas_soporte_financiero','plataformas_servicios',"
                "'informacion_academica','inscripcion_matricula')"
            ),
            name="ck_appointment_history_category_valid",
        ),
        Index("ix_appointment_history_student_id_archived_at", "student_id", "archived_at"),
        Index("ix_appointment_history_sede_status_archived_at", "sede", "status", "archived_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, nullable=False, unique=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    secretaria_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    device_id = Column(String(36), nullable=True, index=True)

    sede = Column(String(80), nullable=False)
    category = Column(String(30), nullable=False, index=True)
    context = Column(String(120), nullable=False)
    status = Column(String(30), nullable=False, index=True)
    turn_number = Column(String(20), nullable=False, index=True)

    created_at = Column(DateTime, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    attention_started_at = Column(DateTime, nullable=True)
    attention_ended_at = Column(DateTime, nullable=True)
    archived_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    student = relationship("User", foreign_keys=[student_id])
    secretaria = relationship("User", foreign_keys=[secretaria_id])

    @property
    def student_name(self) -> str | None:
        """Devuelve nombre del estudiante asociado para respuestas de historial."""
        if self.student is None:
            return None
        return self.student.full_name

    @property
    def student_programa_academico(self) -> str | None:
        """Devuelve el programa académico del estudiante."""
        if self.student is None:
            return None
        return self.student.programa_academico

    @property
    def secretaria_name(self) -> str | None:
        """Devuelve nombre del staff que gestionó la cita archivada."""
        if self.secretaria is None:
            return None
        return self.secretaria.full_name
