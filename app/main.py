from app.db.seed import seed_default_users, seed_roles
from fastapi import FastAPI
from app.db.session import SessionLocal
from app.api.routes import auth_routes
from app.api.routes.estudiante import appointment_routes as estudiante_appointment_routes
from app.api.routes.secretaria import appointment_routes as secretaria_appointment_routes


app = FastAPI()


app.include_router(auth_routes.router)
app.include_router(estudiante_appointment_routes.router)
app.include_router(secretaria_appointment_routes.router)
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    seed_roles(db)
    seed_default_users(db)
    db.close()