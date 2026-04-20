"""Esquemas Pydantic para CRUD de roles y asignacion de rol/sede a usuario."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints


class CrearRol(BaseModel):
    """Payload para crear un rol."""

    name: Annotated[str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)]


class ActualizarRol(BaseModel):
    """Payload parcial para actualizar un rol."""

    name: Annotated[str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)] | None = None


class RespuestaRol(BaseModel):
    """Representacion publica de rol."""

    id: int
    name: str

    class Config:
        from_attributes = True
