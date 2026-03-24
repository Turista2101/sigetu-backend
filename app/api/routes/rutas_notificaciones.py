"""Endpoints para registrar tokens de notificaciones push (Firebase FCM)."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencias_autenticacion import obtener_payload_token_actual, requerir_rol_secretaria_o_admin
from app.db.sesion import obtener_db
from app.schemas.esquema_notificaciones import SolicitudRegistroTokenFCM, RespuestaRegistroTokenFCM
from app.services.servicio_notificaciones import ServicioNotificaciones

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])
servicio_notificaciones = ServicioNotificaciones()


class TokenInfo(BaseModel):
    """Información de un token FCM registrado."""
    device_id: str
    platform: str
    token: str


@router.get("/tokens", response_model=List[TokenInfo])
def obtener_tokens_usuario(
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(obtener_payload_token_actual),
):
    """Obtiene los tokens FCM registrados para el usuario autenticado."""
    from app.models.modelo_usuario import User
    
    usuario = db.query(User).filter(User.email == carga_token["sub"]).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Consulta directa
    from app.models.modelo_token_dispositivo_fcm import FCMDeviceToken
    registros = db.query(FCMDeviceToken).filter(FCMDeviceToken.user_id == usuario.id).all()
    
    logger.info(f"Usuario {usuario.email} tiene {len(registros)} token(s) registrado(s)")

    return [
        TokenInfo(
            device_id=r.device_id,
            platform=r.platform,
            token=r.token[:20] + "..." if len(r.token) > 20 else r.token,
        )
        for r in registros
    ]


@router.post("/device-token", response_model=RespuestaRegistroTokenFCM)
def registrar_token_dispositivo(
    payload: SolicitudRegistroTokenFCM,
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(obtener_payload_token_actual),
):
    """Registra/actualiza token FCM del usuario autenticado o invitado."""
    role = carga_token.get("role")
    logger.info(f"Registrando token FCM - role: {role}, device_id: {payload.device_id}, platform: {payload.platform}")
    
    if role == "guest":
        # Guardar token solo con device_id
        servicio_notificaciones.registrar_token_invitado(
            db=db,
            device_id=payload.device_id,
            fcm_token=payload.fcm_token,
            platform=payload.platform,
        )
        logger.info(f"Token FCM de invitado registrado: {payload.device_id}")
        return {"detail": "Token FCM de invitado registrado correctamente"}
    
    # Usuario autenticado normal
    servicio_notificaciones.registrar_token_usuario(
        db=db,
        user_email=carga_token["sub"],
        device_id=payload.device_id,
        fcm_token=payload.fcm_token,
        platform=payload.platform,
    )
    logger.info(f"Token FCM de usuario registrado: {carga_token['sub']}, device_id: {payload.device_id}")
    return {"detail": "Token FCM registrado correctamente"}
