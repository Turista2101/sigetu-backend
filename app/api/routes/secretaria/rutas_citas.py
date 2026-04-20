"""Endpoints de gestión de cola para staff por sede."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencias_autenticacion import requerir_rol_staff
from app.db.sesion import obtener_db
from app.schemas.esquema_citas import (
    ActualizarEstadoCita,
    ItemColaCita,
    ItemHistorialCita,
    RespuestaCita,
    RespuestaDetalleCita,
    RespuestaExtenderTiempo,
)
from app.services.servicio_citas import ServicioCitas


router = APIRouter(prefix="/appointments", tags=["Appointments"])
servicio = ServicioCitas()


@router.get("/queue", response_model=list[ItemColaCita])
def obtener_cola(
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_staff),
):
    """Obtiene cola activa de la sede asignada al usuario staff autenticado."""
    return servicio.obtener_cola(
        db=db,
        staff_email=carga_token["sub"],
    )


@router.get("/queue/history", response_model=list[ItemColaCita])
def obtener_historial_cola(
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_staff),
):
    """Obtiene historial de cola de la sede asignada al usuario staff autenticado."""
    return servicio.obtener_historial_cola(
        db=db,
        staff_email=carga_token["sub"],
    )


@router.get("/my-history", response_model=list[ItemHistorialCita])
def obtener_mi_historial(
    sede: Optional[str] = Query(None, description="Filtrar por sede"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha de inicio (ISO 8601)"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha fin (ISO 8601)"),
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_staff),
):
    """Obtiene historial de citas atendidas por el usuario staff autenticado."""
    return servicio.obtener_historial_secretaria(
        db=db,
        secretaria_email=carga_token["sub"],
        sede=sede,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


@router.get("/{appointment_id}/detail", response_model=RespuestaDetalleCita)
def obtener_detalle_cita(
    appointment_id: int,
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_staff),
):
    """Devuelve detalle ampliado de cita para gestión operativa."""
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
    carga_token: dict = Depends(requerir_rol_staff),
):
    """Actualiza el estado de una cita según el flujo permitido de transiciones."""
    return servicio.actualizar_estado(
        db=db,
        appointment_id=appointment_id,
        new_status=carga.status,
        changed_by_email=carga_token["sub"],
        changed_by_role=carga_token["role"],
    )


@router.post("/{appointment_id}/start-attention", response_model=RespuestaCita)
def iniciar_atencion(
    appointment_id: int,
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_staff),
):
    """Inicia atención de una cita previamente llamada por el staff."""
    return servicio.iniciar_atencion(
        db=db,
        appointment_id=appointment_id,
        staff_email=carga_token["sub"],
    )


@router.post("/{appointment_id}/extend-time", response_model=RespuestaExtenderTiempo)
def extender_tiempo(
    appointment_id: int,
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_staff),
):
    """Extiende tiempo de atención y reajusta agenda de la sede."""
    return servicio.extender_tiempo(
        db=db,
        appointment_id=appointment_id,
        staff_email=carga_token["sub"],
    )
