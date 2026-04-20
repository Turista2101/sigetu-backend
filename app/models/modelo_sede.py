"""Modelo ORM de sedes asociadas a categorias de atencion."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Sede(Base):
    """Sede operativa para la atencion de citas."""

    __tablename__ = "sedes"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), nullable=False, unique=True, index=True)
    nombre = Column(String(120), nullable=False, unique=True)
    ubicacion = Column(String(255), nullable=True)
    descripcion = Column(String(255), nullable=True)
    es_publica = Column(Boolean, nullable=False, default=True, index=True)
    filtrar_citas_por_programa = Column(Boolean, nullable=False, default=False, index=True)
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    categorias = relationship("Categoria", back_populates="sede", cascade="all, delete-orphan", passive_deletes=True)
    staff_members = relationship("Staff", back_populates="sede", cascade="all, delete-orphan", passive_deletes=True)
    horarios = relationship("HorarioSede", back_populates="sede", cascade="all, delete-orphan", passive_deletes=True)
