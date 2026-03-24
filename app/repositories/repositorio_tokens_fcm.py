"""Repositorio para registrar y consultar tokens de dispositivos FCM."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.modelo_token_dispositivo_fcm import FCMDeviceToken


class RepositorioTokensFCM:
    """Gestiona alta, actualización y limpieza de tokens FCM por usuario."""

    def registrar_o_actualizar(
        self,
        db: Session,
        user_id: int,
        device_id: str,
        token: str,
        platform: str,
    ) -> FCMDeviceToken:
        """Crea o actualiza un token FCM identificando el dispositivo del usuario."""
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)

        existente_dispositivo = (
            db.query(FCMDeviceToken)
            .filter(
                FCMDeviceToken.user_id == user_id,
                FCMDeviceToken.device_id == device_id,
            )
            .first()
        )
        if existente_dispositivo:
            setattr(existente_dispositivo, "token", token)
            setattr(existente_dispositivo, "platform", platform)
            setattr(existente_dispositivo, "updated_at", ahora)
            db.commit()
            db.refresh(existente_dispositivo)
            return existente_dispositivo

        existente_token = db.query(FCMDeviceToken).filter(FCMDeviceToken.token == token).first()
        if existente_token:
            setattr(existente_token, "user_id", user_id)
            setattr(existente_token, "device_id", device_id)
            setattr(existente_token, "platform", platform)
            setattr(existente_token, "updated_at", ahora)
            db.commit()
            db.refresh(existente_token)
            return existente_token

        registro = FCMDeviceToken(
            user_id=user_id,
            device_id=device_id,
            token=token,
            platform=platform,
        )
        db.add(registro)
        db.commit()
        db.refresh(registro)
        return registro

    def registrar_o_actualizar_invitado(
        self,
        db: Session,
        device_id: str,
        token: str,
        platform: str,
    ) -> FCMDeviceToken:
        """Crea o actualiza un token FCM solo con device_id (para invitados)."""
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # 1. Buscar por device_id → si encuentra, actualiza
        existente = db.query(FCMDeviceToken).filter(FCMDeviceToken.device_id == device_id).first()
        if existente:
            existente.token = token
            existente.platform = platform
            existente.updated_at = ahora
            existente.user_id = None  # Asegura que no quede asociado a usuario
            db.commit()
            db.refresh(existente)
            return existente
        
        # 2. Buscar por token → si encuentra, actualiza (evita UniqueViolation)
        existente_token = db.query(FCMDeviceToken).filter(FCMDeviceToken.token == token).first()
        if existente_token:
            existente_token.device_id = device_id
            existente_token.platform = platform
            existente_token.updated_at = ahora
            existente_token.user_id = None  # Asegura que no quede asociado a usuario
            db.commit()
            db.refresh(existente_token)
            return existente_token
        
        # 3. Solo si ninguno existe, crea nuevo registro
        registro = FCMDeviceToken(
            user_id=None,
            device_id=device_id,
            token=token,
            platform=platform,
        )
        db.add(registro)
        db.commit()
        db.refresh(registro)
        return registro

    def listar_tokens_por_usuario(self, db: Session, user_id: int) -> list[str]:
        """Retorna los tokens FCM activos del usuario."""
        filas = db.query(FCMDeviceToken.token).filter(FCMDeviceToken.user_id == user_id).all()
        return [fila[0] for fila in filas]

    def listar_tokens_por_dispositivo(self, db: Session, device_id: str) -> list[str]:
        """Retorna los tokens FCM activos asociados a un device_id (invitado)."""
        filas = db.query(FCMDeviceToken.token).filter(FCMDeviceToken.device_id == device_id).all()
        return [fila[0] for fila in filas]

    def listar_tokens_por_device(self, db: Session, device_id: str) -> list[str]:
        """Devuelve todos los tokens FCM asociados a un device_id (invitado o usuario)."""
        return [r.token for r in db.query(FCMDeviceToken).filter(FCMDeviceToken.device_id == device_id).all()]

    def eliminar_por_token(self, db: Session, token: str) -> None:
        """Elimina un token inválido reportado por Firebase."""
        registro = db.query(FCMDeviceToken).filter(FCMDeviceToken.token == token).first()
        if registro is None:
            return
        db.delete(registro)
        db.commit()
