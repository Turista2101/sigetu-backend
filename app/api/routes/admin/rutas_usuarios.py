"""Endpoints CRUD administrativos para usuarios."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencias_autenticacion import requerir_rol_admin
from app.db.sesion import obtener_db
from app.schemas.esquema_usuarios import (
    ActualizarUsuarioAdmin,
    CrearUsuarioAdmin,
    RespuestaUsuarioAdmin,
)
from app.services.servicio_usuarios import ServicioUsuarios


router = APIRouter(prefix="/users", tags=["Usuarios"])
servicio = ServicioUsuarios()


def _mapear_respuesta_usuario(usuario) -> dict:
    """Mapea entidad User a respuesta administrativa."""
    return {
        "id": usuario.id,
        "email": usuario.email,
        "full_name": usuario.full_name,
        "programa_academico_id": usuario.programa_academico_id,
        "role_id": usuario.role_id,
        "role_name": usuario.role.name,
        "is_active": usuario.is_active,
        "created_at": usuario.created_at,
    }


@router.get("", response_model=list[RespuestaUsuarioAdmin])
def listar_usuarios(
    role_id: int | None = Query(None, description="Filtra por rol"),
    programa_academico_id: int | None = Query(None, description="Filtra por programa académico"),
    is_active: bool | None = Query(None, description="Filtra por estado activo/inactivo"),
    sin_sede: bool | None = Query(None, description="Si es true, retorna usuarios sin sede staff asignada"),
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Lista usuarios con filtros opcionales de administración."""
    usuarios = servicio.listar(
        db=db,
        role_id=role_id,
        programa_academico_id=programa_academico_id,
        is_active=is_active,
        sin_sede=sin_sede,
    )
    return [_mapear_respuesta_usuario(usuario) for usuario in usuarios]


@router.get("/{user_id}", response_model=RespuestaUsuarioAdmin)
def obtener_usuario(
    user_id: int,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Obtiene un usuario por su identificador."""
    usuario = servicio.obtener(db=db, user_id=user_id)
    return _mapear_respuesta_usuario(usuario)


@router.post("", response_model=RespuestaUsuarioAdmin, status_code=201)
def crear_usuario(
    payload: CrearUsuarioAdmin,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Crea un usuario con rol y programa académico."""
    usuario = servicio.crear(db=db, payload=payload)
    return _mapear_respuesta_usuario(usuario)


@router.patch("/{user_id}", response_model=RespuestaUsuarioAdmin)
def actualizar_usuario(
    user_id: int,
    payload: ActualizarUsuarioAdmin,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Actualiza de forma parcial un usuario existente."""
    usuario = servicio.actualizar(db=db, user_id=user_id, payload=payload)
    return _mapear_respuesta_usuario(usuario)


@router.delete("/{user_id}", status_code=204)
def eliminar_usuario(
    user_id: int,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Elimina un usuario del sistema."""
    servicio.eliminar(db=db, user_id=user_id)
    return None
