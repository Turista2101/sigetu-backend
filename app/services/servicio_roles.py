"""Reglas de negocio para CRUD de roles."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.modelo_usuario import User
from app.repositories.repositorio_roles import RepositorioRoles
from app.schemas.esquema_roles import ActualizarRol, CrearRol


class ServicioRoles:
    """Orquesta validaciones para operaciones sobre roles."""

    def __init__(self) -> None:
        self.repositorio = RepositorioRoles()

    @staticmethod
    def _normalizar_nombre(nombre: str) -> str:
        return nombre.strip().lower()

    def listar(self, db: Session):
        return self.repositorio.listar(db=db)

    def obtener(self, db: Session, role_id: int):
        rol = self.repositorio.obtener_por_id(db=db, role_id=role_id)
        if not rol:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        return rol

    def crear(self, db: Session, payload: CrearRol):
        nombre = self._normalizar_nombre(payload.name)
        if self.repositorio.obtener_por_nombre(db=db, nombre=nombre):
            raise HTTPException(status_code=400, detail="Ya existe un rol con ese nombre")
        return self.repositorio.crear(db=db, name=nombre)

    def actualizar(self, db: Session, role_id: int, payload: ActualizarRol):
        rol = self.repositorio.obtener_por_id(db=db, role_id=role_id)
        if not rol:
            raise HTTPException(status_code=404, detail="Rol no encontrado")

        if payload.name is None:
            raise HTTPException(status_code=400, detail="Debes enviar al menos un campo para actualizar")

        nombre = self._normalizar_nombre(payload.name) if payload.name is not None else None
        if nombre is not None:
            existente = self.repositorio.obtener_por_nombre(db=db, nombre=nombre)
            if existente and existente.id != rol.id:
                raise HTTPException(status_code=400, detail="Ya existe un rol con ese nombre")

        return self.repositorio.actualizar(db=db, rol=rol, name=nombre)

    def eliminar(self, db: Session, role_id: int) -> None:
        rol = self.repositorio.obtener_por_id(db=db, role_id=role_id)
        if not rol:
            raise HTTPException(status_code=404, detail="Rol no encontrado")

        usuarios_asociados = db.query(User).filter(User.role_id == rol.id).count()
        if usuarios_asociados > 0:
            raise HTTPException(status_code=400, detail="No se puede eliminar un rol con usuarios asociados")

        self.repositorio.eliminar(db=db, rol=rol)
