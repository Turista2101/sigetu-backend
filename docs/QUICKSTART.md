# ⚡ QUICKSTART - Instala y ejecuta en 5 minutos

Guía para instalar y ejecutar SIGETU Backend en tu máquina de desarrollo.

## ✅ Requisitos previos

Elige **una** de las dos opciones:

### Opción 1: Con Docker (Recomendado - Más simple)
- **Docker Desktop** instalado
- **Docker Compose** (incluido en Docker Desktop)
- **Git**

### Opción 2: Sin Docker (Manual)
- **Python 3.11+** (recomendado 3.12 o 3.13)
- **PostgreSQL 12+** corriendo localmente
- **Git**
- **PowerShell** (Windows) o bash (Linux/Mac)

---

## 🐳 Instalación con Docker (Recomendado)

### Paso 1: Clonar el repositorio

```powershell
git clone <URL_DEL_REPOSITORIO>
cd sigetu-backend
```

### Paso 2: Configurar variables de entorno

Crea archivo `.env` en la raíz del proyecto:

```env
# Base de datos (usa 'db' como host cuando uses Docker Compose)
DATABASE_URL=postgresql://postgres:2101@db:5432/sigetu

# Seguridad
SECRET_KEY=tu_clave_secreta_super_larga_y_segura_aqui
ALGORITHM=HS256

# Tokens
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_DAYS=7

# Firebase (opcional - para notificaciones push)
FIREBASE_CREDENTIALS_PATH=./sigetu-b10c0-firebase-adminsdk-fbsvc-d3c8e11eaf.json

# SMTP (restablecimiento de contraseña)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=usuario@example.com
SMTP_PASSWORD=tu_password_smtp
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=usuario@example.com
SMTP_FROM_NAME=SIGETU
RESET_PASSWORD_BASE_URL=http://localhost:5173/reset-password
RESET_TOKEN_EXPIRE_MINUTES=15
RESET_REQUEST_LIMIT_WINDOW_MINUTES=15
RESET_REQUEST_LIMIT_MAX=3
```

**⚠️ Importante:**
- Genera SECRET_KEY segura: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- El archivo Firebase es opcional (solo si usas notificaciones)
- Para restablecimiento de contraseña debes configurar SMTP y RESET_PASSWORD_BASE_URL
- No commitees el `.env` a Git (ya está en `.gitignore`)

### Paso 3: Ejecutar con Docker Compose

```powershell
# Construir e iniciar servicios (API + PostgreSQL)
docker-compose up -d

# Ver logs
docker-compose logs -f api

# O ver todos los servicios
docker-compose logs -f
```

Deberías ver:
```
sigetu_api | Marcando migraciones como aplicadas...
sigetu_api | Corriendo migraciones...
sigetu_api | Iniciando servidor...
sigetu_api | INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Paso 4: Verificar que funciona

- **Documentación API**: http://localhost:8000/docs
- **Estado de servicios**: `docker-compose ps`

**¡Listo!** Usuarios de prueba creados automáticamente:
- `estudiante@example.com` / `12345678`
- `secretaria@example.com` / `12345678`

### Comandos útiles Docker

```powershell
# Detener servicios
docker-compose down

# Reiniciar servicios
docker-compose restart

# Ver logs en tiempo real
docker-compose logs -f api

# Ejecutar comando dentro del contenedor
docker-compose exec api python -m alembic current

# Acceder a shell del contenedor
docker-compose exec api bash

# Acceder a PostgreSQL
docker-compose exec db psql -U postgres -d sigetu

# Reconstruir después de cambios
docker-compose up -d --build
```

**Saltar a:** [Verificar instalación](#-verificar-que-funciona) | [Troubleshooting](#-troubleshooting)

---

## 📦 Instalación sin Docker (Manual)

### Requisitos
Verifica que tengas Python:
```powershell
python --version  # Debe ser 3.11+
```

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
- Firebase Admin SDK (notificaciones)
- Y más (ver `requirements.txt`)

### Paso 4: Configurar PostgreSQL

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
# Base de datos (usa 'localhost' cuando NO uses Docker)
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/sigetu

# Seguridad
SECRET_KEY=tu_clave_secreta_super_larga_y_segura_aqui
ALGORITHM=HS256

# Tokens
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_DAYS=7

# Firebase (opcional - para notificaciones push)
FIREBASE_CREDENTIALS_PATH=./sigetu-b10c0-firebase-adminsdk-fbsvc-d3c8e11eaf.json

# SMTP (restablecimiento de contraseña)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=usuario@example.com
SMTP_PASSWORD=tu_password_smtp
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=usuario@example.com
SMTP_FROM_NAME=SIGETU
RESET_PASSWORD_BASE_URL=http://localhost:5173/reset-password
RESET_TOKEN_EXPIRE_MINUTES=15
RESET_REQUEST_LIMIT_WINDOW_MINUTES=15
RESET_REQUEST_LIMIT_MAX=3
```

**⚠️ Importante:**
- Reemplaza `tu_password` con tu contraseña de PostgreSQL
- Genera una SECRET_KEY segura: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Para restablecimiento de contraseña debes configurar SMTP y RESET_PASSWORD_BASE_URL
- No commitees el `.env` a Git (está en `.gitignore`)

### Paso 6: Aplicar migraciones

```powershell
# Ver estado actual
python -m alembic current

# Aplicar todas las migraciones
python -m alembic upgrade head

# Verificar versión (debe mostrar el ID de la última migración)
python -m alembic current
```

Las migraciones crearán todas las tablas necesarias:
- `users` (estudiantes, secretaría, administrativos)
- `roles` (admin, estudiante, secretaria, administrativo)
- `appointments` (citas académicas/administrativas)
- `appointment_history` (histórico de citas)
- `revoked_tokens` (tokens invalidados)
- `fcm_device_tokens` (dispositivos para notificaciones)

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

---

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

### Error de migración: "target database is not at a clean state"

```powershell
# Ver estado
python -m alembic current

# Rollback de la última migración
python -m alembic downgrade -1

# Intentar de nuevo
python -m alembic upgrade head
```

### El servidor inicia pero da error 422 en login

Verifica que tus credenciales sean exactas y que existan usuarios en BD. Los usuarios se crean automáticamente al iniciar la app, pero si necesitas recrearlos:

```powershell
python -c "from app.db.seed import seed_roles, seed_default_users; from app.db.session import SessionLocal; db = SessionLocal(); seed_roles(db); seed_default_users(db); db.close()"
```

Usuarios de ejemplo: 
- `estudiante@example.com` / `12345678`
- `secretaria@example.com` / `12345678`

### Docker: "Cannot connect to the Docker daemon"

Asegúrate de que Docker Desktop está corriendo:
- Windows: Abre Docker Desktop desde el menú inicio
- Verifica: `docker ps` debe funcionar

### Docker: "port is already allocated"

El puerto 8000 o 5432 está en uso:

```powershell
# Cambiar puerto de la API en docker-compose.yml
ports:
  - "8001:8000"  # Usa 8001 en vez de 8000

# O detener el proceso que usa el puerto
# Windows: netstat -ano | findstr :8000
# Luego: taskkill /PID <proceso_id> /F
```

## 📁 Estructura después de instalar

### Con Docker
```
sigetu-backend/
├── .env                         # Variables de entorno
├── docker-compose.yml           # Orquestación
├── Dockerfile                   # Imagen Docker
├── start.sh                     # Script de inicio
├── app/                         # Código fuente
└── docs/                        # Documentación
```

### Sin Docker
```
sigetu-backend/
├── venv/                        # Entorno virtual (no commitear)
├── .env                         # Variables de entorno (no commitear)
├── app/
│   ├── api/routes/
│   │   ├── estudiante/
│   │   ├── secretaria/
│   │   ├── rutas_autenticacion.py
│   │   ├── rutas_notificaciones.py
│   │   └── rutas_ws_citas.py
│   ├── services/
│   ├── models/
│   ├── core/
│   ├── db/
│   └── main.py
├── alembic/
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
