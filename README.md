# SIGETU Backend

Sistema de gestión de citas académicas construido con **FastAPI**, **SQLAlchemy** y **PostgreSQL**.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI 0.131](https://img.shields.io/badge/fastapi-0.131-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-12+-336791.svg)](https://www.postgresql.org/)

## 📋 Acerca de

SIGETU Backend permite a **estudiantes** crear y gestionar citas académicas, y a **secretaría** administrar la cola de atención en tiempo real.

**Características principales:**
- 🎓 Gestión de citas por categoría (académica, administrativa, financiera, otra)
- 👥 Dos roles con permisos diferenciados (estudiante, secretaría)
- 🔐 Autenticación con JWT y refresh tokens
- 📡 Actualizaciones en tiempo real vía WebSocket
- 🗄️ Migraciones versionadas con Alembic
- 📚 Documentación interactiva en Swagger

## 🚀 Quick Start

```bash
# 1. Clonar
git clone <repo_url>
cd sigetu-backend

# 2. Instalar
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt

# 3. Configurar BD (.env)
# DATABASE_URL=postgresql://user:pass@localhost:5432/sigetu
# SECRET_KEY=tu_clave_secreta

# 4. Migraciones
python -m alembic upgrade head

# 5. Ejecutar
uvicorn app.main:app --reload
```

Accede a **http://localhost:8000/docs** para la API interactiva.

Para instalación detallada → [docs/QUICKSTART.md](docs/QUICKSTART.md)

## 📚 Documentación

Toda la documentación está en la carpeta **`docs/`**:

| Documento | Descripción |
|-----------|------------|
| [docs/START_HERE.md](docs/START_HERE.md) | 🎯 Lee primero - orientación general |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | ⚡ Instalación en 5 minutos |
| [docs/STRUCTURE.md](docs/STRUCTURE.md) | 🏗️ Arquitectura detallada |
| [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) | 📋 Visión completa del proyecto |
| [docs/COMMANDS.md](docs/COMMANDS.md) | 💻 Comandos útiles |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | 🤝 Guía para desarrolladores |
| [docs/INDEX.md](docs/INDEX.md) | 📑 Índice completo de enlaces |

**👉 Comienza por [docs/START_HERE.md](docs/START_HERE.md)**

## Paso a paso (recién clonado)

## 1) Clonar el repositorio

```powershell
git clone <URL_DEL_REPO>
cd sigetu-backend
```

## 2) Crear y activar entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
```

## 3) Configurar PostgreSQL y variables de entorno

Crea el archivo `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/sigetu
SECRET_KEY=tu-clave-secreta-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## 4) Ejecutar migraciones

```powershell
python -m alembic upgrade head
python -m alembic current
```

## 5) Levantar el servidor

```powershell
uvicorn app.main:app --reload
```

Documentación: **http://localhost:8000/docs**

## 6) Usuarios semilla

Se crean automáticamente:

| Email | Password | Rol |
|-------|----------|-----|
| `estudiante@example.com` | `12345678` | estudiante |
| `secretaria@example.com` | `12345678` | secretaria |

---

## 🏗️ Arquitectura

Arquitectura de capas bien definidas:

```
HTTP/WebSocket Routes
    ↓
Services (Lógica de Negocio)
    ↓
Repositories (Acceso a Datos)
    ↓
Models/Schemas (ORM + Pydantic)
    ↓
PostgreSQL Database
```

Ver detalles en [docs/STRUCTURE.md](docs/STRUCTURE.md)

## 🔐 Roles y permisos

| Rol | Permisos |
|-----|----------|
| **Estudiante** | Crear, ver y editar sus propias citas |
| **Secretaría** | Ver cola, cambiar estados, ver historial |

Autenticación por JWT. Ver [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)

## 📡 API Endpoints principales

### Autenticación
- `POST /auth/register` - Registrar
- `POST /auth/login` - Login (email/password)
- `POST /auth/refresh` - Renovar token
- `POST /auth/logout` - Logout

### Estudiante
- `POST /appointments` - Crear cita
- `GET /appointments/me` - Ver mis citas
- `GET /appointments/me/current` - Ver citas activas
- `GET /appointments/me/history` - Ver historial
- `PATCH /appointments/{id}` - Editar mi cita

### Secretaría
- `GET /appointments/queue` - Ver cola
- `GET /appointments/queue/history` - Ver historial
- `PATCH /appointments/{id}/status` - Cambiar estado

### WebSocket
- `WS /ws/appointments/{token}` - Actualizaciones en tiempo real

Documentación interactiva: **http://localhost:8000/docs**

## 🗄️ Tecnologías

| Componente | Herramienta |
|-----------|-----------|
| Framework | FastAPI 0.131 |
| ORM | SQLAlchemy 2.0.46 |
| Base de datos | PostgreSQL |
| Migraciones | Alembic 1.18.4 |
| Validación | Pydantic 2.12.5 |
| Autenticación | JWT (python-jose) |
| Hashing | bcrypt 3.2.2 |
| Servidor | Uvicorn (ASGI) |

Ver `requirements.txt` para lista completa.

## 📁 Estructura del proyecto

```
sigetu-backend/
├── app/
│   ├── api/routes/           # Endpoints HTTP/WS
│   ├── services/             # Lógica de negocio
│   ├── repositories/         # Acceso a datos
│   ├── models/               # Modelos ORM
│   ├── schemas/              # Validación Pydantic
│   ├── core/                 # Config, auth, seguridad
│   ├── db/                   # Sesiones, seeds
│   └── main.py               # App principal
├── alembic/                  # Migraciones
├── .env                      # Variables de entorno
├── requirements.txt          # Dependencias
└── README.md                 # Este archivo
```

Detalles: [docs/STRUCTURE.md](docs/STRUCTURE.md)

## ⚙️ Configuración

### Variables de entorno (`.env`)

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/sigetu
SECRET_KEY=mi-clave-secreta-super-larga
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Ver [env.example](env.example)

## 🚀 Desarrollo

### Iniciar servidor

```bash
uvicorn app.main:app --reload
```

### Migraciones

```bash
python -m alembic upgrade head
python -m alembic history --verbose
```

[Más comandos →](docs/COMMANDS.md)

## 📖 Documentación completa

- **Para la primera guía**: [docs/START_HERE.md](docs/START_HERE.md)
- **Para instalar**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **Para la arquitectura**: [docs/STRUCTURE.md](docs/STRUCTURE.md)
- **Para desarrollar**: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- **Para comandos**: [docs/COMMANDS.md](docs/COMMANDS.md)
- **Para todo**: [docs/INDEX.md](docs/INDEX.md)

## 🆘 Solución de problemas

| Problema | Solución |
|----------|----------|
| "Database connection failed" | Verifica DATABASE_URL en `.env` |
| "Migration failed" | Revertir: `alembic downgrade -1` |
| "Port already in use" | Usa otro puerto: `--port 8001` |

[Troubleshooting completo →](docs/QUICKSTART.md#-troubleshooting)

## 🔀 Workflow

1. `git checkout -b feature/descripción`
2. Implementar cambios
3. Crear migración si cambió modelo
4. Probar en http://localhost:8000/docs
5. Commit y push

Detalles: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

**¿Eres nuevo?** → [docs/START_HERE.md](docs/START_HERE.md)  
**¿Necesitas instalar?** → [docs/QUICKSTART.md](docs/QUICKSTART.md)  
**¿Vas a desarrollar?** → [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)  
**¿Necesitas buscar algo?** → [docs/INDEX.md](docs/INDEX.md)
