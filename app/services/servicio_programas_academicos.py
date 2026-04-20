"""Reglas de negocio para CRUD de programas academicos."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.repositorio_programas_academicos import RepositorioProgramasAcademicos
from app.schemas.esquema_programas_academicos import ActualizarProgramaAcademico, CrearProgramaAcademico


class ServicioProgramasAcademicos:
    """Orquesta validaciones y operaciones CRUD de programas academicos."""

    def __init__(self) -> None:
        self.repositorio = RepositorioProgramasAcademicos()

    @staticmethod
    def _normalizar_codigo(codigo: str) -> str:
        return codigo.strip().lower()

    @staticmethod
    def _normalizar_nombre(nombre: str) -> str:
        return nombre.strip()

    def listar(self, db: Session, solo_activos: bool | None = None):
        return self.repositorio.listar(db=db, solo_activos=solo_activos)

    def obtener(self, db: Session, programa_id: int):
        programa = self.repositorio.obtener_por_id(db=db, programa_id=programa_id)
        if not programa:
            raise HTTPException(status_code=404, detail="Programa academico no encontrado")
        return programa

    def crear(self, db: Session, payload: CrearProgramaAcademico):
        codigo = self._normalizar_codigo(payload.codigo)
        nombre = self._normalizar_nombre(payload.nombre)

        if self.repositorio.obtener_por_codigo(db=db, codigo=codigo):
            raise HTTPException(status_code=400, detail="Ya existe un programa academico con ese codigo")

        if self.repositorio.obtener_por_nombre(db=db, nombre=nombre):
            raise HTTPException(status_code=400, detail="Ya existe un programa academico con ese nombre")

        return self.repositorio.crear(
            db=db,
            codigo=codigo,
            nombre=nombre,
            descripcion=payload.descripcion,
            activo=payload.activo,
        )

    def actualizar(self, db: Session, programa_id: int, payload: ActualizarProgramaAcademico):
        programa = self.repositorio.obtener_por_id(db=db, programa_id=programa_id)
        if not programa:
            raise HTTPException(status_code=404, detail="Programa academico no encontrado")

        codigo = self._normalizar_codigo(payload.codigo) if payload.codigo is not None else None
        nombre = self._normalizar_nombre(payload.nombre) if payload.nombre is not None else None

        if codigo is not None:
            existente = self.repositorio.obtener_por_codigo(db=db, codigo=codigo)
            if existente and existente.id != programa.id:
                raise HTTPException(status_code=400, detail="Ya existe un programa academico con ese codigo")

        if nombre is not None:
            existente = self.repositorio.obtener_por_nombre(db=db, nombre=nombre)
            if existente and existente.id != programa.id:
                raise HTTPException(status_code=400, detail="Ya existe un programa academico con ese nombre")

        return self.repositorio.actualizar(
            db=db,
            programa=programa,
            codigo=codigo,
            nombre=nombre,
            descripcion=payload.descripcion,
            activo=payload.activo,
        )

    def eliminar(self, db: Session, programa_id: int) -> None:
        programa = self.repositorio.obtener_por_id(db=db, programa_id=programa_id)
        if not programa:
            raise HTTPException(status_code=404, detail="Programa academico no encontrado")
        self.repositorio.eliminar(db=db, programa=programa)
