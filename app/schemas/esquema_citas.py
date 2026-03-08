from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints


TipoCategoria = Literal["academico", "administrativo", "financiero", "otro"]
TipoEstado = Literal["pendiente", "llamando", "en_atencion", "atendido", "no_asistio", "cancelada"]


class CrearCita(BaseModel):
    category: TipoCategoria
    context: Annotated[str, StringConstraints(min_length=2, max_length=120, strip_whitespace=True)]
    scheduled_at: datetime | None = None


class ActualizarCita(BaseModel):
    category: TipoCategoria | None = None
    context: Annotated[str, StringConstraints(min_length=2, max_length=120, strip_whitespace=True)] | None = None
    scheduled_at: datetime | None = None


class ActualizarEstadoCita(BaseModel):
    status: TipoEstado


class InfoEstudianteCita(BaseModel):
    id: int
    full_name: str
    email: str
    programa_academico: str | None = None


class RespuestaDetalleCita(BaseModel):
    id: int
    student_id: int | None
    device_id: str | None = None
    turn_number: str
    sede: str
    category: TipoCategoria
    context: str
    status: TipoEstado
    created_at: datetime
    scheduled_at: datetime | None = None
    attention_started_at: datetime | None = None
    student: InfoEstudianteCita | None = None


class HorarioOcupado(BaseModel):
    scheduled_at: datetime
    status: TipoEstado
    attention_ends_at: datetime | None = None


class RespuestaHorariosOcupados(BaseModel):
    horarios: list[HorarioOcupado]


class RespuestaExtenderTiempo(BaseModel):
    mensaje: str
    citas_actualizadas: int


class RespuestaCita(BaseModel):
    id: int
    student_id: int | None = None
    device_id: str | None = None
    student_name: str | None = None
    sede: str
    category: TipoCategoria
    context: str
    status: TipoEstado
    turn_number: str
    created_at: datetime
    scheduled_at: datetime | None = None
    attention_started_at: datetime | None = None

    class Config:
        from_attributes = True


class ItemColaCita(BaseModel):
    id: int
    student_name: str | None = None
    secretaria_name: str | None = None
    turn_number: str
    category: TipoCategoria
    context: str
    status: TipoEstado
    created_at: datetime
    scheduled_at: datetime | None = None

    class Config:
        from_attributes = True
