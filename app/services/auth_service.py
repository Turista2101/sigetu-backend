from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.models.role_model import Role

class AuthService:

    ALLOWED_PROGRAMAS = {"ingenierias", "derecho", "finanzas"}

    def __init__(self):
        self.user_repo = UserRepository()

    def register(
        self,
        db: Session,
        full_name: str,
        email: str,
        password: str,
        programa_academico: str | None = None,
    ):
        if self.user_repo.get_by_email(db, email):
            raise HTTPException(status_code=400, detail="Email ya registrado")

        hashed_password = hash_password(password)

        default_role = db.query(Role).filter(Role.id == 2).first()
        if not default_role:
            raise HTTPException(status_code=500, detail="Rol por defecto no configurado")

        if default_role.name == "estudiante":
            if programa_academico is None:
                raise HTTPException(status_code=400, detail="programa_academico es obligatorio para estudiantes")
            if programa_academico not in self.ALLOWED_PROGRAMAS:
                raise HTTPException(status_code=400, detail="programa_academico inválido")
        else:
            programa_academico = None

        user = self.user_repo.create(
            db=db,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role_id=default_role.id,
            programa_academico=programa_academico,
        )

        token = create_access_token({"sub": user.email, "role": user.role.name})

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "programa_academico": user.programa_academico,
                "is_active": user.is_active,
                "created_at": user.created_at,
            },
            "access_token": token,
            "token_type": "bearer",
        }

    def login(self, db: Session, email: str, password: str):
        user = self.user_repo.get_by_email(db, email)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Usuario inactivo")

        token = create_access_token({"sub": user.email, "role": user.role.name})

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "programa_academico": user.programa_academico,
                "is_active": user.is_active,
                "created_at": user.created_at,
            },
            "access_token": token,
            "token_type": "bearer",
        }