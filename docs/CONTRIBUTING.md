# 🤝 CONTRIBUTING - Guía para contribuidores

Instrucciones para desarrolladores que quieren contribuir o trabajar en SIGETU Backend.

## 🎯 Principios del proyecto

Este proyecto sigue una arquitectura de **capas bien definidas** con responsabilidades claras:

1. **Routes** (`api/routes/`): Reciben requests, validan entrada, delegan a servicios
2. **Services** (`services/`): Lógica de negocio, validaciones complejas
3. **Repositories** (`repositories/`): Acceso a datos, consultas SQL
4. **Models** (`models/`): Definición de tablas (ORM)
5. **Schemas** (`schemas/`): Validación de entrada/salida (Pydantic)

**La regla de oro**: Cada capa hace UNA cosa bien.

---

## 🚦 Workflow de desarrollo

### 1. Crear rama featureprincipiante

```powershell
# Actualizar main
git checkout main
git pull origin main

# Crear rama
git checkout -b feature/nombre-descriptivo

# Ejemplos:
# feature/estudiante-edit-appointment
# feature/secretaria-queue-filter
# fix/jwt-validation-error
```

### 2. Hacer cambios

```powershell
# Con Docker (recomendado)
docker-compose up -d
docker-compose logs -f api

# Sin Docker
# Instalar dependencias si es necesario
pip install -r requirements.txt

# Activar venv
.\venv\Scripts\Activate.ps1

# Iniciar servidor
uvicorn app.main:app --reload
```

### 3. Probar localmente

```powershell
# Acceder a documentación interactiva
# http://localhost:8000/docs

# Probar endpoints
# Registrar usuario → Login → Crear cita

# Si hay cambios en modelos:
python -m alembic revision --autogenerate -m "descripción"
python -m alembic upgrade head
```

### 4. Commit y push

```powershell
# Ver cambios
git status
git diff

# Agregar cambios
git add .

# Commit (mensajes en tiempo presente)
git commit -m "feat: agregar filtro de categoría a cola"

# Push
git push origin feature/nombre-descriptivo
```

### 5. Crear Pull Request

En GitHub:
1. Abre PR desde tu rama a `main`
2. Descripción breve de cambios
3. Mención de issues relacionados (si existen)

---

## 📋 Checklist antes de hacer commit

Antes de hacer push, verifica:

- [ ] **Cambios enfocados**: ¿Este PR hace UNA cosa bien?
- [ ] **Lógica en services**: ¿La lógica de negocio quedó en `services/`?
- [ ] **BD en repositories**: ¿Las consultas están en `repositories/`?
- [ ] **Validación en schemas**: ¿La validación Pydantic está presente?
- [ ] **Rutas limpias**: ¿Las rutas solo orquestan?
- [ ] **Migraciones**: ¿Si cambié modelo, hice migración?
- [ ] **Tests locales**: ¿Probé manualmente el flujo principal?
- [ ] **Mensajes claros**: ¿El commit message es descriptivo?
- [ ] **Sin hardcoding**: ¿No hay secretos o valores fijos?

---

## 📝 Convenciones de código

### Nombres de archivos

```python
# Archivos de entidades (nomenclatura en español)
modelo_usuario.py               # Modelo ORM
esquema_usuario.py             # Schema Pydantic
repositorio_usuario.py         # Acceso a datos
servicio_autenticacion.py      # Servicio de autenticación
rutas_autenticacion.py         # Rutas HTTP
rutas_notificaciones.py        # Rutas de notificaciones FCM
rutas_ws_citas.py             # WebSocket de citas

# Convención: snake_case, sufijos descriptivos, español
```

### Nombres de variables

```python
# Local
appointment_id: int
student_email: str
is_active: bool

# Función
def create_appointment(...):
def get_student_appointments(...):
def update_appointment_status(...):

# Constante
final_statuses = {"atendido", "no_asistio", "cancelada"}
```

### Comentarios

```python
# ✅ Explicar el POR QUÉ
def validate_scheduled_at(scheduled_at: datetime):
    """
    scheduled_at no puede ser en el pasado
    porque los estudiantes no pueden reservar sesiones pasadas.
    """
    if scheduled_at < datetime.utcnow():
        raise HTTPException(...)

# ❌ No explicar el QUÉ es obvio
def validate_scheduled_at(scheduled_at: datetime):
    # Comparar scheduled_at menor que ahora
    if scheduled_at < datetime.utcnow():
        raise HTTPException(...)
```

### Docstrings

```python
def create_appointment(
    db: Session,
    payload: AppointmentCreate,
    student_email: str
) -> Appointment:
    """
    Crear una nueva cita académica.
    
    Args:
        db: Sesión de BD
        payload: Datos de la cita (categoría, contexto, scheduled_at)
        student_email: Email del estudiante
        
    Returns:
        Appointment: Cita creada con ID y turn_number asignado
        
    Raises:
        HTTPException 404: Si el estudiante no existe
        HTTPException 400: Si scheduled_at está en el pasado
    """
    ...
```

---

## 🧪 Flujo de trabajo típico: Agregar nuevo endpoint

### Paso 1: Definir schema en `app/schemas/`

```python
# esquema_cita.py
class NuevoEndpointRequest(BaseModel):
    param1: str
    param2: int | None = None

class NuevoEndpointResponse(BaseModel):
    id: int
    result: str
```

### Paso 2: Agregar método en `app/services/`

```python
# servicio_cita.py
class ServicioCita:
    def nueva_logica_negocio(self, db: Session, param1: str) -> dict:
        """Lógica de negocio aquí."""
        # Validaciones
        if not param1:
            raise HTTPException(status_code=400, detail="...")
        
        # Llamar a repository
        result = self.repositorio.hacer_algo(db, param1)
        
        # Publicar evento si corresponde
        self._publicar_evento_tiempo_real("tipo_evento", objeto)
        
        return result
```

### Paso 3: Agregar consulta en `app/repositories/`

```python
# repositorio_cita.py
class RepositorioCita:
    def hacer_algo(self, db: Session, param1: str) -> dict:
        """Consulta a BD."""
        result = db.query(Appointment).filter(
            Appointment.name == param1
        ).first()
        
        if not result:
            return None
            
        return result
```

### Paso 4: Exponer en ruta `app/api/routes/`

```python
# estudiante/rutas_cita.py
@router.post("/nuevo-endpoint", response_model=NuevoEndpointResponse)
def nuevo_endpoint(
    payload: NuevoEndpointRequest,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(require_student_role),
):
    """Endpoint description para Swagger."""
    return servicio.nueva_logica_negocio(
        db=db,
        param1=payload.param1
    )
```

### Paso 5: Si cambió modelo, crear migración

```powershell
# Con Docker
docker-compose exec api python -m alembic revision --autogenerate -m "agregar nueva columna X"
docker-compose exec api python -m alembic upgrade head

# Sin Docker
python -m alembic revision --autogenerate -m "agregar nueva columna X"
python -m alembic upgrade head
```

---

## 🔴 Antipatrones a evitar

### ❌ Lógica de BD en rutas

```python
# ❌ MAL
@router.post("/appointments")
def create(payload: AppointmentCreate, db: Session):
    appointment = Appointment(student_id=1, ...)
    db.add(appointment)           # ← DB aquí
    db.commit()                   # ← DB aquí
    return appointment
```

```python
# ✅ BIEN
@router.post("/appointments")
def create(payload: AppointmentCreate, db: Session, token_payload: dict):
    return service.create_appointment(
        db=db,
        payload=payload,
        student_email=token_payload["sub"]
    )
```

### ❌ Lógica de negocio en repository

```python
# ❌ MAL
class AppointmentRepository:
    def create(self, db, payload):
        # Validar scheduled_at
        if payload.scheduled_at < datetime.utcnow():  # ← Lógica aquí
            raise HTTPException(...)
        
        appointment = Appointment(...)
        db.add(appointment)
        db.commit()
```

```python
# ✅ BIEN
class AppointmentService:
    def create_appointment(self, db, payload, student_email):
        # Validaciones
        self._validate_scheduled_at(payload.scheduled_at)
        
        # BD
        return self.repository.create(db, appointment)
```

### ❌ Retornar modelos ORM en respuestas

```python
# ❌ MAL
@router.get("/appointments")
def get_appointments(db: Session):
    appointments = db.query(Appointment).all()
    return appointments  # ← ORM directo, expone contraseñas, etc.
```

```python
# ✅ BIEN
@router.get("/appointments", response_model=list[AppointmentResponse])
def get_appointments(db: Session):
    appointments = service.get_appointments(db)
    # FastAPI convierte automáticamente a AppointmentResponse (Pydantic)
    return appointments
```

### ❌ Cambiar estructura sin migración

```python
# ❌ MAL
class User(Base):
    new_required_field = Column(String, nullable=False)  # ← Sin migración

# ✅ BIEN
# 1. Ejecutar: python -m alembic revision --autogenerate -m "agregar campo"
# 2. Editar migración si es necesario
# 3. Ejecutar: python -m alembic upgrade head
```

---

## 🔐 Validaciones obligatorias

### Autenticación

```python
from app.core.auth_dependencies import require_student_role, require_secretaria_role

@router.post("/...")
def endpoint(
    ...,
    token_payload: dict = Depends(require_student_role)  # ← Validar rol
):
    # El endpoint solo es accesible por estudiantes
    # token_payload contiene: {sub: email, role: role, ...}
    pass
```

### Validación de entrada

```python
from pydantic import BaseModel, StringConstraints
from typing import Annotated

class MySchema(BaseModel):
    name: Annotated[str, StringConstraints(min_length=2, max_length=50)]
    email: EmailStr
    category: Literal["A", "B", "C"]
```

### Errores HTTP claros

```python
from fastapi import HTTPException

# ✅ Mensaje claro en español
if not user:
    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )

if user.status != "active":
    raise HTTPException(
        status_code=403,
        detail="Usuario inactivo"
    )
```

---

## 📊 Estándares de bases de datos

### Nombres de tablas

```sql
-- Snake case, plurales
users
appointments
roles
appointment_history
revoked_tokens
```

### Nombres de columnas

```sql
-- Snake case
student_id
created_at
is_active
programa_academico
```

### Constraints

```python
# Checks en modelo ORM
class Appointment(Base):
    __table_args__ = (
        CheckConstraint(
            "status IN ('pendiente','llamando','en_atencion','atendido','no_asistio','cancelada')",
            name="ck_appointments_status_valid",
        ),
    )
```

### Índices

```python
# Para optimizar queries frecuentes
Index("ix_appointments_sede_status_created_at", "sede", "status", "created_at")
```

---

## 🧑‍⚕️ Review checklist (para revisor)

- [ ] ¿El PR resuelve un issue específico?
- [ ] ¿La lógica está en el lugar correcto (services/repos)?
- [ ] ¿Hay validaciones de entrada?
- [ ] ¿Los errores son descriptivos?
- [ ] ¿Hay migraciones si cambió modelo?
- [ ] ¿Nombres consistentes con el proyecto?
- [ ] ¿Funciona con rol/permisos apropiados?
- [ ] ¿WebSocket actualizado si es necesario?
- [ ] ¿Tests pasadosási hay tests)?

---

## 🐛 Reportar bugs

Si encuentras un bug:

1. Abre un issue en GitHub
2. Título descriptivo: "Bug: emails vacíos al crear usuario"
3. Descripción:
   - Pasos para reproducir
   - Resultado esperado
   - Resultado actual
   - Stack trace si hay error

Ejemplo:
```
## Steps to reproduce
1. POST /auth/register
2. email: "" (vacío)

## Expected
Error 422 con detalle claro

## Actual
Error 500 - Internal Server Error

## Stack trace
...
```

---

## 💡 Proponer features

Si quieres proponer una funcionalidad:

1. Abre issue con etiqueta `enhancement`
2. Descripción clara de la feature
3. Casos de uso
4. Cómo se alinea con la arquitectura existente

---

## 📚 Recursos

- [STRUCTURE.md](STRUCTURE.md) - Entiende antes de cambiar
- [QUICKSTART.md](QUICKSTART.md) - Setup inicial
- [COMMANDS.md](COMMANDS.md) - Comandos útiles
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Visión completa

---

## ✨ Buen comportamiento del código

```python
# Buena práctica: Claro, enfocado, mantenible
class AppointmentService:
    def create_appointment(
        self,
        db: Session,
        payload: AppointmentCreate,
        student_email: str,
    ) -> Appointment:
        """
        Crear una nueva cita académica para un estudiante.
        
        Valida que:
        - El estudiante existe
        - La fecha agendada no es en el pasado
        - Genera un turn_number único
        """
        # 1. Validar precondiciones
        student = self._get_student_or_raise(db, student_email)
        self._validate_scheduled_at(payload.scheduled_at)
        
        # 2. Generar datos
        turn_number = self._generate_turn_number(db)
        
        # 3. Persistir
        appointment = Appointment(
            student_id=student.id,
            category=payload.category,
            context=payload.context,
            scheduled_at=payload.scheduled_at,
            turn_number=turn_number,
            status="pendiente",
        )
        persisted = self.repository.create(db, appointment)
        
        # 4. Notificar
        self._publish_realtime_event("appointment_created", persisted)
        
        return persisted
```

---

## 🎓 Aprendizaje: Arquitectura de capas

```
┌─── ROUTE (HTTP/WS) ──────────────────────┐
│ Recibir request                          │
│ Validar con Pydantic (schema)            │
│ Delegar a service                        │
│ Retornar respuesta serializada           │
└─────────────────────────────────────────┘

┌─── SERVICE (Lógica) ──────────────────────┐
│ Orquestar validaciones                    │
│ Implementar reglas de negocio             │
│ Llamar a repositories                     │
│ Publicar eventos                          │
│ Retornar datos (no ORM)                   │
└─────────────────────────────────────────┘

┌─── REPOSITORY (Datos) ───────────────────┐
│ Construir queries                         │
│ Ejecutar CRUD                             │
│ Retornar modelos ORM                      │
└─────────────────────────────────────────┘

┌─── MODEL (ORM) ─────────────────────────┐
│ Mapear tablas a clases                   │
│ Definir relaciones                       │
│ Setear constraints                       │
└─────────────────────────────────────────┘

┌─── SCHEMA (Validación) ──────────────────┐
│ Validar entrada (request)                │
│ Serializar salida (response)             │
│ Documentar en Swagger                    │
└─────────────────────────────────────────┘
```

---

## ¿Preguntas frecuentes?

**P: ¿Dónde pongo la validación X?**  
R: En `schemas/` con Pydantic si es simple, en `services/` si es lógica compleja.

**P: ¿Cómo agrego roles nuevos?**  
R: Modificar `Role` en modelos, crear migración, actualizar dependencias de auth.

**P: ¿Puedo cambiar nombre de endpoint?**  
R: Solo si hay acuerdo del equipo (API pública), mejor crear nuevo y deprecar.

**P: ¿Dónde documentar casos especiales?**  
R: En docstrings de funciones en `services/`, con ejemplos si es relevante.

---

¡Gracias por contribuir! 🙌
