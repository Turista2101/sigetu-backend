"""Servicio de negocio para gestión de citas, cola, estados y reglas por sede."""

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
from app.services.servicio_notificaciones import ServicioNotificaciones


SEDE_ASISTENCIA = "asistencia_estudiantil"
SEDE_ADMINISTRATIVA = "sede_administrativa"
SEDE_ADMISIONES_MERCADEO = "sede_admisiones_mercadeo"

# CAMBIO: Zona horaria de Colombia (UTC-5) como constante global
COLOMBIA_TZ = timezone(timedelta(hours=-5))

CATEGORIAS_CONTEXTO_ADMINISTRATIVA: dict[str, set[str]] = {
    "pagos_facturacion": {
        "pagos_con_tarjeta",
        "validacion_pagos",
        "facturacion_electronica",
        "cruces_saldos_favor",
        "aplicacion_descuentos",
    },
    "recibos_certificados": {
        "generacion_recibos",
        "certificado_valores_pagados",
        "constancias_certificados",
    },
    "creditos_financiacion": {
        "tramites_credito",
        "financiacion_interna_externa",
        "tramites_icetex",
    },
    "problemas_soporte_financiero": {
        "problemas_matriculas_financieras",
    },
    "plataformas_servicios": {
        "habilitacion_plataformas",
    },
}

CATEGORIAS_CONTEXTO_ADMISIONES_MERCADEO: dict[str, set[str]] = {
    "informacion_academica": {
        "informacion_primer_semestre",
        "informacion_pregrados_posgrados",
    },
    "inscripcion_matricula": {
        "informacion_matricula_nuevos_primer_semestre",
    },
}


class ServicioCitas:
    """Centraliza reglas de negocio de citas para estudiantes y personal de atención."""

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
            if payload.category is None and payload.context is None and payload.scheduled_at is None:
                raise HTTPException(status_code=400, detail="Debes enviar al menos un campo para actualizar")
            categoria_objetivo = payload.category or cita.category
            contexto_objetivo = payload.context or cita.context
            self._validar_categoria_contexto_por_sede(cita.sede, categoria_objetivo, contexto_objetivo)
            self._validar_fecha_agendada(db, payload.scheduled_at, sede=cita.sede, excluir_cita_id=appointment_id)
            actualizada = self.repositorio.actualizar(
                db=db,
                cita=cita,
                category=payload.category,
                context=payload.context,
                scheduled_at=payload.scheduled_at,
            )
            self._publicar_evento_realtime("appointment_updated", actualizada)
            # Notificación push a invitado
            self.servicio_notificaciones.notificar_estado_cita_invitado(
                db=db,
                device_id=device_id,
                nuevo_estado=actualizada.status,
                turno=actualizada.turn_number,
            )
            return actualizada
    """Centraliza reglas de negocio de citas para estudiantes y personal de atención."""

    def __init__(self):
        self.repositorio = RepositorioCitas()
        self.servicio_notificaciones = ServicioNotificaciones()
        self.estados_finales = {"atendido", "no_asistio", "cancelada"}

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
        sede: str,
        excluir_cita_id: int | None = None,
    ) -> None:
        """Valida disponibilidad de `scheduled_at` por sede y evita fechas en pasado."""
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

        consulta = db.query(Appointment).filter(
            Appointment.sede == sede,
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

    def _resolver_sede_por_rol(self, role: str) -> str:
        """Mapea cada rol operativo a la sede que tiene autorizada."""
        if role == "secretaria":
            return SEDE_ASISTENCIA
        if role == "administrativo":
            return SEDE_ADMINISTRATIVA
        if role == "admisiones_mercadeo":
            return SEDE_ADMISIONES_MERCADEO
        raise HTTPException(status_code=403, detail="Rol sin acceso a gestión de sedes")

    def _prefijo_turno_por_sede(self, sede: str) -> str:
        """Retorna prefijo de turno según sede para trazabilidad operativa."""
        if sede == SEDE_ADMINISTRATIVA:
            return "AD"
        if sede == SEDE_ADMISIONES_MERCADEO:
            return "AM"
        return "AE"

    def _categorias_contexto_por_sede(self, sede: str) -> dict[str, set[str]] | None:
        """Devuelve catálogo de categorías/contextos válidos para sedes especializadas."""
        if sede == SEDE_ADMINISTRATIVA:
            return CATEGORIAS_CONTEXTO_ADMINISTRATIVA
        if sede == SEDE_ADMISIONES_MERCADEO:
            return CATEGORIAS_CONTEXTO_ADMISIONES_MERCADEO
        return None

    def _validar_categoria_contexto_por_sede(self, sede: str, category: str | None, context: str | None) -> None:
        """Aplica validación de categoría y contexto según configuración de sede."""
        categorias_contexto = self._categorias_contexto_por_sede(sede)
        if categorias_contexto is None:
            return

        if category is None or context is None:
            return

        contextos_validos = categorias_contexto.get(category)
        if contextos_validos is None:
            categorias = ", ".join(sorted(categorias_contexto.keys()))
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Categoría inválida para la sede '{sede}'. "
                    f"Categorías permitidas: {categorias}"
                ),
            )

        if context not in contextos_validos:
            contextos = ", ".join(sorted(contextos_validos))
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Contexto inválido para la categoría '{category}' en la sede '{sede}'. "
                    f"Contextos permitidos: {contextos}"
                ),
            )

    def _validar_categoria_contexto_administrativa(self, category: str | None, context: str | None) -> None:
        """Compatibilidad histórica: valida categoría/contexto de sede administrativa."""
        if category is None or context is None:
            return

        contextos_validos = CATEGORIAS_CONTEXTO_ADMINISTRATIVA.get(category)
        if contextos_validos is None:
            categorias = ", ".join(sorted(CATEGORIAS_CONTEXTO_ADMINISTRATIVA.keys()))
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Categoría inválida para sede administrativa. "
                    f"Categorías permitidas: {categorias}"
                ),
            )

        if context not in contextos_validos:
            contextos = ", ".join(sorted(contextos_validos))
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Contexto inválido para la categoría '{category}' en sede administrativa. "
                    f"Contextos permitidos: {contextos}"
                ),
            )

    def obtener_horarios_ocupados(self, db: Session, sede: str = SEDE_ASISTENCIA) -> RespuestaHorariosOcupados:
        """Lista horarios ocupados y su estado activo para una sede específica.

        CORRECCIÓN 3: Filtra citas cuyo scheduled_at ya pasó usando hora Colombia.
        """
        estados_activos = {"pendiente", "llamando", "en_atencion"}
        # CORRECCIÓN 3: Usar hora Colombia en lugar de UTC
        ahora_colombia = datetime.now(COLOMBIA_TZ).replace(tzinfo=None)
        filas = (
            db.query(Appointment.scheduled_at, Appointment.status, Appointment.attention_started_at, Appointment.extension_count)
            .filter(
                Appointment.sede == sede,
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
        sede: str = SEDE_ASISTENCIA,
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

        self._validar_fecha_agendada(db, payload.scheduled_at, sede=sede)
        self._validar_categoria_contexto_por_sede(sede, payload.category, payload.context)

        # CAMBIO: Usar hora de Colombia para obtener la fecha local correcta
        hoy = datetime.now(COLOMBIA_TZ).replace(tzinfo=None).date()
        print(f"[DEBUG] hoy Colombia: {hoy}", flush=True)

        ultimo_error: IntegrityError | None = None
        for _ in range(3):
            sec_turno = self.repositorio.siguiente_secuencia_turno(db, sede=sede, para_fecha=hoy)
            prefijo_turno = self._prefijo_turno_por_sede(sede)
            numero_turno = f"{prefijo_turno}-{hoy.strftime('%Y%m%d')}-{sec_turno:03d}"

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
                ultimo_error = exc
        raise HTTPException(status_code=409, detail="No se pudo crear la cita: conflicto de horario")

    def obtener_cola(
        self,
        db: Session,
        staff_email: str,
        staff_role: str,
    ) -> list[Appointment]:
        """Obtiene cola activa de la sede del staff autenticado."""
        sede = self._resolver_sede_por_rol(staff_role)
        secretaria = db.query(User).filter(User.email == staff_email).first()
        if not secretaria:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if staff_role == "secretaria" and not secretaria.programa_academico:
            raise HTTPException(status_code=403, detail="El usuario no tiene programa_academico asignado")

        programa_academico = secretaria.programa_academico if staff_role == "secretaria" else None

        return self.repositorio.obtener_cola(
            db,
            sede=sede,
            programa_academico=programa_academico,
        )

    def obtener_historial_cola(
        self,
        db: Session,
        staff_email: str,
        staff_role: str,
    ) -> list[AppointmentHistory]:
        """Obtiene historial de atención de la sede del staff autenticado."""
        sede = self._resolver_sede_por_rol(staff_role)
        secretaria = db.query(User).filter(User.email == staff_email).first()
        if not secretaria:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if staff_role == "secretaria" and not secretaria.programa_academico:
            raise HTTPException(status_code=403, detail="El usuario no tiene programa_academico asignado")

        secretaria_id = secretaria.id if staff_role == "secretaria" else None

        return self.repositorio.obtener_historial_cola(
            db,
            sede=sede,
            secretaria_id=secretaria_id,
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

        if requester_role in {"secretaria", "administrativo", "admisiones_mercadeo"}:
            sede_permitida = self._resolver_sede_por_rol(requester_role)
            if cita.sede != sede_permitida:
                raise HTTPException(status_code=403, detail="No puedes ver citas de otra sede")

        # Construir respuesta compatible para ambos casos
        detalle = {
            "id": cita.id,
            "student_id": cita.student_id,
            "device_id": cita.device_id,
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
                "programa_academico": getattr(estudiante, "programa_academico", None),
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

        if payload.category is None and payload.context is None and payload.scheduled_at is None:
            raise HTTPException(status_code=400, detail="Debes enviar al menos un campo para actualizar")

        categoria_objetivo = payload.category or cita.category
        contexto_objetivo = payload.context or cita.context
        self._validar_categoria_contexto_por_sede(cita.sede, categoria_objetivo, contexto_objetivo)

        self._validar_fecha_agendada(db, payload.scheduled_at, sede=cita.sede, excluir_cita_id=appointment_id)

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

    def iniciar_atencion(self, db: Session, appointment_id: int, staff_email: str, staff_role: str) -> Appointment:
        """Marca una cita como `en_atencion` por un miembro del staff autorizado."""
        cita = self.repositorio.obtener_por_id(db, appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        sede_permitida = self._resolver_sede_por_rol(staff_role)
        if cita.sede != sede_permitida:
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

    def extender_tiempo(self, db: Session, appointment_id: int, staff_email: str, staff_role: str) -> RespuestaExtenderTiempo:
        """Extiende 15 minutos la cita en atención y reajusta turnos siguientes en la misma sede."""
        cita = self.repositorio.obtener_por_id(db, appointment_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        sede_permitida = self._resolver_sede_por_rol(staff_role)
        if cita.sede != sede_permitida:
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
                Appointment.sede == cita.sede,
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

        if changed_by_role in {"secretaria", "administrativo", "admisiones_mercadeo"}:
            sede_permitida = self._resolver_sede_por_rol(changed_by_role)
            if cita.sede != sede_permitida:
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
                                Appointment.sede == cita.sede,
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
