from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_dependencies import require_secretaria_or_admin_role, require_secretaria_role
from app.db.session import get_db
from app.schemas.appointment_schema import (
    AppointmentDetailResponse,
    AppointmentQueueItem,
    AppointmentResponse,
    AppointmentStatusUpdate,
)
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointments"])
service = AppointmentService()


@router.get("/queue", response_model=list[AppointmentQueueItem])
def get_queue(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(require_secretaria_role),
):
    return service.get_queue(db=db, secretaria_email=token_payload["sub"])


@router.get("/queue/history", response_model=list[AppointmentQueueItem])
def get_queue_history(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(require_secretaria_role),
):
    return service.get_queue_history(db=db, secretaria_email=token_payload["sub"])


@router.get("/{appointment_id}/detail", response_model=AppointmentDetailResponse)
def get_appointment_detail(
    appointment_id: int,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(require_secretaria_or_admin_role),
):
    return service.get_appointment_detail(
        db=db,
        appointment_id=appointment_id,
        requester_email=token_payload["sub"],
        requester_role=token_payload["role"],
    )


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
def update_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(require_secretaria_or_admin_role),
):
    return service.update_status(
        db=db,
        appointment_id=appointment_id,
        new_status=payload.status,
        changed_by_email=token_payload["sub"],
    )
