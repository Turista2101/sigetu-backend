from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from uuid import uuid4
from app.core.configuracion import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashear_contrasena(contrasena: str) -> str:
    contrasena = contrasena[:72]
    return pwd_context.hash(contrasena)

def verificar_contrasena(plana, hasheada):
    return pwd_context.verify(plana, hasheada)

def crear_token_acceso(datos: dict, expiracion_delta: timedelta | None = None):
    a_codificar = datos.copy()
    expiracion = datetime.utcnow() + (expiracion_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    a_codificar.update({"exp": expiracion, "token_type": "access"})

    return jwt.encode(a_codificar, SECRET_KEY, algorithm=ALGORITHM)


def crear_token_refresco(datos: dict, expiracion_delta: timedelta | None = None):
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