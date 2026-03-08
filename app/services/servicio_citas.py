import asyncio
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.modelo_historial_cita import AppointmentHistory
from app.models.modelo_cita import Appointment
from app.models.modelo_usuario import User
from app.core.tiempo_real import gestor_tiempo_real_citas
from app.repositories.repositorio_citas import RepositorioCitas
from app.schemas.esquema_citas import CrearCita, ActualizarCita, RespuestaHorariosOcupados, RespuestaExtenderTiempo


class ServicioCitas:
    def __init__(self):
        self.repositorio = RepositorioCitas()
        self.estados_finales = {"atendido", "no_asistio", "cancelada"}

    def _normalizar_a_utc_naive(self, valor: datetime) -> datetime:
        if valor.tzinfo is None:
            return valor
        return valor.astimezone(timezone.utc).replace(tzinfo=None)

    def _validar_fecha_agendada(self, db: Session, scheduled_at: datetime | None, excluir_cita_id: int | None = None) -> None:
        if scheduled_at is None:
            return

        fecha_normalizada = self._normalizar_a_utc_naive(scheduled_at)
        ahora_utc = datetime.utcnow()

        if fecha_normalizada < ahora_utc:
            raise HTTPException(
                status_code=400,
                detail="No se puede agendar una cita en una fecha u hora pasada",
            )

        consulta = db.query(Appointment).filter(Appointment.scheduled_at == fecha_normalizada)
        if excluir_cita_id is not None:
            consulta = consulta.filter(Appointment.id != excluir_cita_id)
        if consulta.first():
            raise HTTPException(
                status_code=409,
                detail="Ya existe una cita agendada para esa fecha y hora",
            )

    def _publicar_evento_realtime(self, tipo_evento: str, cita: Appointment) -> None:
        awaitable = gestor_tiempo_real_citas.publicar_evento_cita(tipo_evento, cita)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(awaitable)
        except RuntimeError:
            asyncio.run(awaitable)

    def _publicar_evento_realtime_broadcast(self) -> None:
        awaitable = gestor_tiempo_real_citas.broadcast({"event": "appointment_updated"})
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(awaitable)
        except RuntimeError:
            asyncio.run(awaitable)

    def obtener_horarios_ocupados(self, db: Session) -> RespuestaHorariosOcupados:
        estados_activos = {"pendiente", "llamando", "en_atencion"}
        filas = (
            db.query(Appointment.scheduled_at, Appointment.status, Appointment.attention_started_at, Appointment.extension_count)
            .filter(
                Appointment.scheduled_at.isnot(None),
                Appointment.status.in_(estados_activos),
            )
            .all()
        )
        from app.schemas.esquema_citas import HorarioOcupado
        resultado = []
        for f in filas:
            ends_at = None
            if f[2] is not None:  # attention_started_at
                extensiones = f[3] or 0
                ends_at = f[2] + timedelta(minutes=15 * (1 + extensiones))
            resultado.append(HorarioOcupado(scheduled_at=f[0], status=f[1], attention_ends_at=ends_at))
        return RespuestaHorariosOcupados(horarios=resultado)

    def crear_cita(self, db: Session, payload: CrearCita, student_email: str | None = None, device_id: str | None = None) -> Appointment:
        if student_email is None and device_id is None:
            raise HTTPException(status_code=400, detail="Se requiere student_email o device_id")

        estudiante = None
        estudiante_id = None

        if device_id:
            estados_activos = {"pendiente", "llamando", "en_atencion"}
            activa = (
                db.query(Appointment)
                .filter(
                    Appointment.device_id == device_id,
                    Appointment.status.in_(estados_activos),
                )
                .first()
            )
            if activa:
                raise HTTPException(status_code=409, detail="Ya tienes una cita activa como invitado")
        else:
            estudiante = db.query(User).filter(User.email == student_email).first()
            if not estudiante:
                raise HTTPException(status_code=404, detail="Estudiante no encontrado")
            estudiante_id = estudiante.id

        self._validar_fecha_agendada(db, payload.scheduled_at)

        sede = "asistencia_estudiantil"
        hoy = datetime.utcnow().date()

        ultimo_error: IntegrityError | None = None
        for _ in range(3):
            sec_turno = self.repositorio.siguiente_secuencia_turno(db, sede=sede, para_fecha=hoy)
            numero_turno = f"AE-{hoy.strftime('%Y%m%d')}-{sec_turno:03d}"

            cita = Appointment(
                student_id=estudiante_id,
                device_id=device_id,
                sede=sede,
                category=payload.category,
                context=payload.context,
                status="pendiente",
                turn_number=numero_turno,
                scheduled_at=payload.scheduled_at,
            )
            try:
                creada = self.repositorio.crear(db, cita)
                if estudiante is not None:
                    creada.student = estudiante
                    self._publicar_evento_realtime("appointment_created", creada)
                self._publicar_evento_realtime_broadcast()
                return creada
            except IntegrityError as exc:
                db.rollback()
                ultimo_error = exc

        raise HTTPException(status_code=409, detail="No fue posible asignar turno, intenta nuevamente") from ultimo_error

    def obtener_cola(
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

        return self.repositorio.obtener_cola(
            db,
            sede=sede,
            programa_academico=secretaria.programa_academico,
        )

    def obtener_historial_cola(
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

        return self.repositorio.obtener_historial_cola(
            db,
            sede=sede,
            secretaria_id=secretaria.id,
        )

    def obtener_detalle_cita(
        self,
        db: Session,
        appointment_id: int,
        requester_email: str,
        requester_role: str,
    ) -> dict:
        cita = self.repositorio.obtener_por_id(db=db, appointment_id=appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        estudiante = cita.student or db.query(User).filter(User.id == cita.student_id).first()
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        if requester_role == "secretaria":
            secretaria = db.query(User).filter(User.email == requester_email).first()
            if not secretaria:
                raise HTTPException(status_code=404, detail="Secretaría no encontrada")
            if not secretaria.programa_academico:
                raise HTTPException(status_code=403, detail="La secretaría no tiene programa_academico asignado")
            if estudiante.programa_academico != secretaria.programa_academico:
                raise HTTPException(status_code=403, detail="No puedes ver citas de otro programa")

        return {
            "id": cita.id,
            "student_id": cita.student_id,
            "turn_number": cita.turn_number,
            "sede": cita.sede,
            "category": cita.category,
            "context": cita.context,
            "status": cita.status,
            "created_at": cita.created_at,
            "scheduled_at": cita.scheduled_at,
            "student": {
                "id": estudiante.id,
                "full_name": estudiante.full_name,
                "email": estudiante.email,
                "programa_academico": estudiante.programa_academico,
            },
        }

    def obtener_citas_estudiante(self, db: Session, student_email: str) -> list[Appointment]:
        estudiante = db.query(User).filter(User.email == student_email).first()
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        return self.repositorio.obtener_por_id_estudiante(db=db, student_id=estudiante.id)

    def obtener_historial_citas_estudiante(self, db: Session, student_email: str) -> list[AppointmentHistory]:
        estudiante = db.query(User).filter(User.email == student_email).first()
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        return self.repositorio.obtener_historial_por_id_estudiante(db=db, student_id=estudiante.id)

    def obtener_citas_actuales_estudiante(self, db: Session, student_email: str) -> list[Appointment]:
        estudiante = db.query(User).filter(User.email == student_email).first()
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        return self.repositorio.obtener_actuales_por_id_estudiante(db=db, student_id=estudiante.id)

    def obtener_citas_invitado(self, db: Session, device_id: str) -> list[Appointment]:
        return (
            db.query(Appointment)
            .filter(Appointment.device_id == device_id)
            .order_by(Appointment.created_at.desc())
            .all()
        )

    def actualizar_cita_estudiante(
        self,
        db: Session,
        appointment_id: int,
        payload: ActualizarCita,
        student_email: str,
    ) -> Appointment:
        estudiante = db.query(User).filter(User.email == student_email).first()
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        cita = self.repositorio.obtener_por_id(db=db, appointment_id=appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        if cita.student_id != estudiante.id:
            raise HTTPException(status_code=403, detail="No puedes modificar una cita de otro estudiante")

        if cita.status != "pendiente":
            raise HTTPException(status_code=400, detail="Solo se pueden editar citas en estado pendiente")

        if payload.category is None and payload.context is None and payload.scheduled_at is None:
            raise HTTPException(status_code=400, detail="Debes enviar al menos un campo para actualizar")

        self._validar_fecha_agendada(db, payload.scheduled_at, excluir_cita_id=appointment_id)

        actualizada = self.repositorio.actualizar(
            db=db,
            cita=cita,
            category=payload.category,
            context=payload.context,
            scheduled_at=payload.scheduled_at,
        )
        self._publicar_evento_realtime("appointment_updated", actualizada)
        return actualizada

    def cancelar_cita_estudiante(self, db: Session, appointment_id: int, student_email: str) -> AppointmentHistory:
        estudiante = db.query(User).filter(User.email == student_email).first()
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        cita = self.repositorio.obtener_por_id(db=db, appointment_id=appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        if cita.student_id != estudiante.id:
            raise HTTPException(status_code=403, detail="No puedes cancelar una cita de otro estudiante")

        if cita.status != "pendiente":
            raise HTTPException(status_code=400, detail="Solo se pueden cancelar citas en estado pendiente")

        cita.status = "cancelada"
        archivada = self.repositorio.archivar_y_eliminar(
            db=db,
            cita=cita,
            estado_final="cancelada",
            secretaria_id=None,
        )
        self._publicar_evento_realtime("appointment_cancelled", archivada)
        self._publicar_evento_realtime_broadcast()
        return archivada

    def iniciar_atencion(self, db: Session, appointment_id: int, secretaria_email: str) -> Appointment:
        cita = self.repositorio.obtener_por_id(db, appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        if cita.status != "llamando":
            raise HTTPException(status_code=400, detail="Solo se puede iniciar atención en citas en estado 'llamando'")

        secretaria = db.query(User).filter(User.email == secretaria_email).first()
        if not secretaria:
            raise HTTPException(status_code=404, detail="Secretaría no encontrada")

        if cita.secretaria_id and cita.secretaria_id != secretaria.id:
            raise HTTPException(status_code=403, detail="Esta cita está siendo atendida por otra secretaría")

        ahora_colombia = datetime.now(timezone(timedelta(hours=-5))).replace(tzinfo=None)
        cita.status = "en_atencion"
        cita.attention_started_at = ahora_colombia
        cita.secretaria_id = secretaria.id
        db.commit()
        db.refresh(cita)
        self._publicar_evento_realtime("appointment_status_changed", cita)
        self._publicar_evento_realtime_broadcast()
        return cita

    def extender_tiempo(self, db: Session, appointment_id: int, secretaria_email: str) -> RespuestaExtenderTiempo:
        cita = self.repositorio.obtener_por_id(db, appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        if cita.status != "en_atencion":
            raise HTTPException(status_code=400, detail="Solo se puede extender tiempo de citas en atención")

        if cita.scheduled_at is None:
            raise HTTPException(status_code=400, detail="La cita actual no tiene hora programada")

        delta = timedelta(minutes=15)
        fecha_cita = cita.scheduled_at.date()

        citas_siguientes = (
            db.query(Appointment)
            .filter(
                Appointment.id != cita.id,
                Appointment.status.in_({"pendiente", "llamando"}),
                Appointment.scheduled_at.isnot(None),
                Appointment.scheduled_at > cita.scheduled_at,
            )
            .filter(Appointment.scheduled_at < datetime(fecha_cita.year, fecha_cita.month, fecha_cita.day) + timedelta(days=1))
            .filter(Appointment.scheduled_at >= datetime(fecha_cita.year, fecha_cita.month, fecha_cita.day))
            .order_by(Appointment.scheduled_at.desc())
            .all()
        )

        # Se actualiza en orden descendente con flush individual para no violar
        # el unique constraint de scheduled_at: cada slot se libera antes de ocuparse
        for c in citas_siguientes:
            c.scheduled_at = c.scheduled_at + delta
            db.flush()

        cita.scheduled_at = cita.scheduled_at + delta
        cita.extension_count = (cita.extension_count or 0) + 1
        db.flush()
        db.commit()
        self._publicar_evento_realtime_broadcast()
        return RespuestaExtenderTiempo(
            mensaje="Tiempo extendido 15 minutos",
            citas_actualizadas=len(citas_siguientes) + 1,
        )

    def actualizar_estado(
        self,
        db: Session,
        appointment_id: int,
        new_status: str,
        changed_by_email: str,
    ) -> Appointment | AppointmentHistory:
        cita = self.repositorio.obtener_por_id(db, appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        modificado_por = db.query(User).filter(User.email == changed_by_email).first()
        if not modificado_por:
            raise HTTPException(status_code=404, detail="Usuario que actualiza no encontrado")

        transiciones_validas = {
            "pendiente": {"llamando", "cancelada"},
            "llamando": {"en_atencion", "no_asistio", "cancelada"},
            "en_atencion": {"atendido", "cancelada"},
            "atendido": set(),
            "no_asistio": set(),
            "cancelada": set(),
        }

        if new_status not in transiciones_validas.get(cita.status, set()):
            raise HTTPException(
                status_code=400,
                detail=f"No se puede cambiar de {cita.status} a {new_status}",
            )

        if cita.status in {"llamando", "en_atencion"}:
            if cita.secretaria_id is None:
                cita.secretaria_id = modificado_por.id
            elif cita.secretaria_id != modificado_por.id:
                raise HTTPException(
                    status_code=403,
                    detail="Esta cita está siendo atendida por otra secretaría",
                )

        if cita.status == "pendiente" and new_status == "llamando":
            cita.secretaria_id = modificado_por.id

        if new_status in self.estados_finales:
            attention_ended_at = None
            if cita.status == "en_atencion" and new_status == "atendido":
                ahora_colombia = datetime.now(timezone(timedelta(hours=-5))).replace(tzinfo=None)
                attention_ended_at = ahora_colombia
                if cita.attention_started_at is not None and cita.scheduled_at is not None:
                    import math
                    tiempo_usado = (ahora_colombia - cita.attention_started_at).total_seconds()
                    bloques_usados = math.ceil(max(tiempo_usado, 1) / (15 * 60))
                    bloques_totales = 1 + (cita.extension_count or 0)
                    bloques_a_devolver = bloques_totales - bloques_usados
                    fin_real = cita.attention_started_at + timedelta(minutes=15 * bloques_usados)
                    if bloques_a_devolver > 0 and fin_real < cita.scheduled_at:
                        tiempo_a_devolver = timedelta(minutes=15 * bloques_a_devolver)
                        fecha_cita = cita.scheduled_at.date()
                        siguientes = (
                            db.query(Appointment)
                            .filter(
                                Appointment.status.in_({"pendiente", "llamando"}),
                                Appointment.scheduled_at.isnot(None),
                                Appointment.scheduled_at > cita.scheduled_at,
                            )
                            .filter(Appointment.scheduled_at < datetime(fecha_cita.year, fecha_cita.month, fecha_cita.day) + timedelta(days=1))
                            .order_by(Appointment.scheduled_at.asc())
                            .all()
                        )
                        for s in siguientes:
                            s.scheduled_at = s.scheduled_at - tiempo_a_devolver
                            db.flush()

            cita.status = new_status
            archivada = self.repositorio.archivar_y_eliminar(
                db=db,
                cita=cita,
                estado_final=new_status,
                secretaria_id=cita.secretaria_id or modificado_por.id,
                attention_ended_at=attention_ended_at,
            )
            self._publicar_evento_realtime("appointment_status_changed", archivada)
            self._publicar_evento_realtime_broadcast()
            return archivada

        actualizada = self.repositorio.actualizar_estado(db, cita, new_status)
        self._publicar_evento_realtime("appointment_status_changed", actualizada)
        return actualizada
