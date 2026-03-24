"""Servicio para registrar tokens FCM y enviar notificaciones push."""

from __future__ import annotations

import logging
import os

import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy.orm import Session

from app.core.configuracion import FIREBASE_SERVICE_ACCOUNT_PATH
from app.models.modelo_usuario import User
from app.repositories.repositorio_tokens_fcm import RepositorioTokensFCM

logger = logging.getLogger(__name__)


class ServicioNotificaciones:
    """Orquesta persistencia de tokens y envío de mensajes Firebase."""

    def __init__(self) -> None:
        self.repositorio = RepositorioTokensFCM()

    def _inicializar_firebase(self) -> bool:
        """Inicializa el SDK de Firebase si no existe una app activa."""
        if firebase_admin._apps:
            return True

        ruta = FIREBASE_SERVICE_ACCOUNT_PATH
        if not os.path.exists(ruta):
            return False

        credencial = credentials.Certificate(ruta)
        firebase_admin.initialize_app(credencial)
        return True

    def registrar_token_usuario(
        self,
        db: Session,
        user_email: str,
        device_id: str,
        fcm_token: str,
        platform: str,
    ) -> None:
        """Registra o actualiza token FCM para el usuario autenticado."""
        usuario_id = db.query(User.id).filter(User.email == user_email).scalar()
        if usuario_id is None:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        logger.info(f"Registrando token - user_id: {usuario_id}, device_id: {device_id}, token: {fcm_token[:20] if len(fcm_token) > 20 else fcm_token}..., platform: {platform}")
        
        if not fcm_token or len(fcm_token) < 50:
            logger.warning(f"Token FCM sospechosamente corto o vacío: {fcm_token}")
        
        self.repositorio.registrar_o_actualizar(
            db=db,
            user_id=int(usuario_id),
            device_id=device_id,
            token=fcm_token,
            platform=platform,
        )
        logger.info(f"Token registrado exitosamente para usuario {user_email}")

    def registrar_token_invitado(
        self,
        db: Session,
        device_id: str,
        fcm_token: str,
        platform: str,
    ) -> None:
        """Registra o actualiza token FCM para un invitado (sin user_id)."""
        self.repositorio.registrar_o_actualizar_invitado(
            db=db,
            device_id=device_id,
            token=fcm_token,
            platform=platform,
        )

    def notificar_estado_cita(
        self,
        db: Session,
        user_id: int | None,
        nuevo_estado: str,
        turno: str,
    ) -> None:
        """Envía push al estudiante cuando cambia el estado de su cita."""
        if user_id is None:
            logger.warning("user_id es None, no se envía notificación")
            return

        if not self._inicializar_firebase():
            logger.warning("Firebase no está inicializado")
            return

        tokens = self.repositorio.listar_tokens_por_usuario(db=db, user_id=user_id)
        logger.info(f"Enviando notificación al usuario {user_id}: {len(tokens)} token(s) encontrado(s)")
        
        if not tokens:
            logger.warning(f"Usuario {user_id} no tiene tokens FCM registrados")
            return

        titulo = "Actualización de tu cita"
        cuerpo = f"Tu turno {turno} cambió a estado: {nuevo_estado}"
        
        logger.info(f"Notificación - Título: {titulo}, Cuerpo: {cuerpo}")

        for token in tokens:
            try:
                logger.debug(f"Enviando a token: {token[:20]}...")
                mensaje = messaging.Message(
                    token=token,
                    notification=messaging.Notification(title=titulo, body=cuerpo),
                    data={
                        "event": "appointment_status_changed",
                        "status": nuevo_estado,
                        "turn_number": turno,
                    },
                )
                response = messaging.send(mensaje)
                logger.info(f"Notificación enviada exitosamente: {response}")
            except Exception as exc:
                detalle = str(exc)
                logger.error(f"Error al enviar notificación: {detalle}")
                if "registration-token-not-registered" in detalle or "Requested entity was not found" in detalle:
                    self.repositorio.eliminar_por_token(db=db, token=token)
                    logger.info(f"Token eliminado por ser inválido: {token[:20]}...")

    def notificar_estado_cita_invitado(
        self,
        db: Session,
        device_id: str,
        nuevo_estado: str,
        turno: str,
    ) -> None:
        """Envía push a un invitado (por device_id) cuando cambia el estado de su cita."""
        if not device_id:
            logger.warning("device_id no proporcionado")
            return
        if not self._inicializar_firebase():
            logger.warning("Firebase no está inicializado")
            return
        tokens = self.repositorio.listar_tokens_por_device(db=db, device_id=device_id)
        logger.info(f"Enviando notificación al invitado {device_id}: {len(tokens)} token(s) encontrado(s)")
        
        if not tokens:
            logger.warning(f"Invitado {device_id} no tiene tokens FCM registrados")
            return
        titulo = "Actualización de tu cita"
        cuerpo = f"Tu turno {turno} cambió a estado: {nuevo_estado}"
        for token in tokens:
            try:
                mensaje = messaging.Message(
                    token=token,
                    notification=messaging.Notification(title=titulo, body=cuerpo),
                    data={
                        "event": "appointment_status_changed",
                        "status": nuevo_estado,
                        "turn_number": turno,
                    },
                )
                response = messaging.send(mensaje)
                logger.info(f"Notificación enviada exitosamente: {response}")
            except Exception as exc:
                detalle = str(exc)
                logger.error(f"Error al enviar notificación a invitado: {detalle}")
                if "registration-token-not-registered" in detalle or "Requested entity was not found" in detalle:
                    self.repositorio.eliminar_por_token(db=db, token=token)
                    logger.info(f"Token eliminado por ser inválido: {token[:20]}...")

    def notificar_estado_cita_staff(
        self,
        db: Session,
        user_id: int,
        nuevo_estado: str,
        turno: str,
        accion: str = "Actualización",
    ) -> None:
        """Envía push al staff cuando realiza un cambio de estado en una cita."""
        if not self._inicializar_firebase():
            logger.warning("Firebase no está inicializado")
            return

        tokens = self.repositorio.listar_tokens_por_usuario(db=db, user_id=user_id)
        logger.info(f"Enviando notificación al staff {user_id}: {len(tokens)} token(s) encontrado(s)")
        
        if not tokens:
            logger.warning(f"Staff {user_id} no tiene tokens FCM registrados")
            return

        titulo = f"{accion} - Turno {turno}"
        cuerpo = f"Cita actualizada a estado: {nuevo_estado}"
        
        logger.info(f"Notificación staff - Título: {titulo}, Cuerpo: {cuerpo}")

        for token in tokens:
            try:
                logger.debug(f"Enviando a token: {token[:20]}...")
                mensaje = messaging.Message(
                    token=token,
                    notification=messaging.Notification(title=titulo, body=cuerpo),
                    data={
                        "event": "appointment_staff_action",
                        "status": nuevo_estado,
                        "turn_number": turno,
                        "action": accion,
                    },
                )
                response = messaging.send(mensaje)
                logger.info(f"Notificación staff enviada exitosamente: {response}")
            except Exception as exc:
                detalle = str(exc)
                logger.error(f"Error al enviar notificación al staff: {detalle}")
                if "registration-token-not-registered" in detalle or "Requested entity was not found" in detalle:
                    self.repositorio.eliminar_por_token(db=db, token=token)
                    logger.info(f"Token eliminado por ser inválido: {token[:20]}...")

    def notificar_extension_tiempo(
        self,
        db: Session,
        turno: str,
        nuevo_horario: str,
        user_id: int | None = None,
        device_id: str | None = None,
    ) -> None:
        """Notifica al estudiante o invitado que su cita fue reprogramada por extensión de atención."""
        if not self._inicializar_firebase():
            logger.warning("Firebase no está inicializado")
            return

        titulo = "Tu cita fue reprogramada"
        cuerpo = f"Tu turno {turno} se movió a las {nuevo_horario} por extensión de atención"

        if user_id is not None:
            tokens = self.repositorio.listar_tokens_por_usuario(db=db, user_id=user_id)
        elif device_id is not None:
            tokens = self.repositorio.listar_tokens_por_device(db=db, device_id=device_id)
        else:
            return

        if not tokens:
            return

        for token in tokens:
            try:
                mensaje = messaging.Message(
                    token=token,
                    notification=messaging.Notification(title=titulo, body=cuerpo),
                    data={
                        "event": "appointment_rescheduled",
                        "turn_number": turno,
                        "new_time": nuevo_horario,
                    },
                )
                response = messaging.send(mensaje)
                logger.info(f"Notificación extensión enviada: {response}")
            except Exception as exc:
                detalle = str(exc)
                logger.error(f"Error al enviar notificación de extensión: {detalle}")
                if "registration-token-not-registered" in detalle or "Requested entity was not found" in detalle:
                    self.repositorio.eliminar_por_token(db=db, token=token)
