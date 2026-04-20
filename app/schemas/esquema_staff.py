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
