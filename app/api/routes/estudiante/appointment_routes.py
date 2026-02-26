from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_dependencies import require_student_role
from app.db.session import get_db
from app.schemas.appointment_schema import AppointmentCreate, AppointmentResponse
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointments"])
service = AppointmentService()


@router.post("", response_model=AppointmentResponse)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(require_student_role),
):
    return service.create_appointment(db=db, payload=payload, student_email=token_payload["sub"])


@router.get("/me", response_model=list[AppointmentResponse])
def get_my_appointments(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(require_student_role),
):
    return service.get_student_appointments(db=db, student_email=token_payload["sub"])
