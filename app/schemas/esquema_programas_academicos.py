"""Esquemas Pydantic para CRUD de programas academicos."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints


class CrearProgramaAcademico(BaseModel):
    """Payload para crear un programa academico."""

    codigo: Annotated[str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)]
    nombre: Annotated[str, StringConstraints(min_length=2, max_length=120, strip_whitespace=True)]
    descripcion: Annotated[str, StringConstraints(max_length=255, strip_whitespace=True)] | None = None
    activo: bool = True


class ActualizarProgramaAcademico(BaseModel):
    """Payload parcial para actualizar un programa academico."""

    codigo: Annotated[str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)] | None = None
    nombre: Annotated[str, StringConstraints(min_length=2, max_length=120, strip_whitespace=True)] | None = None
    descripcion: Annotated[str, StringConstraints(max_length=255, strip_whitespace=True)] | None = None
    activo: bool | None = None


class RespuestaProgramaAcademico(BaseModel):
    """Representacion publica de programa academico."""

    id: int
    codigo: str
    nombre: str
    descripcion: str | None
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
