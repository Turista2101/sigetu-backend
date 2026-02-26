from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_dependencies import require_secretaria_or_admin_role, require_secretaria_role
from app.db.session import get_db
from app.schemas.appointment_schema import AppointmentQueueItem, AppointmentResponse, AppointmentStatusUpdate
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointments"])
service = AppointmentService()


@router.get("/queue", response_model=list[AppointmentQueueItem])
def get_queue(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(require_secretaria_role),
):
    return service.get_queue(db=db, secretaria_email=token_payload["sub"])


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
def update_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(require_secretaria_or_admin_role),
):
    return service.update_status(db=db, appointment_id=appointment_id, new_status=payload.status)
