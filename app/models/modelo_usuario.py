"""Modelo ORM de usuarios autenticados del sistema."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base

class User(Base):
    """Entidad de usuario con relación a rol y citas asociadas."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(150), unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    full_name = Column(String(150), nullable=False)

    programa_academico_id = Column(Integer, ForeignKey("programas_academicos.id", ondelete="RESTRICT"), nullable=False, index=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    role = relationship("Role", back_populates="users")
    programa = relationship("ProgramaAcademico", back_populates="users", foreign_keys=[programa_academico_id])
    staff = relationship("Staff", back_populates="user", uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    appointments = relationship(
        "Appointment",
        back_populates="student",
        foreign_keys="Appointment.student_id",
        passive_deletes=True,
    )
