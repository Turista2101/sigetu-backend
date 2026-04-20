"""Modelo ORM para bloques de horario de atención por sede."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Time
from sqlalchemy.orm import relationship

from app.db.base import Base


class HorarioSede(Base):
    """Bloque de horario de atención para una sede y día de la semana."""

    __tablename__ = "horarios_sede"

    id = Column(Integer, primary_key=True, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="CASCADE"), nullable=False, index=True)
    dia_semana = Column(Integer, nullable=False, index=True)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    sede = relationship("Sede", back_populates="horarios")