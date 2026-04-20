"""Esquemas Pydantic para catalogos de contextos, categorias y sedes."""

from datetime import datetime, time
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


class CrearContexto(BaseModel):
    """Payload para crear un contexto."""

    categoria_id: int
    codigo: Annotated[str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)]
    nombre: Annotated[str, StringConstraints(min_length=2, max_length=120, strip_whitespace=True)]
    descripcion: Annotated[str, StringConstraints(max_length=255, strip_whitespace=True)] | None = None
    activo: bool = True


class ActualizarContexto(BaseModel):
    """Payload parcial para actualizar contexto."""

    categoria_id: int | None = None
    codigo: Annotated[str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)] | None = None
    nombre: Annotated[str, StringConstraints(min_length=2, max_length=120, strip_whitespace=True)] | None = None
    descripcion: Annotated[str, StringConstraints(max_length=255, strip_whitespace=True)] | None = None
    activo: bool | None = None


class RespuestaContexto(BaseModel):
    """Representacion publica de un contexto."""

    id: int
    categoria_id: int
    codigo: str
    nombre: str
    descripcion: str | None
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CrearCategoria(BaseModel):
    """Payload para crear una categoria asociada a contexto."""

    sede_id: int
    codigo: Annotated[str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)]
    nombre: Annotated[str, StringConstraints(min_length=2, max_length=120, strip_whitespace=True)]
    descripcion: Annotated[str, StringConstraints(max_length=255, strip_whitespace=True)] | None = None
    activo: bool = True


class ActualizarCategoria(BaseModel):
    """Payload parcial para actualizar categoria."""

    sede_id: int | None = None
    codigo: Annotated[str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)] | None = None
    nombre: Annotated[str, StringConstraints(min_length=2, max_length=120, strip_whitespace=True)] | None = None
    descripcion: Annotated[str, StringConstraints(max_length=255, strip_whitespace=True)] | None = None
    activo: bool | None = None


class RespuestaCategoria(BaseModel):
    """Representacion publica de una categoria."""

    id: int
    sede_id: int
    codigo: str
    nombre: str
    descripcion: str | None
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CrearSede(BaseModel):
    """Payload para crear una sede asociada a categoria."""

    codigo: Annotated[str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)]
    nombre: Annotated[str, StringConstraints(min_length=2, max_length=120, strip_whitespace=True)]
    ubicacion: Annotated[str, StringConstraints(min_length=1, max_length=255, strip_whitespace=True)]
    descripcion: Annotated[str, StringConstraints(max_length=255, strip_whitespace=True)] | None = None
    es_publica: bool
    filtrar_citas_por_programa: bool
    activo: bool


class ActualizarSede(BaseModel):
    """Payload parcial para actualizar sede."""

    codigo: Annotated[str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)] | None = None
    nombre: Annotated[str, StringConstraints(min_length=2, max_length=120, strip_whitespace=True)] | None = None
    ubicacion: Annotated[str, StringConstraints(max_length=255, strip_whitespace=True)] | None = None
    descripcion: Annotated[str, StringConstraints(max_length=255, strip_whitespace=True)] | None = None
    es_publica: bool | None = None
    filtrar_citas_por_programa: bool | None = None
    activo: bool | None = None


class RespuestaSede(BaseModel):
    """Representacion publica de una sede."""

    id: int
    codigo: str
    nombre: str
    ubicacion: str | None
    descripcion: str | None
    es_publica: bool
    filtrar_citas_por_programa: bool
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CrearHorarioSede(BaseModel):
    """Payload para crear un bloque de horario de atención en una sede."""

    dia_semana: int = Field(ge=0, le=6)
    hora_inicio: time
    hora_fin: time
    activo: bool = True


class ActualizarHorarioSede(BaseModel):
    """Payload parcial para actualizar un bloque de horario en sede."""

    dia_semana: int | None = Field(default=None, ge=0, le=6)
    hora_inicio: time | None = None
    hora_fin: time | None = None
    activo: bool | None = None


class RespuestaHorarioSede(BaseModel):
    """Representación pública de un bloque de horario de sede."""

    id: int
    sede_id: int
    dia_semana: int
    hora_inicio: time
    hora_fin: time
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
