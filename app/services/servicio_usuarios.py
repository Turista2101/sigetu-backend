"""Reglas de negocio para CRUD administrativo de usuarios."""

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.seguridad import hashear_contrasena
from app.models.modelo_programa_academico import ProgramaAcademico
from app.models.modelo_rol import Role
from app.repositories.repositorio_usuarios import RepositorioUsuario
from app.schemas.esquema_usuarios import ActualizarUsuarioAdmin, CrearUsuarioAdmin


class ServicioUsuarios:
    """Orquesta validaciones y operaciones CRUD de usuarios para administración."""

    def __init__(self) -> None:
        self.repositorio = RepositorioUsuario()

    @staticmethod
    def _normalizar_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _normalizar_nombre(full_name: str) -> str:
        return full_name.strip()

    def listar(
        self,
        db: Session,
        role_id: int | None = None,
        programa_academico_id: int | None = None,
        is_active: bool | None = None,
        sin_sede: bool | None = None,
    ):
        return self.repositorio.listar(
            db=db,
            role_id=role_id,
            programa_academico_id=programa_academico_id,
            is_active=is_active,
            sin_sede=sin_sede,
        )

    def obtener(self, db: Session, user_id: int):
        usuario = self.repositorio.obtener_por_id(db=db, user_id=user_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return usuario

    def _validar_programa_activo(self, db: Session, programa_id: int) -> ProgramaAcademico:
        programa = (
            db.query(ProgramaAcademico)
            .filter(ProgramaAcademico.id == programa_id, ProgramaAcademico.activo == True)
            .first()
        )
        if not programa:
            raise HTTPException(status_code=404, detail="Programa académico no encontrado o inactivo")
        return programa

    def _validar_rol(self, db: Session, role_id: int) -> Role:
        rol = db.query(Role).filter(Role.id == role_id).first()
        if not rol:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        return rol

    def crear(self, db: Session, payload: CrearUsuarioAdmin):
        email = self._normalizar_email(payload.email)
        full_name = self._normalizar_nombre(payload.full_name)

        if self.repositorio.obtener_por_email(db=db, email=email):
            raise HTTPException(status_code=400, detail="Email ya registrado")

        programa = self._validar_programa_activo(db=db, programa_id=payload.programa_academico_id)
        rol = self._validar_rol(db=db, role_id=payload.role_id)

        usuario = self.repositorio.crear(
            db=db,
            email=email,
            full_name=full_name,
            hashed_password=hashear_contrasena(payload.password),
            role_id=rol.id,
            programa_academico_id=programa.id,
            is_active=payload.is_active,
        )

        return usuario

    def actualizar(self, db: Session, user_id: int, payload: ActualizarUsuarioAdmin):
        usuario = self.repositorio.obtener_por_id(db=db, user_id=user_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        cambios = payload.model_dump(exclude_unset=True)
        if not cambios:
            raise HTTPException(status_code=400, detail="Debes enviar al menos un campo para actualizar")

        email = None
        if "email" in cambios:
            email = self._normalizar_email(payload.email)
            existente = self.repositorio.obtener_por_email(db=db, email=email)
            if existente and existente.id != usuario.id:
                raise HTTPException(status_code=400, detail="Email ya registrado")

        full_name = self._normalizar_nombre(payload.full_name) if "full_name" in cambios else None
        hashed_password = hashear_contrasena(payload.password) if "password" in cambios else None

        programa_id = None
        if "programa_academico_id" in cambios:
            programa = self._validar_programa_activo(db=db, programa_id=payload.programa_academico_id)
            programa_id = programa.id

        role_id = None
        if "role_id" in cambios:
            rol_objetivo = self._validar_rol(db=db, role_id=payload.role_id)
            role_id = rol_objetivo.id

        usuario = self.repositorio.actualizar(
            db=db,
            usuario=usuario,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            programa_academico_id=programa_id,
            role_id=role_id,
            is_active=payload.is_active if "is_active" in cambios else None,
        )

        return usuario

    def eliminar(self, db: Session, user_id: int) -> None:
        usuario = self.repositorio.obtener_por_id(db=db, user_id=user_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        try:
            self.repositorio.eliminar(db=db, usuario=usuario)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="No se puede eliminar el usuario por restricciones de integridad")
