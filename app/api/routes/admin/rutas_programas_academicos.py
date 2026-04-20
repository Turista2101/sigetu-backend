"""Endpoints CRUD para gestion de programas academicos."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencias_autenticacion import requerir_rol_admin
from app.db.sesion import obtener_db
from app.schemas.esquema_programas_academicos import (
    ActualizarProgramaAcademico,
    CrearProgramaAcademico,
    RespuestaProgramaAcademico,
)
from app.services.servicio_programas_academicos import ServicioProgramasAcademicos


router = APIRouter(prefix="/programas-academicos", tags=["Programas Academicos"])
servicio = ServicioProgramasAcademicos()


@router.get("", response_model=list[RespuestaProgramaAcademico])
def listar_programas_academicos(
    activos: bool | None = Query(None, description="Filtra por estado activo/inactivo"),
    db: Session = Depends(obtener_db),
):
    """Lista programas academicos, opcionalmente filtrados por estado activo."""
    return servicio.listar(db=db, solo_activos=activos)


@router.get("/{programa_id}", response_model=RespuestaProgramaAcademico)
def obtener_programa_academico(
    programa_id: int,
    db: Session = Depends(obtener_db),
):
    """Obtiene un programa academico por su identificador."""
    return servicio.obtener(db=db, programa_id=programa_id)


@router.post("", response_model=RespuestaProgramaAcademico, status_code=201)
def crear_programa_academico(
    payload: CrearProgramaAcademico,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Crea un programa academico nuevo en el catalogo."""
    return servicio.crear(db=db, payload=payload)


@router.patch("/{programa_id}", response_model=RespuestaProgramaAcademico)
def actualizar_programa_academico(
    programa_id: int,
    payload: ActualizarProgramaAcademico,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Actualiza campos de un programa academico existente."""
    return servicio.actualizar(db=db, programa_id=programa_id, payload=payload)


@router.delete("/{programa_id}", status_code=204)
def eliminar_programa_academico(
    programa_id: int,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Elimina un programa academico del catalogo."""
    servicio.eliminar(db=db, programa_id=programa_id)
    return None
