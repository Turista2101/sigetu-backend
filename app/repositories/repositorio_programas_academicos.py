"""Repositorio de acceso a datos para programas academicos."""

from sqlalchemy.orm import Session

from app.models.modelo_programa_academico import ProgramaAcademico


class RepositorioProgramasAcademicos:
    """Encapsula operaciones CRUD de programas academicos."""

    def listar(self, db: Session, solo_activos: bool | None = None) -> list[ProgramaAcademico]:
        consulta = db.query(ProgramaAcademico)
        if solo_activos is not None:
            consulta = consulta.filter(ProgramaAcademico.activo == solo_activos)
        return consulta.order_by(ProgramaAcademico.nombre.asc()).all()

    def obtener_por_id(self, db: Session, programa_id: int) -> ProgramaAcademico | None:
        return db.query(ProgramaAcademico).filter(ProgramaAcademico.id == programa_id).first()

    def obtener_por_codigo(self, db: Session, codigo: str) -> ProgramaAcademico | None:
        return db.query(ProgramaAcademico).filter(ProgramaAcademico.codigo == codigo).first()

    def obtener_por_nombre(self, db: Session, nombre: str) -> ProgramaAcademico | None:
        return db.query(ProgramaAcademico).filter(ProgramaAcademico.nombre == nombre).first()

    def crear(
        self,
        db: Session,
        codigo: str,
        nombre: str,
        descripcion: str | None,
        activo: bool,
    ) -> ProgramaAcademico:
        programa = ProgramaAcademico(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            activo=activo,
        )
        db.add(programa)
        db.commit()
        db.refresh(programa)
        return programa

    def actualizar(self, db: Session, programa: ProgramaAcademico, **campos) -> ProgramaAcademico:
        for campo, valor in campos.items():
            if valor is not None:
                setattr(programa, campo, valor)
        db.commit()
        db.refresh(programa)
        return programa

    def eliminar(self, db: Session, programa: ProgramaAcademico) -> None:
        db.delete(programa)
        db.commit()
