from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    sede = Column(String(80), nullable=False, default="asistencia_estudiantil")
    category = Column(String(30), nullable=False, index=True)
    context = Column(String(120), nullable=False)
    status = Column(String(30), nullable=False, default="pendiente", index=True)
    turn_number = Column(String(20), nullable=False, unique=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    scheduled_at = Column(DateTime, nullable=True)

    student = relationship("User", back_populates="appointments")
