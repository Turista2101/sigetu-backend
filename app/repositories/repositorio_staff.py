"""Repositorio para consultas de usuarios con rol staff."""

from sqlalchemy.orm import Session

from app.models.modelo_staff import Staff
from app.models.modelo_usuario import User


class RepositorioStaff:
    """Abstrae consultas de usuarios staff y su asignacion de sede."""

    def listar_usuarios_staff(self, db: Session, sin_sede: bool = False) -> list[User]:
        consulta = db.query(User).join(User.role).filter(User.role.has(name="staff"))

        if sin_sede:
            consulta = consulta.outerjoin(Staff, Staff.user_id == User.id).filter(Staff.id.is_(None))

        return consulta.all()

    def obtener_asignacion_por_user_id(self, db: Session, user_id: int) -> Staff | None:
        """Retorna la asignación staff existente para un usuario, si existe."""
        return db.query(Staff).filter(Staff.user_id == user_id).first()

    def crear_asignacion(self, db: Session, user_id: int, sede_id: int, activo: bool = True) -> Staff:
        """Crea una asignación staff para un usuario."""
        asignacion = Staff(user_id=user_id, sede_id=sede_id, activo=activo)
        db.add(asignacion)
        db.commit()
        db.refresh(asignacion)
        return asignacion

    def actualizar_asignacion(
        self,
        db: Session,
        asignacion: Staff,
        sede_id: int | None = None,
        activo: bool | None = None,
    ) -> Staff:
        """Actualiza campos de una asignación staff existente."""
        if sede_id is not None:
            asignacion.sede_id = sede_id
        if activo is not None:
            asignacion.activo = activo
        db.commit()
        db.refresh(asignacion)
        return asignacion

    def eliminar_asignacion(self, db: Session, asignacion: Staff) -> None:
        """Elimina una asignación staff existente."""
        db.delete(asignacion)
        db.commit()