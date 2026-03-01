from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pendiente','llamando','en_atencion','atendido','no_asistio','cancelada')",
            name="ck_appointments_status_valid",
        ),
        CheckConstraint(
            "category IN ('academico','administrativo','financiero','otro')",
            name="ck_appointments_category_valid",
        ),
        Index("ix_appointments_sede_status_created_at", "sede", "status", "created_at"),
    )

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

    @property
    def student_name(self) -> str | None:
        if self.student is None:
            return None
        return self.student.full_name
