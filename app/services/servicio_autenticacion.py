"""Lógica de negocio de autenticación, registro y gestión de tokens."""

from fastapi import HTTPException
from jose import JWTError, jwt
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.repositorio_usuarios import RepositorioUsuario
from app.repositories.repositorio_tokens_revocados import RepositorioTokensRevocados
from app.core.configuracion import ALGORITHM, SECRET_KEY
from app.core.seguridad import hashear_contrasena, verificar_contrasena, crear_token_acceso, crear_token_refresco, crear_token_invitado
from app.models.modelo_rol import Role
from app.models.modelo_cita import Appointment
from app.models.modelo_programa_academico import ProgramaAcademico

class ServicioAutenticacion:
    """Orquesta validación de credenciales, emisión de JWT y revocación de refresh tokens."""

    def __init__(self):
        self.repositorio_usuario = RepositorioUsuario()
        self.repositorio_tokens_revocados = RepositorioTokensRevocados()

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

    def registrar(
        self,
        db: Session,
        full_name: str,
        email: str,
        password: str,
        programa_academico_id: int,
        device_id: str | None = None,
    ):
        """Registra un estudiante y migra citas activas de invitado cuando corresponda."""
        if self.repositorio_usuario.obtener_por_email(db, email):
            raise HTTPException(status_code=400, detail="Email ya registrado")

        contrasena_hasheada = hashear_contrasena(password)

        rol_por_defecto = db.query(Role).filter(Role.id == 2).first()
        if not rol_por_defecto:
            raise HTTPException(status_code=500, detail="Rol por defecto no configurado")

        programa_obj = (
            db.query(ProgramaAcademico)
            .filter(
                ProgramaAcademico.id == programa_academico_id,
                ProgramaAcademico.activo == True,
            )
            .first()
        )
        if not programa_obj:
            raise HTTPException(status_code=400, detail="programa_academico_id inválido")

        usuario = self.repositorio_usuario.crear(
            db=db,
            email=email,
            full_name=full_name,
            hashed_password=contrasena_hasheada,
            role_id=rol_por_defecto.id,
            programa_academico_id=programa_obj.id if programa_obj else None,
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
                "programa_academico_id": usuario.programa.id,
                "is_active": usuario.is_active,
                "created_at": usuario.created_at,
            },
            **tokens,
        }

    def iniciar_sesion(self, db: Session, email: str, password: str):
        """Autentica usuario por email/password y retorna tokens activos."""
        usuario = self.repositorio_usuario.obtener_por_email(db, email)

        if not usuario:
            raise HTTPException(status_code=401, detail="Email no registrado")

        if not verificar_contrasena(password, usuario.hashed_password):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        if not usuario.is_active:
            raise HTTPException(status_code=403, detail="Usuario inactivo")

        tokens = self._construir_par_tokens(email=usuario.email, role=usuario.role.name)

        return {
            "user": {
                "id": usuario.id,
                "email": usuario.email,
                "full_name": usuario.full_name,
                "programa_academico_id": usuario.programa.id,
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