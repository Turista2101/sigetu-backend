from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(150), unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    full_name = Column(String(150), nullable=False)

    programa_academico = Column(String(50), nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    role = relationship("Role", back_populates="users")
    appointments = relationship(
        "Appointment",
        back_populates="student",
        foreign_keys="Appointment.student_id",
        passive_deletes=True,
    )
