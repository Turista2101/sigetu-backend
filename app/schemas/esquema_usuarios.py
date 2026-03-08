from typing import Annotated, Literal
from datetime import datetime
from pydantic import BaseModel, EmailStr, StringConstraints

class CrearUsuario(BaseModel):
    email: EmailStr
    full_name: Annotated[str, StringConstraints(min_length=3, max_length=50, strip_whitespace=True)]
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]
    programa_academico: Literal["ingenierias", "derecho", "finanzas"] | None = None


class SolicitudLogin(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=1, max_length=128)]

class RespuestaUsuario(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    programa_academico: Literal["ingenierias", "derecho", "finanzas"] | None
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class RespuestaAuth(BaseModel):
    user: RespuestaUsuario
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class SolicitudRenovarToken(BaseModel):
    refresh_token: str


class RespuestaRenovarToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RespuestaCierreSesion(BaseModel):
    detail: str


class SolicitudInvitado(BaseModel):
    device_id: Annotated[str, StringConstraints(
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        to_lower=True,
    )]


class RespuestaInvitado(BaseModel):
    access_token: str
    token_type: str = "bearer"