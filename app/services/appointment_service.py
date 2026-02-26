from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.appointment_model import Appointment
from app.models.user_model import User
from app.repositories.appointment_repository import AppointmentRepository
from app.schemas.appointment_schema import AppointmentCreate


class AppointmentService:
    def __init__(self):
        self.repository = AppointmentRepository()

    def create_appointment(self, db: Session, payload: AppointmentCreate, student_email: str) -> Appointment:
        student = db.query(User).filter(User.email == student_email).first()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        sede = "asistencia_estudiantil"
        turn_seq = self.repository.next_turn_sequence(db, sede=sede, for_date=datetime.utcnow().date())
        turn_number = f"AE-{turn_seq:03d}"

        appointment = Appointment(
            student_id=student.id,
            sede=sede,
            category=payload.category,
            context=payload.context,
            status="pendiente",
            turn_number=turn_number,
            scheduled_at=payload.scheduled_at,
        )
        return self.repository.create(db, appointment)

    def get_queue(
        self,
        db: Session,
        secretaria_email: str,
        sede: str = "asistencia_estudiantil",
    ) -> list[Appointment]:
        secretaria = db.query(User).filter(User.email == secretaria_email).first()
        if not secretaria:
            raise HTTPException(status_code=404, detail="Secretaría no encontrada")

        if not secretaria.programa_academico:
            raise HTTPException(status_code=403, detail="La secretaría no tiene programa_academico asignado")

        return self.repository.get_queue(
            db,
            sede=sede,
            programa_academico=secretaria.programa_academico,
        )

    def get_student_appointments(self, db: Session, student_email: str) -> list[Appointment]:
        student = db.query(User).filter(User.email == student_email).first()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        return self.repository.get_by_student_id(db=db, student_id=student.id)

    def update_status(self, db: Session, appointment_id: int, new_status: str) -> Appointment:
        appointment = self.repository.get_by_id(db, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        valid_transitions = {
            "pendiente": {"llamando", "cancelada"},
            "llamando": {"en_atencion", "cancelada"},
            "en_atencion": {"finalizada", "cancelada"},
            "finalizada": set(),
            "cancelada": set(),
        }

        if new_status not in valid_transitions.get(appointment.status, set()):
            raise HTTPException(
                status_code=400,
                detail=f"No se puede cambiar de {appointment.status} a {new_status}",
            )

        return self.repository.update_status(db, appointment, new_status)
