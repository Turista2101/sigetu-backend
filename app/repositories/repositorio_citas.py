"""Repositorio de persistencia para citas activas e historial."""

from datetime import date, datetime, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.modelo_historial_cita import AppointmentHistory
from app.models.modelo_cita import Appointment
from app.models.modelo_usuario import User


class RepositorioCitas:
    """Encapsula consultas y escrituras de citas para reutilizar acceso a datos."""

    def crear(self, db: Session, cita: Appointment) -> Appointment:
        """Persiste una cita nueva y devuelve la entidad refrescada."""
        db.add(cita)
        db.commit()
        db.refresh(cita)
        return cita

    def obtener_por_id(self, db: Session, appointment_id: int) -> Appointment | None:
        """Obtiene una cita activa por identificador interno."""
        return db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def obtener_por_id_estudiante(self, db: Session, student_id: int) -> list[Appointment]:
        """Lista citas activas de un estudiante ordenadas por fecha de creación."""
        return (
            db.query(Appointment)
            .filter(Appointment.student_id == student_id)
            .order_by(Appointment.created_at.desc())
            .all()
        )

    def obtener_historial_por_id_estudiante(self, db: Session, student_id: int) -> list[AppointmentHistory]:
        """Lista citas archivadas de un estudiante en orden descendente."""
        return (
            db.query(AppointmentHistory)
            .filter(
                AppointmentHistory.student_id == student_id,
            )
            .order_by(AppointmentHistory.archived_at.desc())
            .all()
        )

    def obtener_historial_por_device_id(self, db: Session, device_id: str) -> list[AppointmentHistory]:
        """Lista citas archivadas de un invitado por device_id en orden descendente."""
        return (
            db.query(AppointmentHistory)
            .filter(
                AppointmentHistory.device_id == device_id,
            )
            .order_by(AppointmentHistory.archived_at.desc())
            .all()
        )

    def obtener_actuales_por_id_estudiante(self, db: Session, student_id: int) -> list[Appointment]:
        """Retorna citas en curso del estudiante para la vista de estado actual."""
        return (
            db.query(Appointment)
            .filter(
                Appointment.student_id == student_id,
                Appointment.status.in_(["pendiente", "llamando", "en_atencion"]),
            )
            .order_by(Appointment.created_at.desc())
            .all()
        )

    def obtener_cola(self, db: Session, sede: str, programa_academico: str | None = None) -> list[Appointment]:
        """Consulta la cola activa por sede, incluyendo estudiantes e invitados."""
        consulta = (
            db.query(Appointment)
            .filter(
                Appointment.sede == sede,
                Appointment.status.in_(["pendiente", "llamando", "en_atencion"]),
                or_(Appointment.student_id != None, Appointment.device_id != None),
            )
            .order_by(Appointment.created_at.asc())
        )

        if programa_academico is not None:
            # Solo filtra por programa_academico si es estudiante
            consulta = consulta.join(User, Appointment.student_id == User.id)
            consulta = consulta.filter(User.programa_academico == programa_academico)

        return consulta.all()

    def obtener_historial_cola(self, db: Session, sede: str, secretaria_id: int | None = None) -> list[AppointmentHistory]:
        """Consulta historial por sede y, cuando aplica, por usuario staff responsable."""
        consulta = (
            db.query(AppointmentHistory)
            .outerjoin(User, AppointmentHistory.student_id == User.id)
            .filter(
                AppointmentHistory.sede == sede,
            )
            .order_by(AppointmentHistory.archived_at.desc())
        )

        if secretaria_id is not None:
            consulta = consulta.filter(AppointmentHistory.secretaria_id == secretaria_id)

        return consulta.all()

    def obtener_historial_por_secretaria(
        self,
        db: Session,
        secretaria_id: int,
        sede: str | None = None,
        fecha_inicio: datetime | None = None,
        fecha_fin: datetime | None = None,
    ) -> list[AppointmentHistory]:
        """Consulta historial de citas atendidas por una secretaría específica."""
        consulta = (
            db.query(AppointmentHistory)
            .outerjoin(User, AppointmentHistory.student_id == User.id)
            .filter(AppointmentHistory.secretaria_id == secretaria_id)
            .order_by(AppointmentHistory.archived_at.desc())
        )

        if sede is not None:
            consulta = consulta.filter(AppointmentHistory.sede == sede)

        if fecha_inicio is not None:
            consulta = consulta.filter(AppointmentHistory.archived_at >= fecha_inicio)

        if fecha_fin is not None:
            consulta = consulta.filter(AppointmentHistory.archived_at <= fecha_fin)

        return consulta.all()

    def actualizar_estado(self, db: Session, cita: Appointment, status: str) -> Appointment:
        """Actualiza estado de una cita activa y confirma transacción."""
        cita.status = status
        db.commit()
        db.refresh(cita)
        return cita

    def archivar_y_eliminar(
        self,
        db: Session,
        cita: Appointment,
        estado_final: str,
        secretaria_id: int | None = None,
        attention_ended_at=None,
        scheduled_at_historial=None,
    ) -> AppointmentHistory:
        """Mueve una cita a historial y elimina el registro activo en una sola operación."""
        historial = AppointmentHistory(
            appointment_id=cita.id,
            student_id=cita.student_id,
            secretaria_id=secretaria_id,
            device_id=cita.device_id,
            sede=cita.sede,
            category=cita.category,
            context=cita.context,
            status=estado_final,
            turn_number=cita.turn_number,
            created_at=cita.created_at,
            scheduled_at=scheduled_at_historial if scheduled_at_historial is not None else cita.scheduled_at,
            attention_started_at=cita.attention_started_at,
            attention_ended_at=attention_ended_at,
            student=cita.student,
        )
        db.add(historial)
        db.delete(cita)
        db.commit()
        db.refresh(historial)
        return historial

    def actualizar(self, db: Session, cita: Appointment, **campos) -> Appointment:
        """Aplica actualización parcial de campos permitidos sobre una cita."""
        for nombre_campo, valor_campo in campos.items():
            if valor_campo is not None:
                setattr(cita, nombre_campo, valor_campo)
        db.commit()
        db.refresh(cita)
        return cita

    def siguiente_secuencia_turno(self, db: Session, sede: str, para_fecha: date) -> int:
        """Calcula el siguiente consecutivo diario de turnos considerando activos e historial.
        
        Busca por prefijo del turn_number en lugar de por fecha de created_at,
        porque created_at se guarda en UTC y para_fecha está en hora Colombia.
        """
        prefijo = para_fecha.strftime("%Y%m%d")

        turnos_activos = (
            db.query(Appointment.turn_number)
            .filter(
                Appointment.sede == sede,
                Appointment.turn_number.like(f"%-{prefijo}-%"),
            )
            .all()
        )

        turnos_historial = (
            db.query(AppointmentHistory.turn_number)
            .filter(
                AppointmentHistory.sede == sede,
                AppointmentHistory.turn_number.like(f"%-{prefijo}-%"),
            )
            .all()
        )

        max_secuencia = 0
        for tupla_turno in [*turnos_activos, *turnos_historial]:
            numero_turno = tupla_turno[0]
            if not numero_turno:
                continue
            partes = numero_turno.split("-")
            if len(partes) != 3:
                continue
            try:
                secuencia = int(partes[2])
            except ValueError:
                continue
            if secuencia > max_secuencia:
                max_secuencia = secuencia

        return max_secuencia + 1
