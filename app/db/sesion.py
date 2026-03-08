from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.configuracion import DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()