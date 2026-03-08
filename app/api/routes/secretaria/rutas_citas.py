from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencias_autenticacion import requerir_rol_secretaria_o_admin, requerir_rol_secretaria
from app.db.sesion import obtener_db
from app.schemas.esquema_citas import (
    RespuestaDetalleCita,
    ItemColaCita,
    RespuestaCita,
    ActualizarEstadoCita,
    RespuestaExtenderTiempo,
)
from app.services.servicio_citas import ServicioCitas

router = APIRouter(prefix="/appointments", tags=["Appointments"])
servicio = ServicioCitas()


@router.get("/queue", response_model=list[ItemColaCita])
def obtener_cola(
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_secretaria),
):
    return servicio.obtener_cola(db=db, secretaria_email=carga_token["sub"])


@router.get("/queue/history", response_model=list[ItemColaCita])
def obtener_historial_cola(
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_secretaria),
):
    return servicio.obtener_historial_cola(db=db, secretaria_email=carga_token["sub"])


@router.get("/{appointment_id}/detail", response_model=RespuestaDetalleCita)
def obtener_detalle_cita(
    appointment_id: int,
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_secretaria_o_admin),
):
    return servicio.obtener_detalle_cita(
        db=db,
        appointment_id=appointment_id,
        requester_email=carga_token["sub"],
        requester_role=carga_token["role"],
    )


@router.patch("/{appointment_id}/status", response_model=RespuestaCita)
def actualizar_estado(
    appointment_id: int,
    carga: ActualizarEstadoCita,
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_secretaria_o_admin),
):
    return servicio.actualizar_estado(
        db=db,
        appointment_id=appointment_id,
        new_status=carga.status,
        changed_by_email=carga_token["sub"],
    )


@router.post("/{appointment_id}/start-attention", response_model=RespuestaCita)
def iniciar_atencion(
    appointment_id: int,
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_secretaria),
):
    return servicio.iniciar_atencion(
        db=db,
        appointment_id=appointment_id,
        secretaria_email=carga_token["sub"],
    )


@router.post("/{appointment_id}/extend-time", response_model=RespuestaExtenderTiempo)
def extender_tiempo(
    appointment_id: int,
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_secretaria),
):
    return servicio.extender_tiempo(
        db=db,
        appointment_id=appointment_id,
        secretaria_email=carga_token["sub"],
    )
