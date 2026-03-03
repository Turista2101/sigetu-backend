# 🏗️ STRUCTURE - Arquitectura del proyec

Descripción detallada de cómo está organizado el código y las responsabilidades de cada carpeta.

## Distribución general

```
sigetu-backend/
├── alembic/                     # Migraciones de BD (Alembic)
│   └── versions/                # Archivos de migración
├── app/                         # Código principal de la aplicación
│   ├── api/                     # Capa de presentación (rutas HTTP/WS)
│   ├── core/                    # Configuración, seguridad, utilidades
│   ├── db/                      # Sesiones, seeds, base de datos
│   ├── models/                  # Modelos ORM (SQLAlchemy)
│   ├── repositories/            # Capa de acceso a datos
│   ├── schemas/                 # Esquemas de validación (Pydantic)
│   ├── services/                # Lógica de negocio
│   └── main.py                  # Punto de entrada (FastAPI app)
├── docs/                        # Documentación adicional
├── .env                         # Variables de entorno (no commitear)
├── .gitignore                   # Archivos ignorados por Git
├── alembic.ini                  # Configuración de Alembic
├── requirements.txt             # Dependencias Python
└── README.md                    # Información general
```

## 📁 Detalle de carpetas

### `app/main.py` - Punto de entrada

**Responsabilidad**: Crear la aplicación FastAPI e incorporar todos los routers.

```python
app = FastAPI()
app.add_middleware(CORSMiddleware, ...)
app.include_router(auth_routes.router)
app.include_router(estudiante_appointment_routes.router)
app.include_router(secretaria_appointment_routes.router)
app.include_router(appointments_ws_routes.router)

@app.on_event("startup")
def startup_event():
    # Seed de roles y usuarios por defecto
```

**Qué NO debe estar aquí:**
- Lógica de negocio (→ `services/`)
- Acceso directo a BD (→ `repositories/`)
- Validaciones complejas (→ `schemas/`)

---

## `app/api/routes/` - Capa de presentación (HTTP/WebSocket)

**Responsabilidad**: Recibir requests, validarlas, delegar a `services/` y devolver respuestas.

### Estructura:

```
api/routes/
├── auth_routes.py              # Endpoints de autenticación
├── appointments_ws_routes.py    # WebSocket para tiempo real
├── estudiante/
│   └── appointment_routes.py    # Endpoints de estudiante
└── secretaria/
    └── appointment_routes.py    # Endpoints de secretaría
```

### `auth_routes.py`

Endpoints de autenticación:
- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Login con email/password
- `POST /auth/refresh` - Renovar access token
- `POST /auth/logout` - Invalidar refresh token

```python
@router.post("/register", response_model=AuthResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register(...)
```

**Dependencias de seguridad**: Ninguna (públicos)

---

### `estudiante/appointment_routes.py`

Endpoints de citas para estudiantes:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/appointments` | Crear cita |
| GET | `/appointments/me` | Ver todas mis citas |
| GET | `/appointments/me/current` | Ver citas activas |
| GET | `/appointments/me/history` | Ver historial |
| PATCH | `/appointments/{id}` | Editar mi cita |

```python
@router.post("", response_model=AppointmentResponse)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(require_student_role),  # ← Valida rol
):
    return service.create_appointment(...)
```

**Dependencia de autenticación**: `require_student_role`

---

### `secretaria/appointment_routes.py`

Endpoints de citas para secretaría:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/appointments/queue` | Ver cola pendiente |
| GET | `/appointments/queue/history` | Ver historial atendidas |
| GET | `/appointments/{id}/detail` | Detalles de una cita |
| PATCH | `/appointments/{id}/status` | Cambiar estado |

```python
@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
def update_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(require_secretaria_or_admin_role),
):
    return service.update_status(...)
```

**Dependencia de autenticación**: `require_secretaria_or_admin_role`

---

### `appointments_ws_routes.py`

WebSocket para actualizaciones en tiempo real:

```python
@router.websocket("/ws/appointments/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    # Validar token
    # Conectar cliente
    # Mantener conexión abierta
    # Enviar eventos cuando se actualizan citas
```

Recibe eventos como:
- Nueva cita creada
- Estado cambiado
- Cita completada

---

## `app/services/` - Lógica de negocio

**Responsabilidad**: Implementar las reglas de negocio, orquestar repositorios, validaciones complejas.

### `appointment_service.py`

Servicio central para operaciones de citas:

```python
class AppointmentService:
    def __init__(self):
        self.repository = AppointmentRepository()
        self.final_statuses = {"atendido", "no_asistio", "cancelada"}
    
    # Método de creación
    def create_appointment(self, db: Session, payload: AppointmentCreate, student_email: str):
        # 1. Validar que el estudiante existe
        # 2. Validar que scheduled_at no es en el pasado
        # 3. Generar turn_number único
        # 4. Crear registro en BD
        # 5. Publicar evento en tiempo real
        
    # Métodos de consulta
    def get_student_appointments(self, db: Session, student_email: str):
        # Obtener todas las citas del estudiante
        
    def get_queue(self, db: Session, secretaria_email: str):
        # Obtener cola de citas pendientes para secretaría
        
    # Cambio de estado
    def update_status(self, db: Session, appointment_id: int, new_status: str, changed_by_email: str):
        # 1. Validar transición de estado
        # 2. Actualizar BD
        # 3. Crear histórico
        # 4. Publicar evento
```

**NO debe haber:**
- `db.query()` directo (→ repositorio)
- `db.commit()` directo (→ repositorio)
- Retorno de modelos ORM crudos (→ schemas)

---

### `auth_service.py`

Servicio de autenticación y autorización:

```python
class AuthService:
    def register(self, db: Session, full_name: str, email: str, password: str, programa_academico: str):
        # 1. Validar que email no existe
        # 2. Hash de password
        # 3. Crear usuario con rol 'estudiante'
        # 4. Retornar tokens
        
    def login(self, db: Session, email: str, password: str):
        # 1. Buscar usuario por email
        # 2. Verificar password
        # 3. Generar tokens (access + refresh)
        # 4. Retornar usuario + tokens
        
    def refresh(self, db: Session, refresh_token: str):
        # 1. Validar refresh token
        # 2. Generar nuevo access token
```

---

## `app/repositories/` - Acceso a datos

**Responsabilidad**: Operaciones CRUD sobre la BD, consultas específicas.

### `appointment_repository.py`

```python
class AppointmentRepository:
    def create(self, db: Session, appointment: Appointment) -> Appointment:
        # INSERT
        
    def get_by_id(self, db: Session, appointment_id: int) -> Appointment | None:
        # SELECT por ID
        
    def get_by_student_id(self, db: Session, student_id: int) -> list[Appointment]:
        # SELECT todas las citas de un estudiante
        
    def get_queue(self, db: Session, programa_academico: str) -> list[Appointment]:
        # SELECT citas pendientes para una secretaría
        
    def update_status(self, db: Session, appointment_id: int, new_status: str) -> Appointment:
        # UPDATE estado
        
    def next_turn_sequence(self, db: Session, sede: str, for_date: date) -> int:
        # Generar siguiente número de turno
```

### `user_repository.py`

```python
class UserRepository:
    def get_by_email(self, db: Session, email: str) -> User | None:
        # SELECT usuario por email
        
    def create(self, db: Session, user: User) -> User:
        # INSERT usuario
```

### `revoked_token_repository.py`

```python
class RevokedTokenRepository:
    def add_token(self, db: Session, token: str, expires_at: datetime):
        # Agregar token a lista negra
        
    def is_revoked(self, db: Session, token: str) -> bool:
        # Verificar si token está revocado
```

---

## `app/models/` - Modelos ORM (SQLAlchemy)

**Responsabilidad**: Definir estructura de tablas en BD.

### `user_model.py`

```python
class User(Base):
    __tablename__ = "users"
    
    id: int (PK)
    email: str (UNIQUE)
    hashed_password: str
    full_name: str
    programa_academico: str | None
    is_active: bool
    created_at: datetime
    role_id: int (FK → roles)
    
    # Relaciones
    role: Role
    appointments: list[Appointment]
```

**Tabla en BD:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    programa_academico VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT now(),
    role_id INTEGER NOT NULL REFERENCES roles(id)
);
```

---

### `appointment_model.py`

```python
class Appointment(Base):
    __tablename__ = "appointments"
    
    id: int (PK)
    student_id: int (FK → users)
    secretaria_id: int | None (FK → users)
    
    sede: str (ej: "asistencia_estudiantil")
    category: str (academico|administrativo|financiero|otro)
    context: str (descripción)
    status: str (pendiente|llamando|en_atencion|atendido|no_asistio|cancelada)
    turn_number: str (UNIQUE - ej: AE-20260303-001)
    
    created_at: datetime
    scheduled_at: datetime | None
    
    # Relaciones
    student: User
    secretaria: User | None
    
    # Checks
    CHECK status IN (...)
    CHECK category IN (...)
```

---

### `appointment_history_model.py`

```python
class AppointmentHistory(Base):
    __tablename__ = "appointment_history"
    
    # Copia de campos de Appointment
    # Más campo: archived_at
    # Para auditoría de citas finalizadas
```

---

### `role_model.py`

```python
class Role(Base):
    __tablename__ = "roles"
    
    id: int (PK)
    name: str (UNIQUE - admin|estudiante|secretaria)
    
    # Relación
    users: list[User]
```

---

### `revoked_token_model.py`

```python
class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    
    id: int (PK)
    token: str (UNIQUE)
    revoked_at: datetime
    expires_at: datetime
```

---

## `app/schemas/` - Esquemas Pydantic (validación entrada/salida)

**Responsabilidad**: Validar datos de entrada, serealizar modelos ORM para respuestas.

### `appointment_schema.py`

```python
# Entrada (request)
class AppointmentCreate(BaseModel):
    category: Literal["academico", "administrativo", "financiero", "otro"]
    context: str (min=2, max=120)
    scheduled_at: datetime | None

class AppointmentUpdate(BaseModel):
    category: CategoryType | None
    context: str | None
    scheduled_at: datetime | None

class AppointmentStatusUpdate(BaseModel):
    status: StatusType

# Salida (response)
class AppointmentResponse(BaseModel):
    id: int
    student_id: int
    student_name: str | None
    turn_number: str
    category: CategoryType
    status: StatusType
    created_at: datetime
    scheduled_at: datetime | None

class AppointmentDetailResponse(AppointmentResponse):
    # Más campos detallados
    student: AppointmentStudentInfo
    secretaria_id: int | None
```

### `user_schema.py`

```python
# Entrada
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    programa_academico: str | None

class LoginRequest(BaseModel):
    email: str
    password: str

# Salida
class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
```

---

## `app/core/` - Configuración, seguridad, utilidades

### `config.py`

Variables de entorno:

```python
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
```

### `auth_dependencies.py`

Dependencias de autenticación para rutas:

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    # Decodificar JWT y validar

def require_student_role(payload: dict = Depends(get_current_token_payload)) -> dict:
    # Validar que rol == "estudiante"

def require_secretaria_role(payload: dict = Depends(get_current_token_payload)) -> dict:
    # Validar que rol == "secretaria"

def require_secretaria_or_admin_role(payload: dict = Depends(get_current_token_payload)) -> dict:
    # Validar que rol sea "secretaria" o "admin"
```

### `security.py`

Funciones de seguridad:

```python
def hash_password(password: str) -> str:
    # Hash de contraseña con bcrypt

def verify_password(plain: str, hashed: str) -> bool:
    # Verificar contraseña

def create_access_token(data: dict, expires_in: int) -> str:
    # Generar JWT de acceso

def create_refresh_token(data: dict, expires_in: int) -> str:
    # Generar JWT de refresh
```

### `realtime.py`

Manager de WebSocket para actualizaciones en tiempo real:

```python
class AppointmentRealtimeManager:
    async def publish_appointment_event(self, event_type: str, appointment: Appointment):
        # Enviar evento a todos los clientes WebSocket conectados
```

---

## `app/db/` - Sesiones, migraciones, seeds

### `session.py`

Configuración de SQLAlchemy:

```python
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `base.py`

Base declarativa:

```python
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Todos los modelos heredan de Base
```

### `seed.py`

Datos iniciales:

```python
def seed_roles(db: Session):
    # Crear roles: admin, estudiante, secretaria

def seed_default_users(db: Session):
    # Crear usuarios de prueba
    # estudiante@example.com / 12345678
    # secretaria@example.com / 12345678
```

---

## `alembic/` - Migraciones de BD

```
alembic/
├── versions/
│   ├── bd65e13f9cbb_initial_tables.py
│   ├── 9a4d2e7b1c30_add_programa_academico_to_users.py
│   ├── 1f2c3d4e5f6a_create_appointments_table.py
│   ├── d4b7e1a9c2f6_add_secretaria_id_to_appointments.py
│   ├── e4f1a9c2d7b8_add_appointment_checks_and_queue_index.py
│   ├── b9f3c1d8a7e2_create_appointment_history_and_remove_finalizada.py
│   ├── d2c7a1f3b8e9_remove_push_and_fcm_notifications.py
│   ├── a6d8b2e4c9f1_create_fcm_device_tokens_table.py
│   ├── c31b6e2f8a44_cascade_delete_appointments_on_user_delete.py
│   ├── c8a1e3f4b7d2_create_revoked_tokens_table.py
│   ├── f7a2c9d1e4b3_create_push_subscriptions_table.py
│   └── __pycache__/
├── env.py                 # Configuración de Alembic
├── script.py.mako         # Template para nuevas migraciones
└── README
```

**Cada archivo es una migración:**
```python
def upgrade():
    # Hacia adelante (SQL)
    
def downgrade():
    # Hacia atrás (rollback)
```

---

## Flujo de una petición típica

```
1. Cliente envía request
   POST /appointments
   Header: Authorization: Bearer token

2. FastAPI → auth_dependencies.py
   Valida JWT → extrae student_id

3. Ruta (estudiante/appointment_routes.py)
   Valida payload (Pydantic)
   Llama: service.create_appointment(...)

4. Service (services/appointment_service.py)
   - Valida reglas de negocio
   - Llama: repository.create(...)
   - Publica evento WebSocket

5. Repository (repositories/appointment_repository.py)
   - Ejecuta INSERT en BD
   - Retorna modelo ORM

6. Service
   - Convierte ORM → Schema (Pydantic)

7. Ruta
   - Retorna response HTTP 200
   - FastAPI serializa Schema → JSON
```

---

## Diagrama de dependencias

```
routes (HTTP/WS)
    ↓
services (lógica)
    ├→ repositories (BD)
    ├→ schemas (validación)
    └→ core.realtime (WebSocket)
    
models (ORM)
    ↓ usados por
repositories (consultas)
    
core.auth_dependencies
    ↓ usado por
routesmigrations (Alembic)
    ↓ generan
models (tablas)
```

---

## Resumen de responsabilidades

| Carpeta | Responsabilidad |
|---------|-----------------|
| `routes/` | Recibir requests, validar entrada, delegar |
| `services/` | Lógica de negocio, orquestar BD |
| `repositories/` | Consultas SQL, CRUD |
| `models/` | Estructura de tablas |
| `schemas/` | Validación Pydantic |
| `core/` | Config, auth, utilidades|
| `db/` | Sesiones, seeds |
| `alembic/` | Control de versiones de BD |

---

## Claves de arquitectura

✅ **Hacer:**
- Lógica de negocio en `services/`
- Consultas en `repositories/`
- Validación en `schemas/`
- Seguridad en `core/auth_dependencies.py`

❌ **Evitar:**
- `db.query()` en rutas
- Lógica de BD en servicios
- Modelos ORM en respuestas
- Cambios de esquema sin migración

---

Más detalles: Ver [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) y [CONTRIBUTING.md](CONTRIBUTING.md)
