"""Utilidades de seguridad: hashing de contraseñas y generación de tokens JWT."""

from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import Response
from app.core.configuracion import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashear_contrasena(contrasena: str) -> str:
    """Hashea una contraseña de usuario con bcrypt respetando el límite de entrada."""
    contrasena = contrasena[:72]
    return pwd_context.hash(contrasena)

def verificar_contrasena(plana, hasheada):
    """Compara una contraseña en texto plano contra su hash almacenado."""
    return pwd_context.verify(plana, hasheada)

def crear_token_acceso(datos: dict, expiracion_delta: timedelta | None = None):
    """Genera un access token JWT con expiración corta para consumir la API."""
    a_codificar = datos.copy()
    expiracion = datetime.utcnow() + (expiracion_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    a_codificar.update({"exp": expiracion, "token_type": "access"})

    return jwt.encode(a_codificar, SECRET_KEY, algorithm=ALGORITHM)


def crear_token_refresco(datos: dict, expiracion_delta: timedelta | None = None):
    """Genera un refresh token JWT con `jti` para control de revocación."""
    a_codificar = datos.copy()
    expiracion = datetime.utcnow() + (expiracion_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    a_codificar.update({"exp": expiracion, "token_type": "refresh", "jti": uuid4().hex})

    return jwt.encode(a_codificar, SECRET_KEY, algorithm=ALGORITHM)


def crear_token_invitado(device_id: str) -> str:
    """JWT de 4 horas para modo invitado, sin refresh token."""
    carga = {
        "role": "guest",
        "device_id": device_id,
        "token_type": "access",
        "exp": datetime.utcnow() + timedelta(hours=4),
    }
    return jwt.encode(carga, SECRET_KEY, algorithm=ALGORITHM)


def configurar_cookie_refresh_token(
    response: Response,
    refresh_token: str,
    es_desarrollo: bool = False,
):
    """Configura cookie HttpOnly para refresh token con seguridad web."""
    max_age = int(timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,              # No accesible desde JavaScript
        secure=not es_desarrollo,   # Solo HTTPS en producción
        samesite="none" if not es_desarrollo else "lax",  # "none" en prod, "lax" en desarrollo
        max_age=max_age,
        path="/",                   # Disponible para toda la aplicación
    )


def eliminar_cookie_refresh_token(response: Response, es_desarrollo: bool = False):
    """Elimina la cookie de refresh token para cerrar sesión."""
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=not es_desarrollo,
        samesite="none" if not es_desarrollo else "lax",
    )