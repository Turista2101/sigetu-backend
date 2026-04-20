"""Modelo ORM para asignaciones operativas de staff a sede."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Staff(Base):
    """Relación operativa 1:1 entre usuario staff y sede."""

    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="CASCADE"), nullable=False, index=True)
    # cargo eliminado
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="staff")
    sede = relationship("Sede", back_populates="staff_members")
