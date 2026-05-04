"""Repositorio para tokens de restablecimiento de contrasena."""

from datetime import datetime
from sqlalchemy.orm import Session
from app.models.modelo_token_restablecer_contrasena import PasswordResetToken


class RepositorioTokensRestablecerContrasena:
    """Acceso a datos para tokens de restablecimiento de contrasena."""

    def crear(
        self,
        db: Session,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        requested_ip: str,
    ) -> PasswordResetToken:
        token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            requested_ip=requested_ip,
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        return token

    def contar_recientes_por_usuario(
        self,
        db: Session,
        user_id: int,
        desde: datetime,
    ) -> int:
        return (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.user_id == user_id)
            .filter(PasswordResetToken.created_at >= desde)
            .count()
        )

    def contar_recientes_por_ip(
        self,
        db: Session,
        requested_ip: str,
        desde: datetime,
    ) -> int:
        return (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.requested_ip == requested_ip)
            .filter(PasswordResetToken.created_at >= desde)
            .count()
        )

    def obtener_por_hash(self, db: Session, token_hash: str) -> PasswordResetToken | None:
        return (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == token_hash)
            .first()
        )

    def marcar_usado(self, db: Session, token: PasswordResetToken, usado_en: datetime) -> None:
        token.used_at = usado_en
        db.commit()
