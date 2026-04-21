"""Servicio de negocio para consultas de usuarios staff."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.modelo_sede import Sede
from app.models.modelo_usuario import User
from app.repositories.repositorio_staff import RepositorioStaff
from app.schemas.esquema_staff import ActualizarStaff, CrearStaff


class ServicioStaff:
    """Coordina reglas de consulta de staff para endpoints administrativos."""

    def __init__(self) -> None:
        self.repositorio = RepositorioStaff()

    def listar_staff(
        self,
        db: Session,
        sin_sede: bool = False,
        sede_id: int | None = None,
        activo: bool | None = None,
    ):
        filas = self.repositorio.listar_usuarios_staff(
            db=db,
            sin_sede=sin_sede,
            sede_id=sede_id,
            activo=activo,
        )
        return [
            {
                "user_id": usuario.id,
                "email": usuario.email,
                "full_name": usuario.full_name,
                "programa_academico_id": usuario.programa_academico_id,
                "is_active": usuario.is_active,
                "sede_id": asignacion.sede_id if asignacion else None,
                "staff_activo": asignacion.activo if asignacion else None,
            }
            for usuario, asignacion in filas
        ]

    def crear_staff(self, db: Session, payload: CrearStaff):
        usuario = db.query(User).filter(User.id == payload.user_id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if not usuario.role or usuario.role.name != "staff":
            raise HTTPException(status_code=400, detail="El usuario debe tener rol staff")

        sede = db.query(Sede).filter(Sede.id == payload.sede_id, Sede.activo == True).first()
        if not sede:
            raise HTTPException(status_code=404, detail="Sede no encontrada o inactiva")

        existente = self.repositorio.obtener_asignacion_por_user_id(db=db, user_id=payload.user_id)
        if existente:
            raise HTTPException(status_code=400, detail="El usuario ya tiene una asignación staff")

        return self.repositorio.crear_asignacion(
            db=db,
            user_id=payload.user_id,
            sede_id=payload.sede_id,
            activo=payload.activo,
        )

    def actualizar_staff(self, db: Session, user_id: int, payload: ActualizarStaff):
        if payload.sede_id is None and payload.activo is None:
            raise HTTPException(status_code=400, detail="Debes enviar al menos un campo para actualizar")

        asignacion = self.repositorio.obtener_asignacion_por_user_id(db=db, user_id=user_id)
        if not asignacion:
            raise HTTPException(status_code=404, detail="Asignación staff no encontrada")

        if payload.sede_id is not None:
            sede = db.query(Sede).filter(Sede.id == payload.sede_id, Sede.activo == True).first()
            if not sede:
                raise HTTPException(status_code=404, detail="Sede no encontrada o inactiva")

        return self.repositorio.actualizar_asignacion(
            db=db,
            asignacion=asignacion,
            sede_id=payload.sede_id,
            activo=payload.activo,
        )

    def eliminar_staff(self, db: Session, user_id: int) -> None:
        asignacion = self.repositorio.obtener_asignacion_por_user_id(db=db, user_id=user_id)
        if not asignacion:
            raise HTTPException(status_code=404, detail="Asignación staff no encontrada")

        self.repositorio.eliminar_asignacion(db=db, asignacion=asignacion)