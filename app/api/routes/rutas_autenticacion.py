"""Endpoints HTTP para registro, login y manejo de tokens de autenticación."""

import os
from fastapi import APIRouter, Depends, Response, Cookie
from typing import Optional
from sqlalchemy.orm import Session

from app.schemas.esquema_usuarios import (
    RespuestaAuth,
    CrearUsuario,
    RespuestaCierreSesion,
    SolicitudRenovarToken,
    RespuestaRenovarToken,
    SolicitudLogin,
    RespuestaUsuario,
    SolicitudInvitado,
    RespuestaInvitado,
    SolicitudRefreshBody,
)
from app.core.dependencias_autenticacion import obtener_payload_token_actual
from app.models.modelo_usuario import User
from app.db.sesion import obtener_db
from app.services.servicio_autenticacion import ServicioAutenticacion
from app.core.seguridad import configurar_cookie_refresh_token, eliminar_cookie_refresh_token


router = APIRouter(prefix="/auth", tags=["Auth"])
servicio_auth = ServicioAutenticacion()


@router.post("/register", response_model=RespuestaAuth)
def registrar(
    response: Response,
    datos_usuario: CrearUsuario,
    device_id: str | None = None,
    db: Session = Depends(obtener_db)
):
    """Registra un usuario estudiante y devuelve perfil junto con tokens JWT."""
    resultado = servicio_auth.registrar(
        db=db,
        full_name=datos_usuario.full_name,
        email=datos_usuario.email,
        password=datos_usuario.password,
        programa_academico=datos_usuario.programa_academico,
        device_id=device_id,
    )
    # Configurar refresh token como cookie HttpOnly para web
    es_desarrollo = os.getenv("DEBUG", "False").lower() == "true"
    configurar_cookie_refresh_token(response, resultado["refresh_token"], es_desarrollo)
    return resultado


@router.post("/login", response_model=RespuestaAuth)
def iniciar_sesion(
    response: Response,
    datos_login: SolicitudLogin,
    db: Session = Depends(obtener_db)
):
    """Autentica credenciales de usuario y entrega access/refresh token."""
    resultado = servicio_auth.iniciar_sesion(
        db=db,
        email=datos_login.email,
        password=datos_login.password,
    )
    # Configurar refresh token como cookie HttpOnly para web
    es_desarrollo = os.getenv("DEBUG", "False").lower() == "true"
    configurar_cookie_refresh_token(response, resultado["refresh_token"], es_desarrollo)
    return resultado


@router.post("/guest", response_model=RespuestaInvitado)
def login_invitado(solicitud: SolicitudInvitado):
    """Genera token de acceso temporal para flujo de invitado."""
    return servicio_auth.login_invitado(device_id=solicitud.device_id)


@router.post("/refresh", response_model=RespuestaRenovarToken)
def renovar_token(
    response: Response,
    refresh_cookie: Optional[str] = Cookie(None, alias="refresh_token"),
    body: Optional[SolicitudRefreshBody] = None,
    db: Session = Depends(obtener_db),
):
    """Renueva par de tokens usando un refresh token válido (cookie para web, body para Android)."""
    # Priorizar cookie (web), fallback a body (Android)
    refresh_token = refresh_cookie or (body.refresh_token if body else None)
    
    if not refresh_token:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Refresh token requerido")
    
    resultado = servicio_auth.renovar(
        db=db,
        refresh_token=refresh_token,
    )
    # Rotar refresh token - configurar nueva cookie
    es_desarrollo = os.getenv("DEBUG", "False").lower() == "true"
    configurar_cookie_refresh_token(response, resultado["refresh_token"], es_desarrollo)
    return {"access_token": resultado["access_token"], "token_type": resultado["token_type"]}


@router.post("/logout", response_model=RespuestaCierreSesion)
def cerrar_sesion(
    response: Response,
    refresh_cookie: Optional[str] = Cookie(None, alias="refresh_token"),
    body: Optional[SolicitudRenovarToken] = None,
    db: Session = Depends(obtener_db),
):
    """Revoca refresh token para cerrar sesión del cliente (cookie para web, body para Android)."""
    # Obtener refresh token de cookie (web) o body (Android)
    refresh_token = refresh_cookie or (body.refresh_token if body else None)
    
    if not refresh_token:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Refresh token requerido")
    
    resultado = servicio_auth.cerrar_sesion(
        db=db,
        refresh_token=refresh_token,
    )
    # Eliminar cookie de refresh token
    es_desarrollo = os.getenv("DEBUG", "False").lower() == "true"
    eliminar_cookie_refresh_token(response, es_desarrollo)
    return resultado


@router.get("/me", response_model=RespuestaUsuario)
def obtener_mi_perfil(
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(obtener_payload_token_actual),
):
    """Retorna datos del usuario autenticado por token de acceso."""
    usuario = db.query(User).filter(User.email == carga_token["sub"]).first()
    if not usuario:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario