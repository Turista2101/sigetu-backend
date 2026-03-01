from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints


CategoryType = Literal["academico", "administrativo", "financiero", "otro"]
StatusType = Literal["pendiente", "llamando", "en_atencion", "atendido", "no_asistio", "cancelada"]


class AppointmentCreate(BaseModel):
    category: CategoryType
    context: Annotated[str, StringConstraints(min_length=2, max_length=120, strip_whitespace=True)]
    scheduled_at: datetime | None = None


class AppointmentUpdate(BaseModel):
    category: CategoryType | None = None
    context: Annotated[str, StringConstraints(min_length=2, max_length=120, strip_whitespace=True)] | None = None
    scheduled_at: datetime | None = None


class AppointmentStatusUpdate(BaseModel):
    status: StatusType


class AppointmentStudentInfo(BaseModel):
    id: int
    full_name: str
    email: str
    programa_academico: str | None = None


class AppointmentDetailResponse(BaseModel):
    id: int
    student_id: int
    turn_number: str
    sede: str
    category: CategoryType
    context: str
    status: StatusType
    created_at: datetime
    scheduled_at: datetime | None = None
    student: AppointmentStudentInfo


class AppointmentResponse(BaseModel):
    id: int
    student_id: int
    student_name: str | None = None
    sede: str
    category: CategoryType
    context: str
    status: StatusType
    turn_number: str
    created_at: datetime
    scheduled_at: datetime | None = None

    class Config:
        from_attributes = True


class AppointmentQueueItem(BaseModel):
    id: int
    student_name: str | None = None
    turn_number: str
    category: CategoryType
    context: str
    status: StatusType
    created_at: datetime
    scheduled_at: datetime | None = None

    class Config:
        from_attributes = True
