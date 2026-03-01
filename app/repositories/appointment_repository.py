from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.appointment_history_model import AppointmentHistory
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

    def get_history_by_student_id(self, db: Session, student_id: int) -> list[AppointmentHistory]:
        return (
            db.query(AppointmentHistory)
            .filter(
                AppointmentHistory.student_id == student_id,
            )
            .order_by(AppointmentHistory.archived_at.desc())
            .all()
        )

    def get_current_by_student_id(self, db: Session, student_id: int) -> list[Appointment]:
        return (
            db.query(Appointment)
            .filter(
                Appointment.student_id == student_id,
                Appointment.status.in_(["pendiente", "llamando", "en_atencion"]),
            )
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

    def get_queue_history(self, db: Session, sede: str, programa_academico: str | None = None) -> list[AppointmentHistory]:
        query = (
            db.query(AppointmentHistory)
            .join(User, AppointmentHistory.student_id == User.id)
            .filter(
                AppointmentHistory.sede == sede,
            )
            .order_by(AppointmentHistory.archived_at.desc())
        )

        if programa_academico is not None:
            query = query.filter(User.programa_academico == programa_academico)

        return query.all()

    def update_status(self, db: Session, appointment: Appointment, status: str) -> Appointment:
        appointment.status = status
        db.commit()
        db.refresh(appointment)
        return appointment

    def archive_and_delete(
        self,
        db: Session,
        appointment: Appointment,
        final_status: str,
        secretaria_id: int | None = None,
    ) -> AppointmentHistory:
        history = AppointmentHistory(
            appointment_id=appointment.id,
            student_id=appointment.student_id,
            secretaria_id=secretaria_id,
            sede=appointment.sede,
            category=appointment.category,
            context=appointment.context,
            status=final_status,
            turn_number=appointment.turn_number,
            created_at=appointment.created_at,
            scheduled_at=appointment.scheduled_at,
            student=appointment.student,
        )
        db.add(history)
        db.delete(appointment)
        db.commit()
        db.refresh(history)
        return history

    def update(self, db: Session, appointment: Appointment, **fields) -> Appointment:
        for field_name, field_value in fields.items():
            if field_value is not None:
                setattr(appointment, field_name, field_value)
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
