from app.db.datos_iniciales import seed_default_users, seed_roles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.sesion import SessionLocal
from app.api.routes import rutas_ws_citas
from app.api.routes import rutas_autenticacion
from app.api.routes.estudiante import rutas_citas as rutas_citas_estudiante
from app.api.routes.secretaria import rutas_citas as rutas_citas_secretaria


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(rutas_autenticacion.router)
app.include_router(rutas_citas_estudiante.router)
app.include_router(rutas_citas_secretaria.router)
app.include_router(rutas_ws_citas.router)
@app.on_event("startup")
def evento_inicio():
    db = SessionLocal()
    seed_roles(db)
    seed_default_users(db)
    db.close()