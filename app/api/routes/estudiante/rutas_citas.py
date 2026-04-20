"""Endpoints de citas para estudiantes e invitados."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.dependencias_autenticacion import requerir_rol_estudiante, requerir_rol_invitado, requerir_rol_estudiante_o_invitado
from app.db.sesion import obtener_db
from app.schemas.esquema_citas import CrearCita, RespuestaCita, ActualizarCita, RespuestaHorariosOcupados
from app.services.servicio_citas import ServicioCitas

router = APIRouter(prefix="/appointments", tags=["Appointments"])
servicio = ServicioCitas()

@router.get("/horarios-ocupados", response_model=RespuestaHorariosOcupados)
def obtener_horarios_ocupados(
    contexto_id: int = Query(..., description="Id del contexto"),
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_estudiante_o_invitado),
):
    """Retorna franjas de horario ocupadas para el contexto seleccionado."""
    return servicio.obtener_horarios_ocupados(db=db, contexto_id=contexto_id)


@router.get("/guest", response_model=list[RespuestaCita])
def obtener_citas_invitado(
    device_id: str = Query(..., description="UUID v4 del dispositivo invitado"),
    carga_token: dict = Depends(requerir_rol_invitado),
    db: Session = Depends(obtener_db),
):
    """Lista citas del dispositivo invitado autenticado."""
    if carga_token.get("device_id") != device_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes consultar citas de otro dispositivo")
    return servicio.obtener_citas_invitado(db=db, device_id=device_id)


@router.get("/guest/history", response_model=list[RespuestaCita])
def obtener_historial_invitado(
    device_id: str = Query(..., description="UUID v4 del dispositivo invitado"),
    carga_token: dict = Depends(requerir_rol_invitado),
    db: Session = Depends(obtener_db),
):
    """Retorna historial de citas finalizadas/canceladas del invitado."""
    if carga_token.get("device_id") != device_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes consultar el historial de otro dispositivo")
    return servicio.obtener_historial_invitado(db=db, device_id=device_id)


@router.post("", response_model=RespuestaCita)
def crear_cita(
    carga: CrearCita,
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_estudiante_o_invitado),
):
    """Crea una cita en la sede indicada para estudiante o invitado."""
    if carga_token.get("role") == "guest":
        return servicio.crear_cita(
            db=db,
            payload=carga,
            device_id=carga_token["device_id"],
        )
    return servicio.crear_cita(
        db=db,
        payload=carga,
        student_email=carga_token["sub"],
    )


@router.get("/me", response_model=list[RespuestaCita])
def obtener_mis_citas(
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_estudiante),
):
    """Retorna todas las citas activas del estudiante autenticado."""
    return servicio.obtener_citas_estudiante(db=db, student_email=carga_token["sub"])


@router.get("/me/current", response_model=list[RespuestaCita])
def obtener_mis_citas_actuales(
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_estudiante),
):
    """Retorna solo citas en estados activos del estudiante."""
    return servicio.obtener_citas_actuales_estudiante(db=db, student_email=carga_token["sub"])


@router.get("/me/history", response_model=list[RespuestaCita])
def obtener_mi_historial(
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_estudiante),
):
    """Retorna historial de citas finalizadas/canceladas del estudiante."""
    return servicio.obtener_historial_citas_estudiante(db=db, student_email=carga_token["sub"])


@router.patch("/{appointment_id}", response_model=RespuestaCita)
def actualizar_mi_cita(
    appointment_id: int,
    carga: ActualizarCita,
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_estudiante),
):
    """Permite actualizar datos de una cita pendiente del estudiante."""
    return servicio.actualizar_cita_estudiante(
        db=db,
        appointment_id=appointment_id,
        payload=carga,
        student_email=carga_token["sub"],
    )


@router.patch("/{appointment_id}/cancel", response_model=RespuestaCita)
def cancelar_mi_cita(
    appointment_id: int,
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_estudiante),
):
    """Cancela una cita pendiente del estudiante autenticado."""
    return servicio.cancelar_cita_estudiante(
        db=db,
        appointment_id=appointment_id,
        student_email=carga_token["sub"],
    )


@router.patch("/guest/{appointment_id}", response_model=RespuestaCita)
def actualizar_cita_invitado(
    appointment_id: int,
    carga: ActualizarCita,
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_invitado),
):
    """Permite actualizar datos de una cita pendiente del invitado autenticado."""
    return servicio.actualizar_cita_invitado(
        db=db,
        appointment_id=appointment_id,
        payload=carga,
        device_id=carga_token["device_id"],
    )


@router.patch("/guest/{appointment_id}/cancel", response_model=RespuestaCita)
def cancelar_cita_invitado(
    appointment_id: int,
    db: Session = Depends(obtener_db),
    carga_token: dict = Depends(requerir_rol_invitado),
):
    """Cancela una cita pendiente del invitado autenticado."""
    return servicio.cancelar_cita_invitado(
        db=db,
        appointment_id=appointment_id,
        device_id=carga_token["device_id"],
    )
