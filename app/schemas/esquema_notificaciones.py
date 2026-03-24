"""Esquemas de entrada/salida para registro de tokens de notificaciones push."""

from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints


class SolicitudRegistroTokenFCM(BaseModel):
    """Payload para asociar un token FCM a un dispositivo del usuario."""
    device_id: Annotated[str, StringConstraints(min_length=8, max_length=128, strip_whitespace=True)]
    fcm_token: Annotated[str, StringConstraints(min_length=20, max_length=512, strip_whitespace=True)]
    platform: Literal["android", "ios", "web"]


class RespuestaRegistroTokenFCM(BaseModel):
    """Confirmación de registro exitoso del token FCM."""
    detail: str
