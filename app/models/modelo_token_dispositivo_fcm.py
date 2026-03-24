"""Modelo ORM para persistir tokens FCM por usuario/dispositivo."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.db.base import Base


class FCMDeviceToken(Base):
    """Token FCM asociado a un usuario autenticado o invitado por dispositivo."""
    __tablename__ = "fcm_device_tokens"
    __table_args__ = (
        UniqueConstraint("token", name="uq_fcm_device_tokens_token"),
        UniqueConstraint("user_id", "device_id", name="uq_fcm_device_tokens_user_device"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    device_id = Column(String(128), nullable=False, index=True)
    token = Column(String(512), nullable=False)
    platform = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
