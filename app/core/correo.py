"""Envio de correos via Resend."""

import logging
import resend

from app.core.configuracion import RESEND_API_KEY, RESEND_FROM_EMAIL, RESEND_FROM_NAME

logger = logging.getLogger(__name__)

resend.api_key = RESEND_API_KEY


def enviar_correo(destinatario: str, asunto: str, texto: str, html: str | None = None) -> None:
    if not RESEND_API_KEY or not RESEND_FROM_EMAIL:
        raise ValueError("Resend no configurado")

    from_addr = f"{RESEND_FROM_NAME} <{RESEND_FROM_EMAIL}>" if RESEND_FROM_NAME else RESEND_FROM_EMAIL

    try:
        resend.Emails.send({
            "from": from_addr,
            "to": destinatario,
            "subject": asunto,
            "html": html or f"<pre>{texto}</pre>",
            "text": texto,
        })
    except Exception as exc:
        logger.exception("Fallo enviando correo con Resend")
        raise exc
