from sqlalchemy.orm import Session
from app.models.modelo_usuario import User

class RepositorioUsuario:

    def obtener_por_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

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