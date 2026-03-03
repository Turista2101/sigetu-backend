# 📋 PROJECT_SUMMARY - Visión general del proyecto

Descripción completa del SIGETU Backend, funcionalidades, arquitectura y decisiones técnicas.

## 🎯 Propósito del proyecto

**SIGETU Backend** es un sistema de gestión de citas académicas que permite:

1. **Estudiantes**:
   - Crear nuevas citas con especificación de categoría (académica, administrativa, financiera, otra)
   - Consultar sus citas actuales y ver historial
   - Editar o cancelar sus propias citas
   - Recibir actualizaciones en tiempo real del estado de sus citas

2. **Secretaría**:
   - Ver cola de citas pendientes de atención
   - Cambiar estado de citas (llamando → en atención → atendido/no asistió)
   - Asignar citas a sí mismos
   - Ver historial de citas atendidas
   - Recibir notificaciones en tiempo real de nuevas citas

3. **Administración**:
   - Gestión de usuarios y roles
   - Auditoría de cambios

## 🏗️ Arquitectura

### Patrón de capas

```
┌─────────────────────────────┐
│    HTTP/WebSocket Layer     │ ← app/api/routes/
├─────────────────────────────┤
│    Business Logic Layer     │ ← app/services/
├─────────────────────────────┤
│    Data Access Layer        │ ← app/repositories/
├─────────────────────────────┤
│    ORM Layer                │ ← app/models/
├─────────────────────────────┤
│    Database (PostgreSQL)    │
└─────────────────────────────┘
```

### Características arquitectónicas

- **Separación de responsabilidades**: Cada capa tiene un propósito específico
- **Inyección de dependencias**: FastAPI gestiona sesiones de BD automáticamente
- **Validación con Pydantic**: Esquemas validan entrada/salida
- **JWT para autenticación**: Access + Refresh tokens
- **WebSockets para actualización**: Eventos en tiempo real
- **Alembic para migraciones**: Control de versiones de BD
- **Rollback seguro**: Transacciones en BD

---

## 🗄️ Modelo de datos

### Entidades principales

```
┌─────────────┐              ┌───────────────────────┐
│    User     │◄─────────────│   Appointment        │
├─────────────┤              ├───────────────────────┤
│ id (PK)     │              │ id (PK)               │
│ email       │              │ student_id (FK)       │
│ password    │              │ secretaria_id (FK)    │
│ full_name   │              │ category              │
│ role_id     │              │ status                │
│ programa    │              │ turn_number (UNIQUE)  │
│ is_active   │              │ created_at            │
└─────────────┘              │ scheduled_at          │
      ▲                      └───────────────────────┘
      │                               │
      └──────────────────────┬─────────┘
                             │
                    ┌────────▼──────────┐
                    │ AppointmentHistory│
                    ├──────────────────┤
                    │ id (PK)          │
                    │ student_id (FK)  │
                    │ ... (copias)     │
                    │ archived_at      │
                    └──────────────────┘
```

### Tabla: `users`

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    programa_academico VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    role_id INTEGER NOT NULL REFERENCES roles(id)
);
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | int | ID único (PK) |
| `email` | str | Email único |
| `hashed_password` | str | Password hasheada con bcrypt |
| `full_name` | str | Nombre completo |
| `programa_academico` | str | Ej: "ingenierias", "derecho" |
| `is_active` | bool | Estado activo/inactivo |
| `role_id` | int | FK a tabla `roles` |

---

### Tabla: `appointments`

```sql
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    secretaria_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    sede VARCHAR(80) DEFAULT 'asistencia_estudiantil',
    category VARCHAR(30) NOT NULL,
    context VARCHAR(120) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pendiente',
    turn_number VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    scheduled_at TIMESTAMP,
    
    CHECK (status IN ('pendiente','llamando','en_atencion','atendido','no_asistio','cancelada')),
    CHECK (category IN ('academico','administrativo','financiero','otro')),
    
    INDEX (sede, status, created_at)
);
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `student_id` | int | Estudiante que solicita (FK) |
| `secretaria_id` | int | Secretaría asignada (nullable) |
| `categoria` | str | academico, administrativo, financiero, otro |
| `context` | str | Descripción de la consulta (max 120 chars) |
| `status` | str | Estado actual (ver máquina de estados) |
| `turn_number` | str | Número de turno único (ej: AE-20260303-001) |
| `scheduled_at` | datetime | Fecha/hora agendada (opcional) |

---

### Máquina de estados de citas

```
┌──────────┐
│ pendiente│ ← Nueva cita creada
└────┬─────┘
     │
     ▼
┌──────────┐
│ llamando │ ← Secretaría llama
└────┬─────┘
     │
     ▼
┌──────────────┐
│ en_atencion  │ ← Estudiante presente
└─┬──────────┬─┘
  │          │
  ▼          ▼
┌────────┐ ┌────────────┐
│atendido│ │no_asistio  │ ← Resultado
└────────┘ └────────────┘

En cualquier estado previo a "atendido":
  └──────────────┬──────────────────┐
                 ▼                  ▼
             ┌──────────┐      ┌──────────┐
             │cancelada │      │ terminado│
             └──────────┘      └──────────┘
```

**Estados y transiciones válidas:**

| Desde | Hacia | Quién | Condición |
|-------|-------|-------|-----------|
| `pendiente` | `llamando` | Secretaría | Siempre |
| `llamando` | `en_atencion` | Secretaría | Siempre |
| `en_atencion` | `atendido` | Secretaría | Siempre |
| `en_atencion` | `no_asistio` | Secretaría | Si no llega |
| Cualquiera | `cancelada` | Estudiante o Secretaría | Antes de `atendido` |

---

## 🔐 Sistema de autenticación y autorización

### Roles

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| `estudiante` | Usuario estándar | Ver/crear/editar sus propias citas |
| `secretaria` | Gestiona cola | Ver cola, cambiar estados, ver historial |
| `admin` | Administrador | Todo (no implementado aún) |

### Flujo de autenticación

```
1. Registro (opcional)
   POST /auth/register
   {email, password, full_name, programa_academico}
   ├→ Crear usuario con rol "estudiante"
   └→ Retornar tokens

2. Login
   POST /auth/login
   {email, password}
   ├→ Validar credenciales
   ├→ Generar access_token (JWT)
   ├→ Generar refresh_token (JWT)
   └→ Retornar {access_token, refresh_token, user}

3. Usar token
   GET /appointments/me
   Header: Authorization: Bearer {access_token}
   ├→ Validar JWT
   └→ Retornar datos

4. Renovar token
   POST /auth/refresh
   {refresh_token}
   ├→ Validar refresh_token
   ├→ Generar nuevo access_token
   └→ Retornar nuevo access_token

5. Logout
   POST /auth/logout
   {refresh_token}
   ├→ Agregar refresh_token a lista negra
   └→ Retornar {message}
```

### Tokens JWT

**Access Token**:
- Duración: 7 días (configurable)
- Validez: 5 minutos antes de expiración (recomendado)
- Payload: `{sub: email, role: role, token_type: "access", exp: ...}`

**Refresh Token**:
- Duración: 7 días (configurable)
- Payload: `{sub: email, token_type: "refresh", exp: ...}`

### Validación de permisos por ruta

```python
# Para estudiantes
@router.post("", response_model=AppointmentResponse)
def create_appointment(
    ...,
    token_payload: dict = Depends(require_student_role),  # ← Valida rol
):
    ...

# Para secretaría
@router.patch("/{appointment_id}/status")
def update_status(
    ...,
    token_payload: dict = Depends(require_secretaria_or_admin_role),  # ← Valida rol
):
    ...
```

---

## 📡 API REST

### Endpoints de autenticación

```
POST   /auth/register          Registrar nuevo usuario
POST   /auth/login            Login (email/password)
POST   /auth/refresh          Renovar access_token
POST   /auth/logout           Invalidar refresh_token
```

### Endpoints de estudiante

```
POST   /appointments                      Crear cita
GET    /appointments/me                  Ver todas mis citas
GET    /appointments/me/current           Ver citas activas
GET    /appointments/me/history          Ver historial
PATCH  /appointments/{appointment_id}    Editar mi cita
```

### Endpoints de secretaría

```
GET    /appointments/queue              Ver cola de citas
GET    /appointments/queue/history      Ver historial atendidas
GET    /appointments/{appointment_id}/detail   Ver detalles
PATCH  /appointments/{appointment_id}/status   Cambiar estado
```

### WebSocket

```
WS     /ws/appointments/{token}    Conectar a actualizaciones en tiempo real
```

Eventos que se reciben:
```json
{
  "event_type": "appointment_created|status_changed|appointment_finished",
  "data": {
    "appointment_id": 123,
    "status": "llamando",
    "turn_number": "AE-20260303-001",
    ...
  }
}
```

---

## 🛠️ Stack Técnico

### Backend
- **FastAPI 0.131.0** - Framework web moderno, async
- **Uvicorn** - Servidor ASGI
- **SQLAlchemy 2.0.46** - ORM para Python
- **Psycopg2 2.9.11** - Driver PostgreSQL
- **Pydantic 2.12.5** - Validación de datos
- **Alembic 1.18.4** - Migraciones de BD

### Autenticación
- **python-jose 3.5.0** - JWT
- **bcrypt 3.2.2** - Hashing de passwords
- **passlib 1.7.4** - Password management

### Utilidades
- **python-dotenv 1.2.1** - Variables de entorno
- **python-multipart 0.0.22** - Multipart form data
- **Sentry 2.53.3** - Error tracking (opcional)

---

## 📊 Datos de prueba (seeds)

Al iniciar, se crean automáticamente:

**Roles:**
- `admin`
- `estudiante`
- `secretaria`

**Usuarios de prueba:**
- Email: `estudiante@example.com` | Password: `12345678` | Rol: estudiante
- Email: `secretaria@example.com` | Password: `12345678` | Rol: secretaria

Ver: `app/db/seed.py`

---

## 🔄 Ciclo de vida de una cita

```
1. CREACIÓN
   └─ Estudiante → POST /appointments
      └─ Service valida schedulet_at no sea en el pasado
      └─ Service genera turn_number único
      └─ BD: INSERT → appointments
      └─ WebSocket: publish "appointment_created"

2. LLAMADA
   └─ Secretaría → PATCH /appointments/{id}/status
      └─ Cambiar status: pendiente → llamando
      └─ BD: UPDATE → appointments
      └─ WebSocket: publish "status_changed"

3. ATENCIÓN
   └─ Secretaría → PATCH /appointments/{id}/status
      └─ Cambiar status: llamando → en_atencion
      └─ BD: UPDATE → appointments
      └─ WebSocket: publish "status_changed"

4. FINALIZACIÓN
   └─ Secretaría → PATCH /appointments/{id}/status
      └─ Cambiar status: en_atencion → atendido/no_asistio
      └─ BD: UPDATE → appointments
      └─ BD: INSERT → appointment_history (copia + archived_at)
      └─ WebSocket: publish "appointment_finished"

5. CANCELACIÓN (en cualquier momento antes)
   └─ Estudiante/Secretaría → PATCH
      └─ Cambiar status: * → cancelada
      └─ BD: UPDATE → appointments
      └─ WebSocket: publish "appointment_cancelled"
```

---

## 🎯 Decisiones de diseño

### ¿Por qué WebSockets?
- Actualización en tiempo real sin polling
- Menor latencia en notificaciones
- Mejor UX para observar cambios de estado

### ¿Por qué separar roles en rutas?
```
estudiante/appointment_routes.py
secretaria/appointment_routes.py
```
- Validación temprana (antes de la lógica)
- Endpoints específicos para cada rol
- Mejor documentación en `/docs`

### ¿Por qué turn_number único?
```
AE-20260303-001
├─ AE = sede (asistencia_estudiantil)
├─ 20260303 = fecha (YYYYMMDD)
└─ 001 = secuencia del día
```
- Identificación visual para usuarios
- Ordenable por fecha
- Evita duplicados (UNIQUE constraint)

### ¿Por qué AppointmentHistory?
- Auditoría de citas completadas
- No borrar histórico de citas finalizadas
- Consultas rápidas en cola actual (appointments vs history)

### ¿Por qué Alembic?
- Control de versiones de BD
- Rollback seguro
- Documentación de cambios
- Reproducible en cualquier entorno

---

## 📈 Casos de uso principales

### Caso 1: Estudiante crea cita

```
Actor: Estudiante (email: estud@example.com)
Precondición: Autenticado, token válido

1. POST /appointments
   Body: {category: "academico", context: "Consulta sobre...", scheduled_at: null}
   Header: Authorization: Bearer {token}

2. Service valida:
   - ¿Estudiante existe?
   - ¿scheduled_at está en el futuro (si no es null)?

3. Service genera turn_number: AE-20260303-037

4. BD: INSERT en appointments
   status = "pendiente", created_at = NOW()

5. WebSocket: envía a todas las secretarías
   {event: "appointment_created", data: {...}}

6. Response: 201 Created {id, turn_number, status, ...}
```

### Caso 2: Secretaría ve cola

```
Actor: Secretaría (email: secretaria@example.com)
Precondición: Autenticado, programa_academico != null

1. GET /appointments/queue
   Header: Authorization: Bearer {token}

2. Service obtiene:
   SELECT * FROM appointments
   WHERE status IN ('pendiente', 'llamando', 'en_atencion')
   AND fecha_programa_academico = secretaria.programa_academico
   ORDER BY created_at ASC

3. Response: 200 OK [appointment, appointment, ...]
```

### Caso 3: Secretaría actualiza estado

```
Actor: Secretaría
Entrada: appointment_id = 123, new_status = "en_atencion"

1. PATCH /appointments/123/status
   Body: {status: "en_atencion"}

2. Service valida transición: pendiente → en_atencion ✓

3. BD: UPDATE appointments SET status = "en_atencion"

4. WebSocket: envía a todas las conexiones
   {event: "status_changed", data: {...}}

5. Response: 200 OK {id: 123, status: "en_atencion", ...}
```

---

## 🔍 Validaciones de negocio

1. **Creación de cita**:
   - `scheduled_at` no puede ser fecha pasada
   - `category` debe estar en enum
   - `context` entre 2 y 120 caracteres

2. **Cambio de estado**:
   - Solo transiciones válidas
   - Solo rol secretaría puede cambiar

3. **Edición de cita**:
   - Solo el estudiante propietario
   - Solo si status == "pendiente"

4. **Cancelación**:
   - Solo si status != "atendido" y != "no_asistio"
   - Solo propietario o admin

---

## 🚀 Características futuras

- [ ] Notificaciones push (FCM)
- [ ] Recordatorios por email
- [ ] Reporte de estadísticas
- [ ] Integración con calendario (Google, Outlook)
- [ ] Multi-idioma
- [ ] Rate limiting
- [ ] Caché con Redis
- [ ] Panel de admin

---

## 📚 Referencias

- [STRUCTURE.md](STRUCTURE.md) - Estructura detallada de carpetas
- [QUICKSTART.md](QUICKSTART.md) - Instalación rápida
- [COMMANDS.md](COMMANDS.md) - Comandos útiles
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guía para desarrolladores

