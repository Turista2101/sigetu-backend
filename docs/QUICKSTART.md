# ⚡ QUICKSTART - Instala y ejecuta en 5 minutos

Guía para instalar y ejecutar SIGETU Backend en tu máquina de desarrollo.

## ✅ Requisitos previos

- **Python 3.11+** (recomendado 3.12 o 3.13)
- **PostgreSQL** corriendo localmente o en red
- **Git** (para clonar el repo)
- **PowerShell** (en Windows) o bash (Linux/Mac)

Verifica que tengas Python:
```powershell
python --version
```

## 🔧 Instalación paso a paso

### Paso 1: Clonar el repositorio

```powershell
git clone <URL_DEL_REPOSITORIO>
cd sigetu-backend
```

### Paso 2: Crear entorno virtual

```powershell
# Crear venv
python -m venv venv

# Activar venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# O si usas CMD
.\venv\Scripts\activate.bat

# O si usas bash (Linux/Mac)
source venv/bin/activate
```

Deberías ver `(venv)` al inicio del prompt.

### Paso 3: Instalar dependencias

```powershell
# Actualizar pip
python -m pip install --upgrade pip

# Instalar requirements
pip install -r requirements.txt
```

Esto instalará:
- FastAPI, uvicorn (servidor web)
- SQLAlchemy, psycopg2-binary (BD)
- Pydantic (validación)
- python-jose (JWT)
- Alembic (migraciones)
- Y más (ver `requirements.txt`)

### Paso 4: Crear base de datos

Asegúrate de tener PostgreSQL corriendo, luego:

```sql
-- Conéctate como admin a PostgreSQL
CREATE DATABASE sigetu;
```

O desde PowerShell:
```powershell
# Si tienes psql en PATH
psql -U postgres -c "CREATE DATABASE sigetu;"
```

### Paso 5: Configurar variables de entorno

Crea archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/sigetu
SECRET_KEY=tu_clave_secreta_super_larga_y_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**⚠️ Importante:**
- Reemplaza `tu_password` con tu contraseña de PostgreSQL
- Genera una SECRET_KEY segura (ej: resultado de `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- No commitees el `.env` a Git (está en `.gitignore`)

Ver archivo de ejemplo en [env.example](env.example)

### Paso 6: Aplicar migraciones

```powershell
# Ver estado actual
python -m alembic current

# Aplicar todas las migraciones
python -m alembic upgrade head

# Ver versión actual (debe mostrar algo como "e4f1a9c2d7b8")
python -m alembic current
```

Las migraciones crearán todas las tablas necesarias:
- `users` (estudiantes, secretaría)
- `roles` (admin, estudiante, secretaria)
- `appointments` (citas académicas)
- `appointment_history` (histórico de citas)
- `revoked_tokens` (tokens invalidados)

### Paso 7: Iniciar el servidor

```powershell
# Ejecutar con hot-reload (desarrollo)
uvicorn app.main:app --reload

# O sin reload (producción)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

## 🌐 Acceder a la API

### En navegador

- **Documentación interactiva (Swagger)**: http://localhost:8000/docs
- **Documentación alternativa (ReDoc)**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/status (si está configurado)

### Con curl (ejemplo)

```bash
# Registrar un estudiante
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "estudiante@example.com",
    "password": "12345678",
    "full_name": "Juan Pérez",
    "programa_academico": "ingenierias"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "estudiante@example.com",
    "password": "12345678"
  }'
```

### Con Python (ejemplo)

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    json={
        "email": "estudiante@example.com",
        "password": "12345678"
    }
)

data = response.json()
access_token = data["access_token"]

# Crear cita
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.post(
    "http://localhost:8000/appointments",
    headers=headers,
    json={
        "category": "academico",
        "context": "Consulta sobre calificaciones",
        "scheduled_at": None
    }
)

print(response.json())
```

## 🧪 Verificar que funciona

El servidor debería:

1. ✅ Iniciarse sin errores
2. ✅ Responder en http://localhost:8000/docs
3. ✅ Permitir registrarse en `/auth/register`
4. ✅ Permitir login en `/auth/login`
5. ✅ Crear citas en `/appointments` (con token)

Si algún paso falla, ver [Troubleshooting](#troubleshooting).

## 🆘 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastapi'"

```powershell
# Asegúrate que el venv está activado
.\venv\Scripts\Activate.ps1

# Reinstala dependencias
pip install -r requirements.txt
```

### Error: "could not translate host name 'localhost' to address"

La base de datos no está disponible. Verifica:

```powershell
# Instalar PostgreSQL
# O si ya está instalado
psql -U postgres -c "SELECT version();"

# Ver que DATABASE_URL en .env es correcto
```

### Error: "FATAL: password authentication failed"

Verifica la contraseña de PostgreSQL en `DATABASE_URL` en `.env`.

```powershell
# Resetear password de PostgreSQL (Windows)
pg_resetxlog -D "C:\Program Files\PostgreSQL\16\data"

# O crear nuevo usuario
psql -U postgres -c "CREATE USER dev WITH PASSWORD '12345678';"
```

### Error de migración: "FAILED: target database is not at a clean state"

```powershell
# Ver estado
python -m alembic current

# Rollback de la última migración
python -m alembic downgrade -1

# Intentar de nuevo
python -m alembic upgrade head
```

### El servidor inicia pero da error 422 en login

Verifica que tus credenciales sean exactas y que existan usuarios en BD. Ejecuta seed:

```powershell
python -c "from app.db.seed import seed_roles, seed_default_users; from app.db.session import SessionLocal; db = SessionLocal(); seed_roles(db); seed_default_users(db)"
```

Usuario de ejemplo: `estudiante@example.com` / `12345678`

## 📁 Estructura después de instalar

```
sigetu-backend/
├── venv/                    # Entorno virtual (no commitear)
├── app/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── core/
│   ├── db/
│   └── main.py
├── alembic/
├── .env                     # Variables de entorno (no commitear)
├── requirements.txt
└── README.md
```

## 🚀 Próximos pasos

1. ✅ Abre http://localhost:8000/docs
2. ✅ Prueba los endpoints (Register → Login → Create Appointment)
3. ✅ Lee [STRUCTURE.md](STRUCTURE.md) para entender la arquitectura
4. ✅ Consulta [COMMANDS.md](COMMANDS.md) para comandos útiles

## 📚 Más información

- [STRUCTURE.md](STRUCTURE.md) - Estructura del código
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Detalles del proyecto
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guía para desarrolladores
- [COMMANDS.md](COMMANDS.md) - Comandos útiles

---

¿Algo no funciona? → Revisa la sección [Troubleshooting](#troubleshooting)
