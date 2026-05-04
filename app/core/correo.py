"""Envio de correos via SMTP."""

import logging
import smtplib
from email.message import EmailMessage

from app.core.configuracion import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_USE_TLS,
    SMTP_FROM_EMAIL,
    SMTP_FROM_NAME,
)

logger = logging.getLogger(__name__)


def enviar_correo(destinatario: str, asunto: str, texto: str, html: str | None = None) -> None:
    if not SMTP_HOST or not SMTP_FROM_EMAIL:
        raise ValueError("SMTP no configurado")

    mensaje = EmailMessage()
    mensaje["Subject"] = asunto
    mensaje["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>" if SMTP_FROM_NAME else SMTP_FROM_EMAIL
    mensaje["To"] = destinatario
    mensaje.set_content(texto)

    if html:
        mensaje.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as servidor:
            if SMTP_USE_TLS:
                servidor.starttls()
            if SMTP_USERNAME and SMTP_PASSWORD:
                servidor.login(SMTP_USERNAME, SMTP_PASSWORD)
            servidor.send_message(mensaje)
    except smtplib.SMTPException as exc:
        logger.exception("Fallo enviando correo SMTP")
        raise exc
