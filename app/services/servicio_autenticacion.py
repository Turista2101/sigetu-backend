"""Lógica de negocio de autenticación, registro y gestión de tokens."""

from fastapi import HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta
import hashlib
import secrets
from sqlalchemy.orm import Session
from app.repositories.repositorio_usuarios import RepositorioUsuario
from app.repositories.repositorio_tokens_revocados import RepositorioTokensRevocados
from app.repositories.repositorio_tokens_restablecer_contrasena import RepositorioTokensRestablecerContrasena
from app.core.configuracion import (
    ALGORITHM,
    SECRET_KEY,
    RESET_PASSWORD_BASE_URL,
    RESET_TOKEN_EXPIRE_MINUTES,
    RESET_REQUEST_LIMIT_WINDOW_MINUTES,
    RESET_REQUEST_LIMIT_MAX,
)
from app.core.correo import enviar_correo
from app.core.seguridad import (
    hashear_contrasena,
    verificar_contrasena,
    crear_token_acceso,
    crear_token_refresco,
    crear_token_invitado,
)
from app.models.modelo_rol import Role
from app.models.modelo_cita import Appointment

class ServicioAutenticacion:
    """Orquesta validación de credenciales, emisión de JWT y revocación de refresh tokens."""

    PROGRAMAS_PERMITIDOS = {"ingenierias", "derecho", "finanzas"}

    def __init__(self):
        self.repositorio_usuario = RepositorioUsuario()
        self.repositorio_tokens_revocados = RepositorioTokensRevocados()
        self.repositorio_tokens_restablecer = RepositorioTokensRestablecerContrasena()

    def _extraer_payload_refresco(self, refresh_token: str) -> dict:
        """Valida y descompone un refresh token en los datos mínimos requeridos."""
        try:
            carga = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError as exc:
            raise HTTPException(status_code=401, detail="Refresh token inválido o expirado") from exc

        if carga.get("token_type") != "refresh":
            raise HTTPException(status_code=401, detail="Token no válido para renovación")

        sub = carga.get("sub")
        jti = carga.get("jti")
        exp = carga.get("exp")

        if not sub or not jti or exp is None:
            raise HTTPException(status_code=401, detail="Refresh token inválido")

        expira_en = datetime.utcfromtimestamp(exp)

        return {
            "sub": sub,
            "jti": jti,
            "expires_at": expira_en,
        }

    def _construir_par_tokens(self, email: str, role: str) -> dict:
        """Construye el par access/refresh con payload de identidad y rol."""
        carga_token = {"sub": email, "role": role}
        return {
            "access_token": crear_token_acceso(carga_token),
            "refresh_token": crear_token_refresco(carga_token),
            "token_type": "bearer",
        }

    def _hash_reset_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def registrar(
        self,
        db: Session,
        full_name: str,
        email: str,
        password: str,
        programa_academico: str | None = None,
        device_id: str | None = None,
    ):
        """Registra un estudiante y migra citas activas de invitado cuando corresponda."""
        if self.repositorio_usuario.obtener_por_email(db, email):
            raise HTTPException(status_code=400, detail="Email ya registrado")

        contrasena_hasheada = hashear_contrasena(password)

        rol_por_defecto = db.query(Role).filter(Role.id == 2).first()
        if not rol_por_defecto:
            raise HTTPException(status_code=500, detail="Rol por defecto no configurado")

        if rol_por_defecto.name == "estudiante":
            if programa_academico is None:
                raise HTTPException(status_code=400, detail="programa_academico es obligatorio para estudiantes")
            if programa_academico not in self.PROGRAMAS_PERMITIDOS:
                raise HTTPException(status_code=400, detail="programa_academico inválido")
        else:
            programa_academico = None

        usuario = self.repositorio_usuario.crear(
            db=db,
            email=email,
            full_name=full_name,
            hashed_password=contrasena_hasheada,
            role_id=rol_por_defecto.id,
            programa_academico=programa_academico,
        )

        if device_id:
            citas_invitado = (
                db.query(Appointment)
                .filter(Appointment.device_id == device_id)
                .all()
            )
            for cita in citas_invitado:
                cita.student_id = usuario.id
                cita.device_id = None
            db.commit()

        tokens = self._construir_par_tokens(email=usuario.email, role=usuario.role.name)

        return {
            "user": {
                "id": usuario.id,
                "email": usuario.email,
                "full_name": usuario.full_name,
                "programa_academico": usuario.programa_academico,
                "is_active": usuario.is_active,
                "created_at": usuario.created_at,
            },
            **tokens,
        }

    def iniciar_sesion(self, db: Session, email: str, password: str):
        """Autentica usuario por email/password y retorna tokens activos."""
        usuario = self.repositorio_usuario.obtener_por_email(db, email)

        if not usuario or not verificar_contrasena(password, usuario.hashed_password):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        if not usuario.is_active:
            raise HTTPException(status_code=403, detail="Usuario inactivo")

        tokens = self._construir_par_tokens(email=usuario.email, role=usuario.role.name)

        return {
            "user": {
                "id": usuario.id,
                "email": usuario.email,
                "full_name": usuario.full_name,
                "programa_academico": usuario.programa_academico,
                "is_active": usuario.is_active,
                "created_at": usuario.created_at,
            },
            **tokens,
        }

    def renovar(self, db: Session, refresh_token: str) -> dict:
        """Rota refresh token y emite un nuevo par de tokens si el usuario sigue activo."""
        carga_refresco = self._extraer_payload_refresco(refresh_token)

        if self.repositorio_tokens_revocados.esta_revocado(db, carga_refresco["jti"]):
            raise HTTPException(status_code=401, detail="Refresh token revocado")

        usuario = self.repositorio_usuario.obtener_por_email(db, carga_refresco["sub"])
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        if not usuario.is_active:
            raise HTTPException(status_code=403, detail="Usuario inactivo")

        self.repositorio_tokens_revocados.revocar(
            db=db,
            jti=carga_refresco["jti"],
            expires_at=carga_refresco["expires_at"],
        )

        return self._construir_par_tokens(email=usuario.email, role=usuario.role.name)

    def cerrar_sesion(self, db: Session, refresh_token: str) -> dict:
        """Revoca el refresh token actual para cerrar sesión de forma segura."""
        carga_refresco = self._extraer_payload_refresco(refresh_token)

        self.repositorio_tokens_revocados.revocar(
            db=db,
            jti=carga_refresco["jti"],
            expires_at=carga_refresco["expires_at"],
        )

        return {"detail": "Sesión cerrada correctamente"}

    def login_invitado(self, device_id: str) -> dict:
        """Genera un access token temporal para flujo de invitado por dispositivo."""
        return {
            "access_token": crear_token_invitado(device_id),
            "token_type": "bearer",
        }

    def solicitar_reset_password(self, db: Session, email: str, requested_ip: str) -> dict:
        """Genera token de restablecimiento y envia correo sin revelar si el email existe."""
        if not RESET_PASSWORD_BASE_URL:
            raise HTTPException(status_code=500, detail="Base URL de restablecimiento no configurada")

        ventana = datetime.utcnow() - timedelta(minutes=RESET_REQUEST_LIMIT_WINDOW_MINUTES)
        intentos_ip = self.repositorio_tokens_restablecer.contar_recientes_por_ip(
            db=db,
            requested_ip=requested_ip,
            desde=ventana,
        )
        if intentos_ip >= RESET_REQUEST_LIMIT_MAX:
            raise HTTPException(status_code=429, detail="Has alcanzado el limite de solicitudes")

        usuario = self.repositorio_usuario.obtener_por_email(db, email)
        if not usuario or not usuario.is_active:
            return {"detail": "Si el correo existe, enviaremos instrucciones para restablecer la contrasena"}

        intentos_usuario = self.repositorio_tokens_restablecer.contar_recientes_por_usuario(
            db=db,
            user_id=usuario.id,
            desde=ventana,
        )
        if intentos_usuario >= RESET_REQUEST_LIMIT_MAX:
            raise HTTPException(status_code=429, detail="Has alcanzado el limite de solicitudes")

        token = secrets.token_urlsafe(32)
        token_hash = self._hash_reset_token(token)
        expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)

        self.repositorio_tokens_restablecer.crear(
            db=db,
            user_id=usuario.id,
            token_hash=token_hash,
            expires_at=expires_at,
            requested_ip=requested_ip,
        )

        enlace = f"{RESET_PASSWORD_BASE_URL}?token={token}"
        asunto = "Restablecer contrasena"
        texto = (
            "Recibimos una solicitud para restablecer tu contrasena.\n\n"
            f"Usa este enlace para continuar: {enlace}\n\n"
            f"Este enlace expira en {RESET_TOKEN_EXPIRE_MINUTES} minutos."
        )
        html = f"""
        <!doctype html>
        <html lang="es">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>SIGETU - UNIAUTONOMA</title>
          </head>
          <body style="margin:0;padding:0;background-color:#F4F8FF;font-family:Arial,Helvetica,sans-serif;color:#1A2B4C;">
            <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background-color:#F4F8FF;padding:24px 12px;">
              <tr>
                <td align="center">
                  <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;background-color:#FFFFFF;border:1px solid #C9D8FF;border-radius:16px;overflow:hidden;">
                    <tr>
                      <td align="center" style="padding:28px 24px 8px 24px;background-color:#FFFFFF;">
                        <img src="https://buscacarrera.com.co/public/content/logos/uniautonoma_cauca.png" alt="SIGETU" width="120" style="display:block;border:0;outline:none;text-decoration:none;">
                      </td>
                    </tr>
                    <tr>
                      <td align="center" style="padding:0 24px 20px 24px;">
                        <h1 style="margin:0;font-size:20px;letter-spacing:0.5px;color:#1A2B4C;">SIGETU - UNIAUTONOMA</h1>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:0 28px 10px 28px;">
                        <p style="margin:0;font-size:15px;line-height:1.6;color:#1A2B4C;">
                          Recibimos una solicitud para restablecer tu contrasena. Si fuiste tu, usa el boton de abajo para continuar.
                        </p>
                      </td>
                    </tr>
                    <tr>
                      <td align="center" style="padding:18px 28px 12px 28px;">
                        <a href="{enlace}" style="background-color:#2F6FED;color:#FFFFFF;text-decoration:none;padding:12px 22px;border-radius:10px;display:inline-block;font-weight:700;font-size:14px;">
                          Restablecer contrasena
                        </a>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:0 28px 16px 28px;">
                        <p style="margin:0;font-size:13px;line-height:1.6;color:#4A5A7A;">
                          Este enlace expira en {RESET_TOKEN_EXPIRE_MINUTES} minutos.
                        </p>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:0 28px 20px 28px;">
                        <p style="margin:0;font-size:12px;line-height:1.6;color:#4A5A7A;">
                          Si el boton no funciona, copia y pega este enlace en tu navegador:
                        </p>
                        <p style="margin:8px 0 0 0;font-size:12px;line-height:1.6;word-break:break-all;">
                          <a href="{enlace}" style="color:#2F6FED;text-decoration:underline;">{enlace}</a>
                        </p>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:16px 28px 24px 28px;border-top:1px solid #C9D8FF;background-color:#F8FAFF;">
                        <p style="margin:0;font-size:12px;line-height:1.6;color:#4A5A7A;">
                          Si no solicitaste este cambio, puedes ignorar este correo.
                        </p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """

        try:
            enviar_correo(destinatario=usuario.email, asunto=asunto, texto=texto, html=html)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="No fue posible enviar el correo de restablecimiento",
            ) from exc

        return {"detail": "Si el correo existe, enviaremos instrucciones para restablecer la contrasena"}

    def confirmar_reset_password(self, db: Session, token: str, new_password: str) -> dict:
        """Valida token de restablecimiento y actualiza la contrasena."""
        token_hash = self._hash_reset_token(token)
        registro = self.repositorio_tokens_restablecer.obtener_por_hash(db, token_hash)

        if not registro:
            raise HTTPException(status_code=400, detail="Token invalido o expirado")

        ahora = datetime.utcnow()
        if registro.used_at is not None or registro.expires_at < ahora:
            raise HTTPException(status_code=400, detail="Token invalido o expirado")

        usuario = self.repositorio_usuario.obtener_por_id(db, registro.user_id)
        if not usuario or not usuario.is_active:
            raise HTTPException(status_code=400, detail="Token invalido o expirado")

        contrasena_hasheada = hashear_contrasena(new_password)
        self.repositorio_usuario.actualizar_contrasena(
            db=db,
            usuario=usuario,
            hashed_password=contrasena_hasheada,
        )
        self.repositorio_tokens_restablecer.marcar_usado(db=db, token=registro, usado_en=ahora)

        return {"detail": "Contrasena actualizada correctamente"}
