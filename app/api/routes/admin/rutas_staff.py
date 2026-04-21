from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencias_autenticacion import requerir_rol_admin
from app.db.sesion import obtener_db
from app.schemas.esquema_staff import ActualizarStaff, CrearStaff, RespuestaStaff, RespuestaStaffUsuario
from app.services.servicio_staff import ServicioStaff

router = APIRouter(prefix="/staff", tags=["Staff"])
servicio = ServicioStaff()


@router.post("", response_model=RespuestaStaff, status_code=201)
def crear_staff(
    payload: CrearStaff,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Crea una asignación staff (usuario staff + sede)."""
    return servicio.crear_staff(db=db, payload=payload)


@router.patch("/{user_id}", response_model=RespuestaStaff)
def actualizar_staff(
    user_id: int,
    payload: ActualizarStaff,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Actualiza asignación staff por user_id (sede y/o estado)."""
    return servicio.actualizar_staff(db=db, user_id=user_id, payload=payload)


@router.delete("/{user_id}", status_code=204)
def eliminar_staff(
    user_id: int,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Elimina asignación staff por user_id."""
    servicio.eliminar_staff(db=db, user_id=user_id)
    return None

@router.get("", response_model=list[RespuestaStaffUsuario])
def listar_staff(
    sin_sede: bool = Query(False, description="Si es true, retorna solo staff sin sede asignada"),
    sede_id: int | None = Query(None, description="Filtra staff por sede asignada"),
    activo: bool | None = Query(None, description="Filtra por estado activo de la asignación staff"),
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Lista staff con filtros opcionales por sede y estado de asignación."""
    return servicio.listar_staff(db=db, sin_sede=sin_sede, sede_id=sede_id, activo=activo)
