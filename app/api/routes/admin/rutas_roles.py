"""Endpoints CRUD para roles."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencias_autenticacion import requerir_rol_admin
from app.db.sesion import obtener_db
from app.schemas.esquema_roles import (
    ActualizarRol,
    CrearRol,
    RespuestaRol,
)
from app.services.servicio_roles import ServicioRoles


router = APIRouter(prefix="/roles", tags=["Roles"])
servicio = ServicioRoles()


@router.get("", response_model=list[RespuestaRol])
def listar_roles(
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Lista todos los roles disponibles."""
    return servicio.listar(db=db)


@router.get("/{role_id}", response_model=RespuestaRol)
def obtener_rol(
    role_id: int,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Obtiene un rol por su identificador."""
    return servicio.obtener(db=db, role_id=role_id)


@router.post("", response_model=RespuestaRol, status_code=201)
def crear_rol(
    payload: CrearRol,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Crea un rol nuevo en el catalogo."""
    return servicio.crear(db=db, payload=payload)


@router.patch("/{role_id}", response_model=RespuestaRol)
def actualizar_rol(
    role_id: int,
    payload: ActualizarRol,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Actualiza un rol existente."""
    return servicio.actualizar(db=db, role_id=role_id, payload=payload)


@router.delete("/{role_id}", status_code=204)
def eliminar_rol(
    role_id: int,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Elimina un rol sin usuarios asociados."""
    servicio.eliminar(db=db, role_id=role_id)
    return None
