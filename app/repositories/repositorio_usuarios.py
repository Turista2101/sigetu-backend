"""Repositorio de operaciones CRUD básicas de usuarios."""

from sqlalchemy.orm import Session

from app.models.modelo_staff import Staff
from app.models.modelo_usuario import User

class RepositorioUsuario:
    """Abstrae lectura y creación de usuarios en base de datos."""

    def obtener_por_email(self, db: Session, email: str):
        """Busca un usuario por correo electrónico."""
        return db.query(User).filter(User.email == email).first()

    def obtener_por_id(self, db: Session, user_id: int):
        """Busca un usuario por identificador."""
        return db.query(User).filter(User.id == user_id).first()

    def listar(
        self,
        db: Session,
        role_id: int | None = None,
        programa_academico_id: int | None = None,
        is_active: bool | None = None,
        sin_sede: bool | None = None,
    ):
        """Lista usuarios con filtros opcionales de rol, programa, estado y asignación staff."""
        consulta = db.query(User)

        if role_id is not None:
            consulta = consulta.filter(User.role_id == role_id)
        if programa_academico_id is not None:
            consulta = consulta.filter(User.programa_academico_id == programa_academico_id)
        if is_active is not None:
            consulta = consulta.filter(User.is_active == is_active)
        if sin_sede is True:
            consulta = consulta.outerjoin(Staff, Staff.user_id == User.id).filter(Staff.id.is_(None))

        return consulta.order_by(User.id.asc()).all()

    def crear(
        self,
        db: Session,
        email: str,
        full_name: str,
        hashed_password: str,
        role_id: int,
        programa_academico_id: int,
        is_active: bool = True,
    ):
        """Crea un usuario nuevo con su rol y metadatos iniciales."""
        usuario = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role_id=role_id,
            programa_academico_id=programa_academico_id,
            is_active=is_active,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    def actualizar(self, db: Session, usuario: User, **campos):
        """Actualiza campos de usuario de manera parcial."""
        for campo, valor in campos.items():
            if valor is not None:
                setattr(usuario, campo, valor)
        db.commit()
        db.refresh(usuario)
        return usuario

    def eliminar(self, db: Session, usuario: User) -> None:
        """Elimina un usuario."""
        db.delete(usuario)
        db.commit()