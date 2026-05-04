"""Repositorio de operaciones CRUD básicas de usuarios."""

from sqlalchemy.orm import Session
from app.models.modelo_usuario import User

class RepositorioUsuario:
    """Abstrae lectura y creación de usuarios en base de datos."""

    def obtener_por_email(self, db: Session, email: str):
        """Busca un usuario por correo electrónico."""
        return db.query(User).filter(User.email == email).first()

    def obtener_por_id(self, db: Session, user_id: int):
        """Busca un usuario por id."""
        return db.query(User).filter(User.id == user_id).first()

    def crear(
        self,
        db: Session,
        email: str,
        full_name: str,
        hashed_password: str,
        role_id: int,
        programa_academico: str | None = None,
        is_active: bool = True,
    ):
        """Crea un usuario nuevo con su rol y metadatos iniciales."""
        usuario = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role_id=role_id,
            programa_academico=programa_academico,
            is_active=is_active,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    def actualizar_contrasena(self, db: Session, usuario: User, hashed_password: str) -> User:
        """Actualiza la contrasena hasheada de un usuario."""
        usuario.hashed_password = hashed_password
        db.commit()
        db.refresh(usuario)
        return usuario