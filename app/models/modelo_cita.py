"""Modelo ORM de citas activas en cola por sede."""

from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class Appointment(Base):
    """Representa una cita activa con estado, turno y metadatos de atención."""
    __tablename__ = "appointments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pendiente','llamando','en_atencion','atendido','no_asistio','cancelada')",
            name="ck_appointments_status_valid",
        ),
        CheckConstraint(
            "(student_id IS NULL) != (device_id IS NULL)",
            name="ck_appointments_owner",
        ),
        UniqueConstraint("contexto_id", "scheduled_at", name="uq_appointments_contexto_id_scheduled_at"),
        Index("ix_appointments_contexto_id_status_created_at", "contexto_id", "status", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    device_id = Column(String(36), nullable=True, index=True)
    secretaria_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    contexto_id = Column(Integer, ForeignKey("contextos.id", ondelete="RESTRICT"), nullable=False, index=True)

    status = Column(String(30), nullable=False, default="pendiente", index=True)
    turn_number = Column(String(20), nullable=False, unique=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    scheduled_at = Column(DateTime, nullable=True)
    attention_started_at = Column(DateTime, nullable=True)
    extension_count = Column(Integer, nullable=False, default=0)

    student = relationship("User", back_populates="appointments", foreign_keys=[student_id])
    secretaria = relationship("User", foreign_keys=[secretaria_id])
    contexto_rel = relationship("Contexto", foreign_keys=[contexto_id])

    @property
    def sede_rel(self):
        """Devuelve la sede asociada al contexto de la cita."""
        if self.contexto_rel is None or self.contexto_rel.categoria is None:
            return None
        return self.contexto_rel.categoria.sede

    @property
    def sede(self) -> str | None:
        """Devuelve el codigo de sede asociado a la cita."""
        sede_rel = self.sede_rel
        if sede_rel is None:
            return None
        return sede_rel.codigo

    @property
    def category(self) -> str | None:
        """Devuelve el codigo de categoria asociado al contexto de la cita."""
        if self.contexto_rel is None or self.contexto_rel.categoria is None:
            return None
        return self.contexto_rel.categoria.codigo

    @property
    def context(self) -> str | None:
        """Devuelve el codigo de contexto asociado a la cita."""
        if self.contexto_rel is None:
            return None
        return self.contexto_rel.codigo

    @property
    def student_name(self) -> str | None:
        """Expone nombre del estudiante relacionado para serialización rápida."""
        if self.student is None:
            return None
        return self.student.full_name

    @property
    def secretaria_name(self) -> str | None:
        """Expone nombre del staff asignado para vistas de cola."""
        if self.secretaria is None:
            return None
        return self.secretaria.full_name
