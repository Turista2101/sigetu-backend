"""Modelo ORM de citas archivadas con resultado final de atención."""

from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.modelo_sede import Sede


class AppointmentHistory(Base):
    """Representa una cita finalizada o cancelada movida fuera de la cola activa."""
    __tablename__ = "appointment_history"
    __table_args__ = (
        CheckConstraint(
            "status IN ('atendido','no_asistio','cancelada')",
            name="ck_appointment_history_status_valid",
        ),
        Index("ix_appointment_history_student_id_archived_at", "student_id", "archived_at"),
        Index("ix_appointment_history_contexto_id_status_archived_at", "contexto_id", "status", "archived_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, nullable=False, unique=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    secretaria_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    device_id = Column(String(36), nullable=True, index=True)
    contexto_id = Column(Integer, ForeignKey("contextos.id", ondelete="RESTRICT"), nullable=False, index=True)

    status = Column(String(30), nullable=False, index=True)
    turn_number = Column(String(20), nullable=False, index=True)

    created_at = Column(DateTime, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    attention_started_at = Column(DateTime, nullable=True)
    attention_ended_at = Column(DateTime, nullable=True)
    archived_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    student = relationship("User", foreign_keys=[student_id])
    secretaria = relationship("User", foreign_keys=[secretaria_id])
    contexto_rel = relationship("Contexto", foreign_keys=[contexto_id])

    @property
    def sede_rel(self):
        """Devuelve la sede asociada al contexto del historial."""
        if self.contexto_rel is None or self.contexto_rel.categoria is None:
            return None
        return self.contexto_rel.categoria.sede

    @property
    def sede(self) -> str | None:
        """Devuelve el codigo de sede asociado al historial."""
        sede_rel = self.sede_rel
        if sede_rel is None:
            return None
        return sede_rel.codigo

    @property
    def category(self) -> str | None:
        """Devuelve el codigo de categoria asociado al contexto del historial."""
        if self.contexto_rel is None or self.contexto_rel.categoria is None:
            return None
        return self.contexto_rel.categoria.codigo

    @property
    def context(self) -> str | None:
        """Devuelve el codigo de contexto asociado al historial."""
        if self.contexto_rel is None:
            return None
        return self.contexto_rel.codigo

    @property
    def student_name(self) -> str | None:
        """Devuelve nombre del estudiante asociado para respuestas de historial."""
        if self.student is None:
            return None
        return self.student.full_name

    @property
    def student_programa_academico_id(self) -> int | None:
        """Devuelve el id del programa académico del estudiante."""
        if self.student is None:
            return None
        if self.student.programa is None:
            return None
        return self.student.programa.id

    @property
    def secretaria_name(self) -> str | None:
        """Devuelve nombre del staff que gestionó la cita archivada."""
        if self.secretaria is None:
            return None
        return self.secretaria.full_name
