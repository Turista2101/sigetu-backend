# SIGETU Backend

Sistema de gestión de citas académicas construido con **FastAPI**, **SQLAlchemy** y **PostgreSQL**.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI 0.131](https://img.shields.io/badge/fastapi-0.131-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-12+-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)](https://www.docker.com/)

## 📋 Acerca de

SIGETU Backend permite a **estudiantes** crear y gestionar citas académicas, y a **secretaría/administrativos** administrar la cola de atención en tiempo real.

**Características principales:**
- 🎓 Gestión de citas por categoría y sede (académica, administrativa, financiera)
- 👥 Sistema de roles con permisos diferenciados (estudiante, secretaría, administrativo)
- 🔐 Autenticación JWT con refresh tokens
- 📡 Actualizaciones en tiempo real vía WebSocket
- 🔔 Notificaciones push con Firebase Cloud Messaging (FCM)
- 🐳 Docker Compose para despliegue rápido
- 🗄️ Migraciones versionadas con Alembic
- 📚 Documentación interactiva con Swagger

## 🚀 Quick Start

### Opción 1: Con Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone <repo_url>
cd sigetu-backend

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 3. Ejecutar con Docker Compose
docker-compose up -d

# 4. Ver logs
docker-compose logs -f api
```

Accede a **http://localhost:8000/docs** para la API interactiva.

### Opción 2: Sin Docker (Instalación manual)

```bash
# 1. Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows PowerShell

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env
# DATABASE_URL=postgresql://postgres:password@localhost:5432/sigetu
# SECRET_KEY=tu_clave_secreta_segura

# 4. Ejecutar migraciones
python -m alembic upgrade head

# 5. Iniciar servidor
uvicorn app.main:app --reload
```

**Para más detalles** → [docs/QUICKSTART.md](docs/QUICKSTART.md)

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

## 👥 Usuarios de prueba

Al iniciar el servidor por primera vez, se crean automáticamente:

| Email | Password | Rol |
|-------|----------|-----|
| `estudiante@example.com` | `12345678` | estudiante |
| `secretaria@example.com` | `12345678` | secretaria |
| `admin@example.com` | `12345678` | administrativo |

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
| **Administrativo** | Ver cola, cambiar estados, ver historial |

**Autenticación:** JWT con access y refresh tokens. Ver [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)

## 📡 API Endpoints principales

### Autenticación (`/auth/*`)
- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Login con email/password
- `POST /auth/refresh` - Renovar access token
- `POST /auth/logout` - Cerrar sesión

### Citas - Estudiante (`/appointments`)
- `POST /appointments` - Crear cita
- `GET /appointments/me` - Ver todas mis citas
- `GET /appointments/me/current` - Ver citas activas
- `GET /appointments/me/history` - Ver historial
- `PATCH /appointments/{id}` - Editar mi cita
- `DELETE /appointments/{id}/cancel` - Cancelar mi cita

### Citas - Secretaría/Administrativo
- `GET /appointments/queue` - Ver cola de atención
- `GET /appointments/queue/history` - Ver historial atendidas
- `GET /appointments/{id}/detail` - Ver detalles de cita
- `PATCH /appointments/{id}/status` - Cambiar estado de cita

### Notificaciones (`/notifications`)
- `POST /notifications/register-device` - Registrar dispositivo FCM
- `POST /notifications/unregister-device` - Desregistrar dispositivo

### WebSocket (`/ws/*`)
- `WS /ws/appointments/{token}` - Actualizaciones en tiempo real

**Documentación interactiva:** http://localhost:8000/docs

## 🗄️ Tecnologías

| Componente | Herramienta |
|-----------|-----------|
| Framework | FastAPI 0.131 |
| ORM | SQLAlchemy 2.0.46 |
| Base de datos | PostgreSQL 16 |
| Migraciones | Alembic 1.18.4 |
| Validación | Pydantic 2.12.5 |
| Autenticación | JWT (python-jose) |
| Hashing | bcrypt 3.2.2 |
| Notificaciones | Firebase Admin SDK |
| Servidor | Uvicorn (ASGI) |
| Contenedores | Docker + Docker Compose |

Ver `requirements.txt` para la lista completa de dependencias.

## 📁 Estructura del proyecto

```
sigetu-backend/
├── app/
│   ├── api/routes/              # Endpoints HTTP/WS
│   │   ├── estudiante/          # Rutas de estudiantes
│   │   ├── secretaria/          # Rutas de secretaría/admin
│   │   ├── rutas_autenticacion.py
│   │   ├── rutas_notificaciones.py
│   │   └── rutas_ws_citas.py
│   ├── services/                # Lógica de negocio
│   ├── repositories/            # Acceso a datos
│   ├── models/                  # Modelos ORM (SQLAlchemy)
│   │   ├── modelo_usuario.py
│   │   ├── modelo_cita.py
│   │   ├── modelo_historial_cita.py
│   │   ├── modelo_token_dispositivo_fcm.py
│   │   └── ...
│   ├── schemas/                 # Validación Pydantic
│   ├── core/                    # Config, auth, seguridad
│   ├── db/                      # Sesiones, seeds
│   └── main.py                  # App principal FastAPI
├── alembic/                     # Migraciones de base de datos
├── docs/                        # Documentación del proyecto
├── docker-compose.yml           # Orquestación Docker
├── Dockerfile                   # Imagen Docker
├── start.sh                     # Script de inicio
├── .env                         # Variables de entorno (no commitear)
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

**Detalles completos:** [docs/STRUCTURE.md](docs/STRUCTURE.md)

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

### Con Docker Compose

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f api

# Ejecutar migraciones
docker-compose exec api python -m alembic upgrade head

# Detener servicios
docker-compose down
```

### Sin Docker

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Iniciar servidor con hot-reload
uvicorn app.main:app --reload

# Ejecutar migraciones
python -m alembic upgrade head
```

**Más comandos:** [docs/COMMANDS.md](docs/COMMANDS.md)

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

## 🔀 Workflow de desarrollo

1. Crear rama: `git checkout -b feature/descripcion`
2. Implementar cambios siguiendo la arquitectura de capas
3. Si cambiaste modelos: `python -m alembic revision --autogenerate -m "descripcion"`
4. Aplicar migraciones: `python -m alembic upgrade head`
5. Probar en http://localhost:8000/docs
6. Commit y push

**Guía completa:** [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

**¿Eres nuevo?** → [docs/START_HERE.md](docs/START_HERE.md)  
**¿Necesitas instalar?** → [docs/QUICKSTART.md](docs/QUICKSTART.md)  
**¿Vas a desarrollar?** → [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)  
**¿Necesitas buscar algo?** → [docs/INDEX.md](docs/INDEX.md)
