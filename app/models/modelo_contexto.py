"""Modelo ORM de contextos para clasificar categorias."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class Contexto(Base):
    """Catalogo de contextos funcionales por categoria."""

    __tablename__ = "contextos"
    __table_args__ = (
        UniqueConstraint("categoria_id", "codigo", name="uq_contextos_categoria_codigo"),
        UniqueConstraint("categoria_id", "nombre", name="uq_contextos_categoria_nombre"),
    )

    id = Column(Integer, primary_key=True, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="CASCADE"), nullable=False, index=True)
    codigo = Column(String(50), nullable=False)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(String(255), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    categoria = relationship("Categoria", back_populates="contextos")
