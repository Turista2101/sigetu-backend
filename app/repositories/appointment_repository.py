from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.appointment_model import Appointment
from app.models.user_model import User


class AppointmentRepository:
    def create(self, db: Session, appointment: Appointment) -> Appointment:
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return appointment

    def get_by_id(self, db: Session, appointment_id: int) -> Appointment | None:
        return db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def get_by_student_id(self, db: Session, student_id: int) -> list[Appointment]:
        return (
            db.query(Appointment)
            .filter(Appointment.student_id == student_id)
            .order_by(Appointment.created_at.desc())
            .all()
        )

    def get_queue(self, db: Session, sede: str, programa_academico: str | None = None) -> list[Appointment]:
        query = (
            db.query(Appointment)
            .join(User, Appointment.student_id == User.id)
            .filter(
                Appointment.sede == sede,
                Appointment.status.in_(["pendiente", "llamando", "en_atencion"]),
            )
            .order_by(Appointment.created_at.asc())
        )

        if programa_academico is not None:
            query = query.filter(User.programa_academico == programa_academico)

        return query.all()

    def update_status(self, db: Session, appointment: Appointment, status: str) -> Appointment:
        appointment.status = status
        db.commit()
        db.refresh(appointment)
        return appointment

    def next_turn_sequence(self, db: Session, sede: str, for_date: date) -> int:
        count = (
            db.query(func.count(Appointment.id))
            .filter(
                Appointment.sede == sede,
                func.date(Appointment.created_at) == for_date,
            )
            .scalar()
        )
        return int(count or 0) + 1
