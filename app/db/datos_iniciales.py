from sqlalchemy.orm import Session
from app.models.modelo_rol import Role
from app.models.modelo_usuario import User
from app.core.seguridad import hashear_contrasena


SEED_PASSWORD = "12345678"
PROGRAMAS_ACADEMICOS = ["ingenierias", "derecho", "finanzas"]

def seed_roles(db: Session):
    roles = ["admin", "estudiante", "secretaria"]

    for role_name in roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            new_role = Role(name=role_name)
            db.add(new_role)

    db.commit()


def seed_default_users(db: Session):
    role_estudiante = db.query(Role).filter(Role.name == "estudiante").first()
    role_secretaria = db.query(Role).filter(Role.name == "secretaria").first()

    if not role_estudiante or not role_secretaria:
        return

    def upsert_user(email: str, full_name: str, role_id: int, programa_academico: str | None):
        existing_user = db.query(User).filter(User.email == email).first()
        hashed = hashear_contrasena(SEED_PASSWORD)

        if existing_user:
            existing_user.full_name = full_name
            existing_user.role_id = role_id
            existing_user.programa_academico = programa_academico
            existing_user.is_active = True
            existing_user.hashed_password = hashed
            db.commit()
            return

        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed,
            programa_academico=programa_academico,
            is_active=True,
            role_id=role_id,
        )
        db.add(user)
        db.commit()

    upsert_user(
        email="secretaria@uniautonoma.edu.co",
        full_name="Secretaria Ingenierias",
        role_id=role_secretaria.id,
        programa_academico="ingenierias",
    )

    for programa in PROGRAMAS_ACADEMICOS:
        upsert_user(
            email=f"estudiante.{programa}@uniautonoma.edu.co",
            full_name=f"Estudiante {programa.capitalize()}",
            role_id=role_estudiante.id,
            programa_academico=programa,
        )
        upsert_user(
            email=f"secretaria.{programa}@uniautonoma.edu.co",
            full_name=f"Secretaria {programa.capitalize()}",
            role_id=role_secretaria.id,
            programa_academico=programa,
        )