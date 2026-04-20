"""Modelo ORM de categorias asociadas a una sede."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class Categoria(Base):
    """Categoria de atencion agrupada por sede."""

    __tablename__ = "categorias"
    __table_args__ = (
        UniqueConstraint("sede_id", "codigo", name="uq_categorias_sede_codigo"),
        UniqueConstraint("sede_id", "nombre", name="uq_categorias_sede_nombre"),
    )

    id = Column(Integer, primary_key=True, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="CASCADE"), nullable=False, index=True)
    codigo = Column(String(50), nullable=False)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(String(255), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    sede = relationship("Sede", back_populates="categorias")
    contextos = relationship("Contexto", back_populates="categoria", cascade="all, delete-orphan", passive_deletes=True)
