"""Esquemas Pydantic para autenticación y representación de usuarios."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated, Optional

class CrearUsuario(BaseModel):
    """Payload para registrar estudiantes en el sistema."""
    email: EmailStr
    full_name: Annotated[str, StringConstraints(min_length=3, max_length=50, strip_whitespace=True)]
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]
    programa_academico_id: int


class SolicitudLogin(BaseModel):
    """Credenciales mínimas para autenticación por contraseña."""
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=1, max_length=128)]

class RespuestaUsuario(BaseModel):
    """Estructura pública de usuario retornada por la API."""
    id: int
    email: EmailStr
    full_name: str
    programa_academico_id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class RespuestaAuth(BaseModel):
    """Respuesta estándar de login/registro con perfil y tokens."""
    user: RespuestaUsuario
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class SolicitudRenovarToken(BaseModel):
    """Payload para solicitar rotación de refresh token (Android)."""
    refresh_token: str


class SolicitudRefreshBody(BaseModel):
    """Payload opcional para refresh token desde body (Android)."""
    refresh_token: str | None = None


class RespuestaRenovarToken(BaseModel):
    """Respuesta de renovación de sesión con nuevo par de tokens."""
    access_token: str
    refresh_token:  Optional[str] = None
    token_type: str = "bearer"


class RespuestaCierreSesion(BaseModel):
    """Mensaje de confirmación de cierre de sesión."""
    detail: str


class SolicitudInvitado(BaseModel):
    """Payload de autenticación para flujo invitado por dispositivo."""
    device_id: Annotated[str, StringConstraints(
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        to_lower=True,
    )]


class RespuestaInvitado(BaseModel):
    """Respuesta de acceso temporal para invitados."""
    access_token: str
    token_type: str = "bearer"


class CrearUsuarioAdmin(BaseModel):
    """Payload de creación de usuario para panel administrativo."""

    email: EmailStr
    full_name: Annotated[str, StringConstraints(min_length=3, max_length=150, strip_whitespace=True)]
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]
    programa_academico_id: int
    role_id: int
    is_active: bool = True


class ActualizarUsuarioAdmin(BaseModel):
    """Payload parcial de actualización de usuario para panel administrativo."""

    email: EmailStr | None = None
    full_name: Annotated[str, StringConstraints(min_length=3, max_length=150, strip_whitespace=True)] | None = None
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)] | None = None
    programa_academico_id: int | None = None
    role_id: int | None = None
    is_active: bool | None = None


class RespuestaUsuarioAdmin(BaseModel):
    """Estructura pública extendida de usuario para administración."""

    id: int
    email: EmailStr
    full_name: str
    programa_academico_id: int
    role_id: int
    role_name: str
    is_active: bool
    created_at: datetime
