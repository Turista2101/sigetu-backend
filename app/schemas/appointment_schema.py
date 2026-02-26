from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints


CategoryType = Literal["academico", "administrativo", "financiero", "otro"]
StatusType = Literal["pendiente", "llamando", "en_atencion", "finalizada", "cancelada"]


class AppointmentCreate(BaseModel):
    category: CategoryType
    context: Annotated[str, StringConstraints(min_length=2, max_length=120, strip_whitespace=True)]
    scheduled_at: datetime | None = None


class AppointmentStatusUpdate(BaseModel):
    status: StatusType


class AppointmentResponse(BaseModel):
    id: int
    student_id: int
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
    turn_number: str
    category: CategoryType
    context: str
    status: StatusType
    created_at: datetime

    class Config:
        from_attributes = True
