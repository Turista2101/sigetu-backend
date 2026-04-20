"""Repositorio de acceso a datos para roles."""

from sqlalchemy.orm import Session

from app.models.modelo_rol import Role


class RepositorioRoles:
    """Encapsula operaciones CRUD de roles."""

    def listar(self, db: Session) -> list[Role]:
        return db.query(Role).order_by(Role.name.asc()).all()

    def obtener_por_id(self, db: Session, role_id: int) -> Role | None:
        return db.query(Role).filter(Role.id == role_id).first()

    def obtener_por_nombre(self, db: Session, nombre: str) -> Role | None:
        return db.query(Role).filter(Role.name == nombre).first()

    def crear(self, db: Session, name: str) -> Role:
        rol = Role(name=name)
        db.add(rol)
        db.commit()
        db.refresh(rol)
        return rol

    def actualizar(self, db: Session, rol: Role, name: str | None = None) -> Role:
        if name is not None:
            rol.name = name
        db.commit()
        db.refresh(rol)
        return rol

    def eliminar(self, db: Session, rol: Role) -> None:
        db.delete(rol)
        db.commit()
