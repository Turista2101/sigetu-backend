# AGENTS.md — SIGETU Backend

Backend de gestión de citas académicas. FastAPI + SQLAlchemy + PostgreSQL + Alembic.

## Comandos esenciales

| Acción | Comando |
|--------|---------|
| Dev server (local) | `uvicorn app.main:app --reload` |
| Dev server (Docker) | `docker-compose up -d` |
| Ver logs Docker | `docker-compose logs -f api` |
| Aplicar migraciones | `python -m alembic upgrade head` |
| Crear migración | `python -m alembic revision --autogenerate -m "descripcion"` |
| Revertir última migración | `python -m alembic downgrade -1` |
| Ver estado migraciones | `python -m alembic current` |
| Docker: migrar | `docker-compose exec api python -m alembic upgrade head` |

**Entorno virtual (Windows):** `.\venv\Scripts\Activate.ps1`

**Docker:** `docker-compose down -v` borra datos de la BD.

## Arquitectura de capas (obligatorio respetar)

```
Routes (app/api/routes/) → Services (app/services/) → Repositories (app/repositories/) → Models (app/models/)
```

- **Routes**: solo reciben requests, delegan a services, devuelven respuestas. Nunca `db.query()` directo.
- **Services**: lógica de negocio, validaciones complejas, orquestan repositories. Nunca `db.query()` directo.
- **Repositories**: acceso a datos, CRUD, consultas SQL. Retornan modelos ORM.
- **Schemas** (`app/schemas/`): validación Pydantic de entrada/salida.
- **Core** (`app/core/`): config, auth dependencies, seguridad, WebSocket manager.

## Convención de nombres de archivos (español con prefijos)

| Tipo | Prefijo | Ejemplo |
|------|---------|---------|
| Modelos ORM | `modelo_` | `modelo_cita.py` |
| Servicios | `servicio_` | `servicio_citas.py` |
| Repositorios | `repositorio_` | `repositorio_citas.py` |
| Schemas Pydantic | `esquema_` | `esquema_citas.py` |
| Rutas HTTP | `rutas_` | `rutas_autenticacion.py` |

## Reglas de negocio clave

- **Estados de cita válidos**: `pendiente`, `llamando`, `en_atencion`, `atendido`, `no_asistio`, `cancelada`
- Transiciones de estado están en `servicio_citas.py` — respetar el flujo definido ahí.
- `scheduled_at` no puede estar en fecha/hora pasada.
- Secretaría solo ve citas de su `programa_academico`.
- CORS permite `localhost:8080` (Flutter Web dev).

## Autenticación y roles

- JWT con access + refresh tokens.
- Dependencias en `app/core/dependencias_autenticacion.py`:
  - `require_student_role`
  - `require_secretaria_or_admin_role`
- **Orden de routers en `main.py` importa**: secretaría se registra antes que estudiante (rutas más específicas primero).

## Base de datos y migraciones

- Alembic lee `DATABASE_URL` del `.env` vía `dotenv` en `alembic/env.py`.
- Al iniciar, `main.py` ejecuta `Base.metadata.create_all()` + seed de roles y usuarios de prueba.
- `start.sh` (Docker) hace `alembic stamp head || true` antes de `upgrade head`.
- **Toda modificación de modelos requiere migración Alembic.** No borrar migraciones históricas.
- Seed automático crea: `estudiante@example.com`, `secretaria@example.com`, `admin@example.com` (password: `12345678`).

## Variables de entorno (.env)

Obligatorias: `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `FIREBASE_SERVICE_ACCOUNT_PATH`.

El archivo `sigetu-b10c0-firebase-adminsdk-fbsvc-d3c8e11eaf.json` contiene credenciales de Firebase — **no commitear**.

## Testing

No hay framework de tests configurado en este repo. Para validar cambios, usar la API interactiva en `http://localhost:8000/docs` o pruebas manuales (login → crear cita → cambio de estado).

## Lo que NO hay configurado

- No hay linter, formatter, ni typechecker configurados.
- No hay CI/CD ni pre-commit hooks.
- No hay suite de tests.

## Instrucciones relacionadas

- `.github/copilot-instructions.md` — reglas de código y convenciones del proyecto.
- `docs/STRUCTURE.md` — arquitectura detallada.
- `docs/COMMANDS.md` — referencia completa de comandos.
