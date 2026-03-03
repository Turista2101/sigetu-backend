# SIGETU Backend

Backend de gestión de citas construido con FastAPI + SQLAlchemy + Alembic.

## Requisitos

- Python 3.11+ (recomendado 3.12/3.13)
- PostgreSQL activo
- Windows PowerShell (comandos de ejemplo)

## Paso a paso (recién clonado)

## 1) Clonar el repositorio

```powershell
git clone <URL_DEL_REPO>
cd sigetu-backend
```

## 2) Crear y activar entorno virtual

```powershell
# desde la raíz del proyecto
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3) Configurar PostgreSQL y variables de entorno

Asegúrate de tener una base de datos creada (por ejemplo `sigetu`).

Crea/edita el archivo `.env` en la raíz:

```env
DATABASE_URL=postgresql://postgres:12345678@localhost:5432/sigetu
SECRET_KEY=tu_secret_key_larga
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## 4) Ejecutar migraciones

Usa siempre Alembic con el Python del entorno virtual:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

## 5) Levantar el servidor

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Documentación interactiva:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 6) Usuarios semilla (se crean en startup)

Contraseña por defecto:

- `12345678`

Ejemplos útiles:

- Estudiante: `estudiante.ingenierias@uniautonoma.edu.co`
- Secretaría: `secretaria.ingenierias@uniautonoma.edu.co`
- Secretaría general: `secretaria@uniautonoma.edu.co`

## Flujo rápido de prueba

1. Login estudiante en `/auth/login`
2. Crear cita en `POST /appointments`
3. Login secretaría en `/auth/login`
4. Cambiar estado en `PATCH /appointments/{appointment_id}/status`

Para mantener sesión en frontend, usa `/auth/refresh` enviando el `refresh_token` cuando el `access_token` expire.

Para cerrar sesión, usa `/auth/logout` con el `refresh_token`; el token queda revocado y ya no podrá renovarse.

Body para cambio de estado:

```json
{
  "status": "llamando"
}
```

## Solución de problemas

### `alembic` no se reconoce en terminal

Ejecuta con:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

### Error de migración por estado parcial de base de datos

Si una migración falló a mitad de camino y la base quedó inconsistente, limpia el esquema y vuelve a migrar:

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

Luego ejecuta otra vez:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

### Error de bcrypt/passlib al iniciar

Este proyecto fija `bcrypt==3.2.2` para compatibilidad con `passlib==1.7.4`.
Si ya tenías otra versión instalada, reinstala:

```powershell
python -m pip install -r requirements.txt
```
