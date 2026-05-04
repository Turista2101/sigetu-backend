"""Punto de entrada de FastAPI: registra middlewares, rutas y datos semilla."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.sesion import SessionLocal, engine
from app.db.datos_iniciales import seed_default_users, seed_roles

# Importar todos los modelos para que Base los registre antes de create_all
import app.models.modelo_rol
import app.models.modelo_usuario
import app.models.modelo_cita
import app.models.modelo_historial_cita
import app.models.modelo_token_revocado
import app.models.modelo_token_dispositivo_fcm

from app.api.routes import rutas_ws_citas
from app.api.routes import rutas_autenticacion
from app.api.routes import rutas_notificaciones
from app.api.routes.estudiante import rutas_citas as rutas_citas_estudiante
from app.api.routes.secretaria import rutas_citas as rutas_citas_secretaria

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",        # Flutter Web desarrollo
        "https://sigetu-ft.vercel.app",        # Producción web (cambiar por tu dominio)   
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rutas_autenticacion.router)
app.include_router(rutas_notificaciones.router)
app.include_router(rutas_citas_secretaria.router)  # ← Secretaría PRIMERO
app.include_router(rutas_citas_estudiante.router)  # ← Estudiante DESPUÉS
app.include_router(rutas_ws_citas.router)

@app.on_event("startup")
def evento_inicio():
    """Crea tablas si no existen, luego inicializa roles y usuarios semilla."""
    logger.info("Iniciando aplicación...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_roles(db)
    seed_default_users(db)
    db.close()
    logger.info("Aplicación iniciada correctamente")
