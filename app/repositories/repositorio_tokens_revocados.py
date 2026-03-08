from datetime import datetime

from sqlalchemy.orm import Session

from app.models.modelo_token_revocado import RevokedToken


class RepositorioTokensRevocados:
    def esta_revocado(self, db: Session, jti: str) -> bool:
        return db.query(RevokedToken).filter(RevokedToken.jti == jti).first() is not None

    def revocar(self, db: Session, jti: str, expires_at: datetime) -> RevokedToken:
        existente = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
        if existente:
            return existente

        token = RevokedToken(jti=jti, expires_at=expires_at)
        db.add(token)
        db.commit()
        db.refresh(token)
        return token
