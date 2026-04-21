from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, StringConstraints

class CrearStaff(BaseModel):
    user_id: int
    sede_id: int
    # cargo eliminado
    activo: bool = True

class ActualizarStaff(BaseModel):
    sede_id: int | None = None
    # cargo eliminado
    activo: bool | None = None

class RespuestaStaff(BaseModel):
    id: int
    user_id: int
    sede_id: int
    # cargo eliminado
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RespuestaStaffUsuario(BaseModel):
    """Respuesta de listado de staff con datos de usuario y asignación."""

    user_id: int
    email: str
    full_name: str
    programa_academico_id: int
    is_active: bool
    sede_id: int | None
    staff_activo: bool | None
