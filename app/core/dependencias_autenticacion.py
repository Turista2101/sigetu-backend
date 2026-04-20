"""Dependencias FastAPI para validar token JWT y permisos por rol."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.configuracion import ALGORITHM, SECRET_KEY


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def obtener_payload_token_actual(token: str = Depends(oauth2_scheme)) -> dict:
    """Decodifica y valida el access token vigente del request actual."""
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
    """Restringe el endpoint a usuarios con rol estudiante."""
    if carga.get("role") != "estudiante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo estudiantes pueden agendar citas",
        )
    return carga


def requerir_rol_secretaria(carga: dict = Depends(obtener_payload_token_actual)) -> dict:
    """Restringe el endpoint a usuarios con rol secretaría."""
    if carga.get("role") != "secretaria":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo secretaría puede consultar la cola",
        )
    return carga


def requerir_rol_secretaria_o_administrativo(carga: dict = Depends(obtener_payload_token_actual)) -> dict:
    """Permite acceso a roles operativos de gestión de cola por sede."""
    if carga.get("role") not in {"secretaria", "administrativo", "admisiones_mercadeo"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo secretaría, administrativo o admisiones_mercadeo pueden consultar la cola",
        )
    return carga


def requerir_rol_secretaria_o_admin(carga: dict = Depends(obtener_payload_token_actual)) -> dict:
    """Permite actualizar estados a staff de sede y al rol admin."""
    if carga.get("role") not in {"secretaria", "administrativo", "admisiones_mercadeo", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo secretaría, administrativo, admisiones_mercadeo o admin pueden actualizar estados",
        )
    return carga


def requerir_rol_staff(carga: dict = Depends(obtener_payload_token_actual)) -> dict:
    """Permite acceso a cualquier rol interno que no sea estudiante o invitado."""
    if carga.get("role") in {"estudiante", "guest"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo staff puede acceder a esta acción",
        )
    return carga


def requerir_rol_admin(carga: dict = Depends(obtener_payload_token_actual)) -> dict:
    """Restringe el endpoint a usuarios con rol admin."""
    if carga.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin puede gestionar programas academicos",
        )
    return carga


def requerir_rol_invitado(carga: dict = Depends(obtener_payload_token_actual)) -> dict:
    """Valida que el token pertenezca al flujo de usuario invitado."""
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
    """Permite operaciones abiertas a estudiantes autenticados o invitados."""
    if carga.get("role") not in {"estudiante", "guest"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo estudiantes o invitados pueden realizar esta acción",
        )
    return carga
