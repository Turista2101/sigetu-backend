"""Servicio de negocio para gestión de citas, cola, estados y reglas por sede."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.modelo_historial_cita import AppointmentHistory
from app.models.modelo_cita import Appointment
from app.models.modelo_contexto import Contexto
from app.models.modelo_horario_sede import HorarioSede
from app.models.modelo_sede import Sede
from app.models.modelo_usuario import User
from app.core.tiempo_real import gestor_tiempo_real_citas
from app.repositories.repositorio_citas import RepositorioCitas
from app.schemas.esquema_citas import CrearCita, ActualizarCita, RespuestaHorariosOcupados, RespuestaExtenderTiempo
from app.services.servicio_notificaciones import ServicioNotificaciones


SEDE_ASISTENCIA = "asistencia_estudiantil"
SEDE_ADMINISTRATIVA = "sede_administrativa"
SEDE_ADMISIONES_MERCADEO = "sede_admisiones_mercadeo"

# CAMBIO: Zona horaria de Colombia (UTC-5) como constante global
COLOMBIA_TZ = timezone(timedelta(hours=-5))
logger = logging.getLogger(__name__)

class ServicioCitas:
    """Centraliza reglas de negocio de citas para estudiantes y personal de atención."""

    def __init__(self):
        self.repositorio = RepositorioCitas()
        self.servicio_notificaciones = ServicioNotificaciones()
        self.estados_finales = {"atendido", "no_asistio", "cancelada"}

    def _obtener_usuario_staff(self, db: Session, staff_email: str) -> User:
        """Obtiene un usuario staff con asignación operativa vigente."""
        usuario = db.query(User).filter(User.email == staff_email).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if usuario.staff is None or not usuario.staff.activo:
            raise HTTPException(status_code=403, detail="El usuario no tiene asignación staff activa")
        return usuario

    def _obtener_sede_staff(self, db: Session, staff_email: str) -> Sede:
        """Obtiene la sede operativa del staff desde su asignación en tabla staff."""
        usuario = self._obtener_usuario_staff(db=db, staff_email=staff_email)
        sede = usuario.staff.sede if usuario.staff else None
        if sede is None or not sede.activo:
            raise HTTPException(status_code=403, detail="El usuario no tiene una sede activa asociada")
        return sede

    def actualizar_cita_invitado(
        self,
        db: Session,
        appointment_id: int,
        payload: ActualizarCita,
        device_id: str,
    ) -> Appointment:
        """Permite editar cita pendiente de invitado validando reglas de sede."""
        cita = self.repositorio.obtener_por_id(db=db, appointment_id=appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        if cita.device_id != device_id:
            raise HTTPException(status_code=403, detail="No puedes modificar una cita de otro dispositivo")
        if cita.status != "pendiente":
            raise HTTPException(status_code=400, detail="Solo se pueden editar citas en estado pendiente")
        if payload.contexto_id is None and payload.scheduled_at is None:
            raise HTTPException(status_code=400, detail="Debes enviar al menos un campo para actualizar")
        contexto_id_objetivo = payload.contexto_id or cita.contexto_id
        self._obtener_contexto_activo_por_id(db=db, contexto_id=contexto_id_objetivo)
        self._validar_fecha_agendada(db, payload.scheduled_at, contexto_id=contexto_id_objetivo, excluir_cita_id=appointment_id)
        actualizada = self.repositorio.actualizar(
            db=db,
            cita=cita,
            contexto_id=payload.contexto_id,
            scheduled_at=payload.scheduled_at,
        )
        self._publicar_evento_realtime("appointment_updated", actualizada)
        self.servicio_notificaciones.notificar_estado_cita_invitado(
            db=db,
            device_id=device_id,
            nuevo_estado=actualizada.status,
            turno=actualizada.turn_number,
        )
        return actualizada

    def _obtener_contexto_activo_por_id(self, db: Session, contexto_id: int) -> Contexto:
        contexto = db.query(Contexto).filter(Contexto.id == contexto_id).first()
        if not contexto or not contexto.activo:
            raise HTTPException(status_code=404, detail="Contexto no encontrado o inactivo")
        if contexto.categoria is None or contexto.categoria.sede is None or not contexto.categoria.sede.activo:
            raise HTTPException(status_code=404, detail="Contexto sin sede activa asociada")
        return contexto

    def _obtener_sede_desde_contexto(self, contexto: Contexto) -> Sede:
        if contexto.categoria is None or contexto.categoria.sede is None:
            raise HTTPException(status_code=404, detail="Contexto sin sede asociada")
        sede = contexto.categoria.sede
        if not sede.activo:
            raise HTTPException(status_code=404, detail="Sede no encontrada o inactiva")
        return sede

    def _normalizar_a_colombia_naive(self, valor: datetime) -> datetime:
        """Convierte cualquier datetime a hora Colombia naive para persistencia consistente.
        - Sin tzinfo: asume que ya es hora Colombia, lo devuelve tal cual.
        - Con tzinfo: convierte a COLOMBIA_TZ y elimina tzinfo.
        """
        if valor.tzinfo is None:
            return valor
        return valor.astimezone(COLOMBIA_TZ).replace(tzinfo=None)

    def _validar_fecha_agendada(
        self,
        db: Session,
        scheduled_at: datetime | None,
        contexto_id: int,
        excluir_cita_id: int | None = None,
    ) -> None:
        """Valida disponibilidad de `scheduled_at` por contexto y evita fechas en pasado."""
        if scheduled_at is None:
            return

        # CORRECCIÓN 2: Usar método y variable de Colombia en lugar de UTC
        fecha_normalizada = self._normalizar_a_colombia_naive(scheduled_at)
        ahora_colombia = datetime.now(COLOMBIA_TZ).replace(tzinfo=None)

        if fecha_normalizada < ahora_colombia:
            raise HTTPException(
                status_code=400,
                detail="No se puede agendar una cita en una fecha u hora pasada",
            )

        contexto = db.query(Contexto).filter(Contexto.id == contexto_id).first()
        if not contexto or not contexto.categoria or not contexto.categoria.sede:
            raise HTTPException(status_code=404, detail="Contexto sin sede activa asociada")

        sede = contexto.categoria.sede
        dia_semana = fecha_normalizada.weekday()
        hora_cita = fecha_normalizada.time()
        bloque_disponible = (
            db.query(HorarioSede)
            .filter(
                HorarioSede.sede_id == sede.id,
                HorarioSede.dia_semana == dia_semana,
                HorarioSede.activo.is_(True),
                HorarioSede.hora_inicio <= hora_cita,
                HorarioSede.hora_fin > hora_cita,
            )
            .first()
        )
        if not bloque_disponible:
            raise HTTPException(
                status_code=400,
                detail="La fecha y hora agendada está fuera del horario de atención de la sede",
            )

        consulta = db.query(Appointment).filter(
            Appointment.contexto_id == contexto_id,
            Appointment.scheduled_at == fecha_normalizada,
        )
        if excluir_cita_id is not None:
            consulta = consulta.filter(Appointment.id != excluir_cita_id)
        if consulta.first():
            raise HTTPException(
                status_code=409,
                detail="Ya existe una cita agendada para esa fecha y hora",
            )

    def _publicar_evento_realtime(self, tipo_evento: str, cita: Appointment) -> None:
        """Publica un evento puntual de cita sin bloquear el flujo HTTP."""
        awaitable = gestor_tiempo_real_citas.publicar_evento_cita(tipo_evento, cita)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(awaitable)
        except RuntimeError:
            asyncio.run(awaitable)

    def _publicar_evento_realtime_broadcast(self) -> None:
        """Dispara notificación global para refresco de vistas de cola."""
        awaitable = gestor_tiempo_real_citas.broadcast({"event": "appointment_updated"})
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(awaitable)
        except RuntimeError:
            asyncio.run(awaitable)

    def _prefijo_turno_por_sede(self, sede: str) -> str:
        """Retorna prefijo de turno según sede para trazabilidad operativa."""
        if sede == SEDE_ADMINISTRATIVA:
            return "AD"
        if sede == SEDE_ADMISIONES_MERCADEO:
            return "AM"
        return "AE"

    def obtener_horarios_ocupados(self, db: Session, contexto_id: int) -> RespuestaHorariosOcupados:
        """Lista horarios ocupados y su estado activo para un contexto específico.

        CORRECCIÓN 3: Filtra citas cuyo scheduled_at ya pasó usando hora Colombia.
        """
        estados_activos = {"pendiente", "llamando", "en_atencion"}
        # CORRECCIÓN 3: Usar hora Colombia en lugar de UTC
        ahora_colombia = datetime.now(COLOMBIA_TZ).replace(tzinfo=None)
        filas = (
            db.query(Appointment.scheduled_at, Appointment.status, Appointment.attention_started_at, Appointment.extension_count)
            .filter(
                Appointment.contexto_id == contexto_id,
                Appointment.scheduled_at.isnot(None),
                Appointment.status.in_(estados_activos),
                Appointment.scheduled_at >= ahora_colombia,  # CORRECCIÓN 3: Solo citas futuras o actuales
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

    def crear_cita(
        self,
        db: Session,
        payload: CrearCita,
        student_email: str | None = None,
        device_id: str | None = None,
    ) -> Appointment:
        """Crea una cita para estudiante o invitado respetando reglas de sede y disponibilidad."""
        if student_email is None and device_id is None:
            raise HTTPException(status_code=400, detail="Se requiere student_email o device_id")

        estudiante = None
        estudiante_id = None

        # Invitado: permitir múltiples citas activas (sin restricción por device_id)
        if device_id:
            pass
        else:
            estudiante = db.query(User).filter(User.email == student_email).first()
            if not estudiante:
                raise HTTPException(status_code=404, detail="Estudiante no encontrado")
            estudiante_id = estudiante.id

        contexto = self._obtener_contexto_activo_por_id(db=db, contexto_id=payload.contexto_id)
        sede = self._obtener_sede_desde_contexto(contexto)
        if device_id and not sede.es_publica:
            raise HTTPException(
                status_code=403,
                detail="Esta sede es privada y requiere cuenta de estudiante para agendar citas",
            )
        self._validar_fecha_agendada(db, payload.scheduled_at, contexto_id=contexto.id)

        # CAMBIO: Usar hora de Colombia para obtener la fecha local correcta
        hoy = datetime.now(COLOMBIA_TZ).replace(tzinfo=None).date()
        logger.debug("hoy Colombia para secuencia de turnos: %s", hoy)

        for _ in range(3):
            sec_turno = self.repositorio.siguiente_secuencia_turno(db, sede_codigo=sede.codigo, para_fecha=hoy)
            prefijo_turno = self._prefijo_turno_por_sede(sede.codigo)
            numero_turno = f"{prefijo_turno}-{hoy.strftime('%Y%m%d')}-{sec_turno:03d}"

            cita = Appointment(
                student_id=estudiante_id,
                device_id=device_id,
                contexto_id=payload.contexto_id,
                status="pendiente",
                turn_number=numero_turno,
                scheduled_at=payload.scheduled_at,
            )
            try:
                self.repositorio.crear(db, cita)
                self._publicar_evento_realtime("appointment_created", cita)
                self._publicar_evento_realtime_broadcast()
                # Notificación push a invitado si aplica
                if device_id:
                    self.servicio_notificaciones.notificar_estado_cita_invitado(
                        db=db,
                        device_id=device_id,
                        nuevo_estado="pendiente",
                        turno=numero_turno,
                    )
                return cita
            except IntegrityError as exc:
                db.rollback()
                logger.warning("Conflicto de integridad al crear cita, reintentando: %s", exc)
        raise HTTPException(status_code=409, detail="No se pudo crear la cita: conflicto de horario")

    def obtener_cola(
        self,
        db: Session,
        staff_email: str,
    ) -> list[Appointment]:
        """Obtiene cola activa de la sede del staff autenticado."""
        usuario = self._obtener_usuario_staff(db=db, staff_email=staff_email)
        sede = self._obtener_sede_staff(db=db, staff_email=staff_email)
        filtrar_por_programa = bool(sede.filtrar_citas_por_programa)

        if filtrar_por_programa and not usuario.programa:
            raise HTTPException(status_code=403, detail="El usuario no tiene programa_academico asignado")

        programa_academico_id = usuario.programa.id if filtrar_por_programa else None

        return self.repositorio.obtener_cola(
            db,
            sede_codigo=sede.codigo,
            programa_academico_id=programa_academico_id,
        )

    def obtener_historial_cola(
        self,
        db: Session,
        staff_email: str,
    ) -> list[AppointmentHistory]:
        """Obtiene historial de atención de la sede del staff autenticado."""
        usuario = self._obtener_usuario_staff(db=db, staff_email=staff_email)
        sede = self._obtener_sede_staff(db=db, staff_email=staff_email)
        filtrar_por_programa = bool(sede.filtrar_citas_por_programa)

        if filtrar_por_programa and not usuario.programa:
            raise HTTPException(status_code=403, detail="El usuario no tiene programa_academico asignado")

        programa_academico_id = usuario.programa.id if filtrar_por_programa else None

        return self.repositorio.obtener_historial_cola(
            db,
            sede=sede.codigo,
            programa_academico_id=programa_academico_id,
        )

    def obtener_historial_secretaria(
        self,
        db: Session,
        secretaria_email: str,
        sede: str | None = None,
        fecha_inicio: datetime | None = None,
        fecha_fin: datetime | None = None,
    ) -> list[AppointmentHistory]:
        """Obtiene historial de citas atendidas por una secretaría específica."""
        secretaria = db.query(User).filter(User.email == secretaria_email).first()
        if not secretaria:
            raise HTTPException(status_code=404, detail="Secretaría no encontrada")

        return self.repositorio.obtener_historial_por_secretaria(
            db=db,
            secretaria_id=secretaria.id,
            sede=sede,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

    def obtener_detalle_cita(
        self,
        db: Session,
        appointment_id: int,
        requester_email: str,
        requester_role: str,
    ) -> dict:
        """Retorna detalle de cita aplicando controles de visibilidad por sede y rol. Soporta citas de invitados."""
        cita = self.repositorio.obtener_por_id(db=db, appointment_id=appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        # Si es cita de invitado, no hay estudiante asociado
        if cita.student_id is None and cita.device_id:
            estudiante = None
        else:
            estudiante = cita.student or db.query(User).filter(User.id == cita.student_id).first()
            if not estudiante:
                raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        if requester_role not in {"estudiante", "guest"}:
            sede_permitida = self._obtener_sede_staff(db=db, staff_email=requester_email)
            if cita.sede != sede_permitida.codigo:
                raise HTTPException(status_code=403, detail="No puedes ver citas de otra sede")

        # Construir respuesta compatible para ambos casos
        detalle = {
            "id": cita.id,
            "student_id": cita.student_id,
            "device_id": cita.device_id,
            "contexto_id": cita.contexto_id,
            "turn_number": cita.turn_number,
            "sede": cita.sede,
            "category": cita.category,
            "context": cita.context,
            "status": cita.status,
            "created_at": cita.created_at,
            "scheduled_at": cita.scheduled_at,
            "attention_started_at": cita.attention_started_at,
            "extension_count": getattr(cita, "extension_count", 0),
        }
        if estudiante:
            detalle["student"] = {
                "id": estudiante.id,
                "full_name": estudiante.full_name,
                "email": estudiante.email,
                "programa_academico_id": estudiante.programa.id,
            }
        else:
            detalle["student"] = None
        return detalle

    def obtener_citas_estudiante(self, db: Session, student_email: str) -> list[Appointment]:
        """Lista todas las citas activas del estudiante autenticado."""
        estudiante = db.query(User).filter(User.email == student_email).first()
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        return self.repositorio.obtener_por_id_estudiante(db=db, student_id=estudiante.id)

    def obtener_historial_citas_estudiante(self, db: Session, student_email: str) -> list[AppointmentHistory]:
        """Lista historial de citas finalizadas/canceladas del estudiante."""
        estudiante = db.query(User).filter(User.email == student_email).first()
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        return self.repositorio.obtener_historial_por_id_estudiante(db=db, student_id=estudiante.id)

    def obtener_citas_actuales_estudiante(self, db: Session, student_email: str) -> list[Appointment]:
        """Retorna únicamente citas en curso para seguimiento rápido del estudiante."""
        estudiante = db.query(User).filter(User.email == student_email).first()
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        return self.repositorio.obtener_actuales_por_id_estudiante(db=db, student_id=estudiante.id)

    def obtener_citas_invitado(self, db: Session, device_id: str) -> list[Appointment]:
        """Consulta citas asociadas al `device_id` del flujo invitado."""
        return (
            db.query(Appointment)
            .filter(Appointment.device_id == device_id)
            .order_by(Appointment.created_at.desc())
            .all()
        )

    def obtener_historial_invitado(self, db: Session, device_id: str) -> list[AppointmentHistory]:
        """Consulta historial de citas archivadas del invitado por device_id."""
        return self.repositorio.obtener_historial_por_device_id(db=db, device_id=device_id)

    def actualizar_cita_estudiante(
        self,
        db: Session,
        appointment_id: int,
        payload: ActualizarCita,
        student_email: str,
    ) -> Appointment:
        """Permite editar cita pendiente del estudiante validando reglas de sede."""
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

        if payload.contexto_id is None and payload.scheduled_at is None:
            raise HTTPException(status_code=400, detail="Debes enviar al menos un campo para actualizar")

        contexto_id_objetivo = payload.contexto_id or cita.contexto_id
        self._obtener_contexto_activo_por_id(db=db, contexto_id=contexto_id_objetivo)
        self._validar_fecha_agendada(db, payload.scheduled_at, contexto_id=contexto_id_objetivo, excluir_cita_id=appointment_id)

        actualizada = self.repositorio.actualizar(
            db=db,
            cita=cita,
            contexto_id=payload.contexto_id,
            scheduled_at=payload.scheduled_at,
        )
        self._publicar_evento_realtime("appointment_updated", actualizada)
        return actualizada

    def cancelar_cita_estudiante(self, db: Session, appointment_id: int, student_email: str) -> AppointmentHistory:
        """Cancela una cita pendiente del estudiante y la mueve a historial."""
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

    def cancelar_cita_invitado(self, db: Session, appointment_id: int, device_id: str) -> AppointmentHistory:
        """Cancela una cita pendiente de invitado y la mueve a historial."""
        cita = self.repositorio.obtener_por_id(db=db, appointment_id=appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        if cita.device_id != device_id:
            raise HTTPException(status_code=403, detail="No puedes cancelar una cita de otro dispositivo")
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
        # Notificación push a invitado
        self.servicio_notificaciones.notificar_estado_cita_invitado(
            db=db,
            device_id=device_id,
            nuevo_estado="cancelada",
            turno=archivada.turn_number,
        )
        return archivada

    def iniciar_atencion(self, db: Session, appointment_id: int, staff_email: str) -> Appointment:
        """Marca una cita como `en_atencion` por un miembro del staff autorizado."""
        cita = self.repositorio.obtener_por_id(db, appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        sede_permitida = self._obtener_sede_staff(db=db, staff_email=staff_email)
        if cita.sede != sede_permitida.codigo:
            raise HTTPException(status_code=403, detail="No puedes gestionar citas de otra sede")

        if cita.status != "llamando":
            raise HTTPException(status_code=400, detail="Solo se puede iniciar atención en citas en estado 'llamando'")

        secretaria = db.query(User).filter(User.email == staff_email).first()
        if not secretaria:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if cita.secretaria_id and cita.secretaria_id != secretaria.id:
            raise HTTPException(status_code=403, detail="Esta cita está siendo atendida por otra secretaría")

        # CAMBIO: Usar constante COLOMBIA_TZ en lugar de crear timezone cada vez
        ahora_colombia = datetime.now(COLOMBIA_TZ).replace(tzinfo=None)
        cita.status = "en_atencion"
        cita.attention_started_at = ahora_colombia
        cita.secretaria_id = secretaria.id
        db.commit()
        db.refresh(cita)
        self._publicar_evento_realtime("appointment_status_changed", cita)
        self._publicar_evento_realtime_broadcast()
        
        # Notificar a estudiante autenticado o invitado
        if cita.student_id:
            self.servicio_notificaciones.notificar_estado_cita(
                db=db,
                user_id=cita.student_id,
                nuevo_estado=cita.status,
                turno=cita.turn_number,
            )
        elif cita.device_id:
            self.servicio_notificaciones.notificar_estado_cita_invitado(
                db=db,
                device_id=cita.device_id,
                nuevo_estado=cita.status,
                turno=cita.turn_number,
            )
        
        # Notificar al staff que inició la atención
        self.servicio_notificaciones.notificar_estado_cita_staff(
            db=db,
            user_id=secretaria.id,
            nuevo_estado=cita.status,
            turno=cita.turn_number,
            accion="Atención iniciada",
        )
        
        return cita

    def extender_tiempo(self, db: Session, appointment_id: int, staff_email: str) -> RespuestaExtenderTiempo:
        """Extiende 15 minutos la cita en atención y reajusta turnos siguientes en la misma sede."""
        cita = self.repositorio.obtener_por_id(db, appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        sede_permitida = self._obtener_sede_staff(db=db, staff_email=staff_email)
        if cita.sede != sede_permitida.codigo:
            raise HTTPException(status_code=403, detail="No puedes gestionar citas de otra sede")

        if cita.status != "en_atencion":
            raise HTTPException(status_code=400, detail="Solo se puede extender tiempo de citas en atención")

        secretaria = db.query(User).filter(User.email == staff_email).first()
        if not secretaria:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if cita.secretaria_id and cita.secretaria_id != secretaria.id:
            raise HTTPException(status_code=403, detail="Esta cita está siendo atendida por otro usuario")

        if cita.scheduled_at is None:
            raise HTTPException(status_code=400, detail="La cita actual no tiene hora programada")

        delta = timedelta(minutes=15)
        fecha_cita = cita.scheduled_at.date()

        citas_siguientes = (
            db.query(Appointment)
            .filter(
                Appointment.id != cita.id,
                Appointment.contexto_id == cita.contexto_id,
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

        # Notificar a cada cita afectada por la extensión
        for c in citas_siguientes:
            nuevo_horario = c.scheduled_at.strftime('%H:%M')
            self.servicio_notificaciones.notificar_extension_tiempo(
                db=db,
                turno=c.turn_number,
                nuevo_horario=nuevo_horario,
                user_id=c.student_id,
                device_id=c.device_id,
            )

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
        changed_by_role: str,
    ) -> Appointment | AppointmentHistory:
        """Aplica transición de estado de cita respetando flujo permitido y ownership de atención."""
        cita = self.repositorio.obtener_por_id(db, appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        if changed_by_role not in {"estudiante", "guest"}:
            sede_permitida = self._obtener_sede_staff(db=db, staff_email=changed_by_email)
            if cita.sede != sede_permitida.codigo:
                raise HTTPException(status_code=403, detail="No puedes gestionar citas de otra sede")

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
            scheduled_at_original = cita.scheduled_at
            if cita.status == "en_atencion" and new_status == "atendido":
                # CAMBIO: Usar constante COLOMBIA_TZ en lugar de crear timezone cada vez
                ahora_colombia = datetime.now(COLOMBIA_TZ).replace(tzinfo=None)
                attention_ended_at = ahora_colombia
                if cita.attention_started_at is not None and cita.scheduled_at is not None:
                    import math
                    tiempo_usado = (ahora_colombia - cita.attention_started_at).total_seconds()
                    bloques_usados = math.floor(max(tiempo_usado, 1) / (15 * 60))
                    bloques_totales = 1 + (cita.extension_count or 0)
                    bloques_extendidos = cita.extension_count or 0  # ← solo los extendidos, sin el base
                    bloques_a_devolver = min(bloques_extendidos - bloques_usados, bloques_extendidos)  # ← nunca devuelve el bloque base
                    bloques_a_devolver = max(bloques_a_devolver, 0)  # ← nunca negativo
                    fin_real = cita.attention_started_at + timedelta(minutes=15 * bloques_usados)
                    if bloques_a_devolver > 0 and fin_real < cita.scheduled_at:
                        cita.scheduled_at = None
                        db.flush()

                        tiempo_a_devolver = timedelta(minutes=15 * bloques_a_devolver)
                        fecha_cita = scheduled_at_original.date()
                        siguientes = (
                            db.query(Appointment)
                            .filter(
                                Appointment.contexto_id == cita.contexto_id,
                                Appointment.status.in_({"pendiente", "llamando"}),
                                Appointment.scheduled_at.isnot(None),
                                Appointment.scheduled_at > scheduled_at_original,
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
                scheduled_at_historial=scheduled_at_original,
            )
            self._publicar_evento_realtime("appointment_status_changed", archivada)
            self._publicar_evento_realtime_broadcast()

            # Notificar a estudiante autenticado o invitado
            if archivada.student_id:
                self.servicio_notificaciones.notificar_estado_cita(
                    db=db,
                    user_id=archivada.student_id,
                    nuevo_estado=archivada.status,
                    turno=archivada.turn_number,
                )
            elif archivada.device_id:
                self.servicio_notificaciones.notificar_estado_cita_invitado(
                    db=db,
                    device_id=archivada.device_id,
                    nuevo_estado=archivada.status,
                    turno=archivada.turn_number,
                )
            return archivada

        actualizada = self.repositorio.actualizar_estado(db, cita, new_status)
        self._publicar_evento_realtime("appointment_status_changed", actualizada)
        
        # Notificar a estudiante autenticado o invitado (dueño de la cita)
        if actualizada.student_id:
            self.servicio_notificaciones.notificar_estado_cita(
                db=db,
                user_id=actualizada.student_id,
                nuevo_estado=actualizada.status,
                turno=actualizada.turn_number,
            )
        elif actualizada.device_id:
            self.servicio_notificaciones.notificar_estado_cita_invitado(
                db=db,
                device_id=actualizada.device_id,
                nuevo_estado=actualizada.status,
                turno=actualizada.turn_number,
            )
        
        # Notificar al staff que realizó el cambio (para que reciba confirmación en su dispositivo)
        if changed_by_role in {"secretaria", "administrativo", "admisiones_mercadeo"}:
            staff = db.query(User).filter(User.email == changed_by_email).first()
            if staff:
                self.servicio_notificaciones.notificar_estado_cita_staff(
                    db=db,
                    user_id=staff.id,
                    nuevo_estado=actualizada.status,
                    turno=actualizada.turn_number,
                    accion=f"Cita {new_status}",
                )
        
        return actualizada
