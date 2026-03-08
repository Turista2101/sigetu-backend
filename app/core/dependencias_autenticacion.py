from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.configuracion import ALGORITHM, SECRET_KEY


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def obtener_payload_token_actual(token: str = Depends(oauth2_scheme)) -> dict:
    excepcion_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        carga = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise excepcion_credenciales from exc

    rol = carga.get("role")
    tipo_token = carga.get("token_type", "access")
    if not rol or tipo_token != "access":
        raise excepcion_credenciales

    # Tokens de usuario requieren sub; tokens de invitado usan device_id
    if rol != "guest" and not carga.get("sub"):
        raise excepcion_credenciales

    return carga


def requerir_rol_estudiante(carga: dict = Depends(obtener_payload_token_actual)) -> dict:
    if carga.get("role") != "estudiante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo estudiantes pueden agendar citas",
        )
    return carga


def requerir_rol_secretaria(carga: dict = Depends(obtener_payload_token_actual)) -> dict:
    if carga.get("role") != "secretaria":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo secretaría puede consultar la cola",
        )
    return carga


def requerir_rol_secretaria_o_admin(carga: dict = Depends(obtener_payload_token_actual)) -> dict:
    if carga.get("role") not in {"secretaria", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo secretaría o admin pueden actualizar estados",
        )
    return carga


def requerir_rol_invitado(carga: dict = Depends(obtener_payload_token_actual)) -> dict:
    if carga.get("role") != "guest":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso solo para invitados",
        )
    device_id = carga.get("device_id")
    if not device_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de invitado sin device_id",
        )
    return carga


def requerir_rol_estudiante_o_invitado(carga: dict = Depends(obtener_payload_token_actual)) -> dict:
    if carga.get("role") not in {"estudiante", "guest"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo estudiantes o invitados pueden realizar esta acción",
        )
    return carga
