"""Modelo ORM para catalogo de roles de usuario."""

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Role(Base):
    """Representa un rol funcional del sistema (estudiante, staff, admin)."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="role")