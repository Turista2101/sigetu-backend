import asyncio
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.appointment_history_model import AppointmentHistory
from app.models.appointment_model import Appointment
from app.models.user_model import User
from app.core.realtime import appointment_realtime_manager
from app.repositories.appointment_repository import AppointmentRepository
from app.schemas.appointment_schema import AppointmentCreate, AppointmentUpdate


class AppointmentService:
    def __init__(self):
        self.repository = AppointmentRepository()
        self.final_statuses = {"atendido", "no_asistio", "cancelada"}

    def _normalize_to_utc_naive(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value
        return value.astimezone().replace(tzinfo=None)

    def _validate_scheduled_at(self, scheduled_at: datetime | None) -> None:
        if scheduled_at is None:
            return

        normalized_scheduled_at = self._normalize_to_utc_naive(scheduled_at)
        now_utc_naive = datetime.utcnow()

        if normalized_scheduled_at < now_utc_naive:
            raise HTTPException(
                status_code=400,
                detail="No se puede agendar una cita en una fecha u hora pasada",
            )

    def _publish_realtime_event(self, event_type: str, appointment: Appointment) -> None:
        awaitable = appointment_realtime_manager.publish_appointment_event(event_type, appointment)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(awaitable)
        except RuntimeError:
            asyncio.run(awaitable)

    def create_appointment(self, db: Session, payload: AppointmentCreate, student_email: str) -> Appointment:
        student = db.query(User).filter(User.email == student_email).first()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        self._validate_scheduled_at(payload.scheduled_at)

        sede = "asistencia_estudiantil"
        today = datetime.utcnow().date()
        turn_seq = self.repository.next_turn_sequence(db, sede=sede, for_date=today)
        turn_number = f"AE-{today.strftime('%Y%m%d')}-{turn_seq:03d}"

        appointment = Appointment(
            student_id=student.id,
            sede=sede,
            category=payload.category,
            context=payload.context,
            status="pendiente",
            turn_number=turn_number,
            scheduled_at=payload.scheduled_at,
        )
        created = self.repository.create(db, appointment)
        created.student = student
        self._publish_realtime_event("appointment_created", created)
        return created

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

    def get_queue_history(
        self,
        db: Session,
        secretaria_email: str,
        sede: str = "asistencia_estudiantil",
    ) -> list[AppointmentHistory]:
        secretaria = db.query(User).filter(User.email == secretaria_email).first()
        if not secretaria:
            raise HTTPException(status_code=404, detail="Secretaría no encontrada")

        if not secretaria.programa_academico:
            raise HTTPException(status_code=403, detail="La secretaría no tiene programa_academico asignado")

        return self.repository.get_queue_history(
            db,
            sede=sede,
            programa_academico=secretaria.programa_academico,
        )

    def get_appointment_detail(
        self,
        db: Session,
        appointment_id: int,
        requester_email: str,
        requester_role: str,
    ) -> dict:
        appointment = self.repository.get_by_id(db=db, appointment_id=appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        student = appointment.student or db.query(User).filter(User.id == appointment.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        if requester_role == "secretaria":
            secretaria = db.query(User).filter(User.email == requester_email).first()
            if not secretaria:
                raise HTTPException(status_code=404, detail="Secretaría no encontrada")
            if not secretaria.programa_academico:
                raise HTTPException(status_code=403, detail="La secretaría no tiene programa_academico asignado")
            if student.programa_academico != secretaria.programa_academico:
                raise HTTPException(status_code=403, detail="No puedes ver citas de otro programa")

        return {
            "id": appointment.id,
            "student_id": appointment.student_id,
            "turn_number": appointment.turn_number,
            "sede": appointment.sede,
            "category": appointment.category,
            "context": appointment.context,
            "status": appointment.status,
            "created_at": appointment.created_at,
            "scheduled_at": appointment.scheduled_at,
            "student": {
                "id": student.id,
                "full_name": student.full_name,
                "email": student.email,
                "programa_academico": student.programa_academico,
            },
        }

    def get_student_appointments(self, db: Session, student_email: str) -> list[Appointment]:
        student = db.query(User).filter(User.email == student_email).first()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        return self.repository.get_by_student_id(db=db, student_id=student.id)

    def get_student_appointment_history(self, db: Session, student_email: str) -> list[AppointmentHistory]:
        student = db.query(User).filter(User.email == student_email).first()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        return self.repository.get_history_by_student_id(db=db, student_id=student.id)

    def get_student_current_appointments(self, db: Session, student_email: str) -> list[Appointment]:
        student = db.query(User).filter(User.email == student_email).first()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        return self.repository.get_current_by_student_id(db=db, student_id=student.id)

    def update_student_appointment(
        self,
        db: Session,
        appointment_id: int,
        payload: AppointmentUpdate,
        student_email: str,
    ) -> Appointment:
        student = db.query(User).filter(User.email == student_email).first()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        appointment = self.repository.get_by_id(db=db, appointment_id=appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        if appointment.student_id != student.id:
            raise HTTPException(status_code=403, detail="No puedes modificar una cita de otro estudiante")

        if appointment.status != "pendiente":
            raise HTTPException(status_code=400, detail="Solo se pueden editar citas en estado pendiente")

        if payload.category is None and payload.context is None and payload.scheduled_at is None:
            raise HTTPException(status_code=400, detail="Debes enviar al menos un campo para actualizar")

        self._validate_scheduled_at(payload.scheduled_at)

        updated = self.repository.update(
            db=db,
            appointment=appointment,
            category=payload.category,
            context=payload.context,
            scheduled_at=payload.scheduled_at,
        )
        self._publish_realtime_event("appointment_updated", updated)
        return updated

    def cancel_student_appointment(self, db: Session, appointment_id: int, student_email: str) -> AppointmentHistory:
        student = db.query(User).filter(User.email == student_email).first()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        appointment = self.repository.get_by_id(db=db, appointment_id=appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        if appointment.student_id != student.id:
            raise HTTPException(status_code=403, detail="No puedes cancelar una cita de otro estudiante")

        if appointment.status != "pendiente":
            raise HTTPException(status_code=400, detail="Solo se pueden cancelar citas en estado pendiente")

        appointment.status = "cancelada"
        archived = self.repository.archive_and_delete(
            db=db,
            appointment=appointment,
            final_status="cancelada",
            secretaria_id=None,
        )
        self._publish_realtime_event("appointment_cancelled", archived)
        return archived

    def update_status(
        self,
        db: Session,
        appointment_id: int,
        new_status: str,
        changed_by_email: str,
    ) -> Appointment | AppointmentHistory:
        appointment = self.repository.get_by_id(db, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        changed_by_user = db.query(User).filter(User.email == changed_by_email).first()
        if not changed_by_user:
            raise HTTPException(status_code=404, detail="Usuario que actualiza no encontrado")

        valid_transitions = {
            "pendiente": {"llamando", "cancelada"},
            "llamando": {"en_atencion", "no_asistio", "cancelada"},
            "en_atencion": {"atendido", "cancelada"},
            "atendido": set(),
            "no_asistio": set(),
            "cancelada": set(),
        }

        if new_status not in valid_transitions.get(appointment.status, set()):
            raise HTTPException(
                status_code=400,
                detail=f"No se puede cambiar de {appointment.status} a {new_status}",
            )

        if new_status in self.final_statuses:
            appointment.status = new_status
            archived = self.repository.archive_and_delete(
                db=db,
                appointment=appointment,
                final_status=new_status,
                secretaria_id=changed_by_user.id,
            )
            self._publish_realtime_event("appointment_status_changed", archived)
            return archived

        updated = self.repository.update_status(db, appointment, new_status)
        self._publish_realtime_event("appointment_status_changed", updated)
        return updated
