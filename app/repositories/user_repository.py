from sqlalchemy.orm import Session
from app.models.user_model import User

class UserRepository:

    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def create(
        self,
        db: Session,
        email: str,
        full_name: str,
        hashed_password: str,
        role_id: int,
        programa_academico: str | None = None,
        is_active: bool = True,
    ):
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role_id=role_id,
            programa_academico=programa_academico,
            is_active=is_active,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user