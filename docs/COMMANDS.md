# 💻 COMMANDS - Comandos útiles para desarrollo

Referencia de comandos para instalar, ejecutar, debuggear y administrar el proyecto.

## 🚀 Inicio rápido

### Activar entorno virtual

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
.\venv\Scripts\activate.bat

# Linux/Mac bash
source venv/bin/activate
```

### Iniciar servidor en desarrollo

```powershell
# Con hot-reload (recompila cambios automáticamente)
uvicorn app.main:app --reload

# Sin reload
uvicorn app.main:app

# Con configuración avanzada
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

**Resultado esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

Luego accede a:
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternate Docs (ReDoc)**: http://localhost:8000/redoc

---

## 📦 Gestión de dependencias

### Instalar todas las dependencias

```powershell
pip install -r requirements.txt
```

### Agregar una nueva dependencia

```powershell
# 1. Instalar el paquete
pip install nombre-del-paquete

# 2. Actualizar requirements.txt
pip freeze > requirements.txt

# 3. Commitear cambios
git add requirements.txt
git commit -m "feat: agregar paquete X"
```

### Ver versiones instaladas

```powershell
pip list
pip show nombre-del-paquete
```

### Crear requirements limpio (sin versiones exactas)

```powershell
# Para desarrollo
pip install pipreqs
pipreqs --force .
```

---

## 🗄️ Migraciones de base de datos (Alembic)

### Ver estado actual

```powershell
python -m alembic current
```

Muestra el ID de la migración actual en BD.

### Aplicar todas las migraciones

```powershell
# Aplicar todas pendientes
python -m alembic upgrade head

# Mostrar qué se va a ejecutar (sin ejecutar)
python -m alembic upgrade head --sql
```

### Revertir última migración

```powershell
python -m alembic downgrade -1

# Revertir N migraciones
python -m alembic downgrade -3
```

### Ver histórico de migraciones

```powershell
python -m alembic history --verbose

# Salida:
# <base> -> bd65e13f9cbb (head), initial_tables
#   - crea tabla users, roles
# bd65e13f9cbb -> 9a4d2e7b1c30, add_programa_academico_to_users
#   - agrega programa_academico a users
```

### Crear nueva migración

```powershell
# Auto-generar basado en cambios de modelos
python -m alembic revision --autogenerate -m "descripcion_del_cambio"

# Ejemplo:
python -m alembic revision --autogenerate -m "add_phone_to_users"

# Manual (sin auto-generar)
python -m alembic revision -m "descripcion"
```

Luego edita el archivo en `alembic/versions/` y ejecuta:
```powershell
python -m alembic upgrade head
```

### Iniciar desde cero

```powershell
# ⚠️ CUIDADO: Elimina todas las tablas
python -m alembic downgrade base

# Luego:
python -m alembic upgrade head
```

### Debug de SQL generado

```powershell
# Ver SQL sin ejecutar
python -m alembic upgrade head --sql

# Ver SQL y detalle
python -m alembic history --verbose
```

---

## 🗄️ Base de datos PostgreSQL

### Conectar a la BD

```powershell
# Desde PowerShell
psql -U postgres -d sigetu

# Luego dentro de psql:
\dt                    # Ver todas las tablas
\d appointments        # Ver estructura de tabla
SELECT * FROM users;   # Consulta
\q                     # Salir
```

### Crear base de datos

```powershell
# Opción 1: Directamente
psql -U postgres -c "CREATE DATABASE sigetu;"

# Opción 2: Dentro de psql
psql -U postgres
> CREATE DATABASE sigetu;
> \l               # Listar BDs
> \c sigetu        # Conectar a BD
```

### Resetear BD completamente

```powershell
# ⚠️ Elimina toda la BD
psql -U postgres -c "DROP DATABASE sigetu;"
psql -U postgres -c "CREATE DATABASE sigetu;"

# Luego:
python -m alembic upgrade head
```

### Exportar/Importar datos

```powershell
# Exportar en SQL
pg_dump -U postgres sigetu > backup.sql

# Exportar en custom format (más compacto)
pg_dump -U postgres -Fc sigetu > backup.dump

# Importar
psql -U postgres -d sigetu < backup.sql

# O format custom:
pg_restore -U postgres -d sigetu backup.dump
```

---

## 🔐 Gestión de usuario de BD

### Ver usuarios

```powershell
psql -U postgres
> \du               # Ver usuarios
> SELECT * FROM pg_user;
```

### Crear usuario

```powershell
psql -U postgres -c "CREATE USER dev WITH PASSWORD 'mi_password';"
```

### Dar permisos

```powershell
psql -U postgres
> GRANT ALL PRIVILEGES ON DATABASE sigetu TO dev;
> GRANT ALL ON SCHEMA public TO dev;
```

### Resetear password

```powershell
psql -U postgres
> ALTER USER postgres WITH PASSWORD 'nueva_password';
```

---

## 🧪 Testing (si se implementa)

### Ejecutar tests

```powershell
# Con pytest
pytest

# Con verbose
pytest -v

# Un archivo específico
pytest tests/test_auth.py

# Una función específica
pytest tests/test_auth.py::test_login -v
```

### Coverage

```powershell
pytest --cov=app
```

---

## 🐛 Debugging

### Ver logs del servidor

Con `--log-level debug`:
```powershell
uvicorn app.main:app --reload --log-level debug
```

Salida:
```
DEBUG:     Server running on http://127.0.0.1:8000
DEBUG:     Uvicorn running on http://127.0.0.1:8000
DEBUG:     Started server process
DEBUG:     Application startup complete
```

### Usar pdb (Python Debugger)

```python
# En tu código
def create_appointment(db: Session, payload: AppointmentCreate):
    import pdb; pdb.set_trace()  # ← Se pausa aquí
    # ...
```

Luego en terminal:
```
(Pdb) print(payload)
(Pdb) step
(Pdb) continue
(Pdb) exit
```

### Inspeccionar variables en contexto

```python
from pprint import pprint

def some_function():
    user = db.query(User).first()
    print(f"User: {user}")
    pprint(vars(user))  # Ver todos los atributos
```

---

## 🔍 Búsqueda y análisis de código

### Buscar en archivos

```powershell
# Buscar archivo
dir /s *.py | findstr "appointment"

# Buscar contenido (incluye subcarpetas)
findstr /s /i "def create_appointment" .

# Case-sensitive
findstr /s "def create_appointment" .
```

### Grep (Linux/Mac)

```bash
grep -r "def create_appointment" app/
grep -r "DATABASE_URL" .
```

---

## 📝 Seeding y datos de prueba

### Ejecutar seeds

```powershell
python -c "
from app.db.seed import seed_roles, seed_default_users
from app.db.session import SessionLocal

db = SessionLocal()
seed_roles(db)
seed_default_users(db)
db.close()
print('Seeds ejecutados')
"
```

### Usuarios de seedfá

| Email | Password | Rol |
|-------|----------|-----|
| `estudiante@example.com` | `12345678` | estudiante |
| `secretaria@example.com` | `12345678` | secretaria |

---

## 🔄 Git y control de versiones

### Ver estado

```powershell
git status
git diff           # Cambios unstaged
git diff --staged  # Cambios staged
```

### Hacer commit

```powershell
# Agregar específicos
git add app/services/appointment_service.py
git commit -m "fix: validar transición de estado"

# Agregar todo
git add .
git commit -m "feat: agregar nuevo endpoint"
```

### Ver logs

```powershell
git log --oneline -10        # Últimos 10 commits
git log --graph --oneline    # Gráfico de branches
git show <commit_hash>       # Ver cambios de un commit
```

### Ramas

```powershell
# Crear rama
git checkout -b feature/nueva-funcionalidad

# Cambiar rama
git checkout main

# Listar ramas
git branch -a

# Eliminar rama
git branch -D feature/vieja-funcionalidad
```

---

## 🐳 Docker (si se usa)

### Construir imagen

```powershell
docker build -t sigetu-backend:latest .
```

### Ejecutar contenedor

```powershell
docker run -p 8000:8000 --env-file .env.docker sigetu-backend:latest
```

### Ver logs

```powershell
docker logs <container_id>
docker logs -f <container_id>  # Seguir logs
```

---

## 🧹 Limpieza

### Limpiar caché Python

```powershell
# Eliminar todos los __pycache__
Get-ChildItem -Path . -Include __pycache__ -Recurse | Remove-Item -Recurse

# O directamente
rm -r -Force @(Get-ChildItem -Path . -Include __pycache__ -Recurse)
```

### Limpiar archivos temporales

```powershell
# Archivos .pyc
Remove-Item -Path . -Include *.pyc -Recurse

# Carpetas de venv residuales
Remove-Item -Path . -Include .pytest_cache -Recurse
Remove-Item -Path . -Include .mypy_cache -Recurse
```

---

## 📊 Análisis de código

### Formatear código (Black)

```powershell
pip install black

black app/
```

### Linter (Pylint)

```powershell
pip install pylint

pylint app/services/appointment_service.py
```

### Type checking (Mypy)

```powershell
pip install mypy

mypy app/services/
```

---

## 📖 Documentación

### Generar documentos interactivos

Con FastAPI automático en `/docs`:
```
http://localhost:8000/docs
```

### Ver docstrings

```python
python -c "from app.services.appointment_service import AppointmentService; help(AppointmentService.create_appointment)"
```

---

## 🔐 Variables de entorno

### Ver variables actuales

```powershell
# Archivo .env
Get-Content .env

# Variables del sistema
$env:DATABASE_URL
$env:SECRET_KEY
```

### Cargar desde archivo

```powershell
# PowerShell
Get-Content .env | ForEach-Object {
    if ($_ -match "^([^=]+)=(.*)$") {
        $name = $matches[1]
        $value = $matches[2]
        [Environment]::SetEnvironmentVariable($name, $value)
    }
}
```

---

## 🆘 Troubleshooting de comandos

| Problema | Solución |
|----------|----------|
| "command not found: python" | Instala Python, o usa python3 |
| "venv no activa" | Usa ruta completa: `.\venv\Scripts\python.exe` |
| "Database connection failed" | Verifica DATABASE_URL en .env |
| "Migration failed" | Revierte con `alembic downgrade -1` |
| "Port 8000 already in use" | Usa otro puerto: `--port 8001` |
| "Module not found" | Instala dependencias: `pip install -r requirements.txt` |

---

## 📚 Referencia rápida

```powershell
# Setup inicial
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m alembic upgrade head
uvicorn app.main:app --reload

# Operación diaria
.\venv\Scripts\Activate.ps1          # Activar venv
uvicorn app.main:app --reload        # Correr servidor
# ... desarrollo ...
python -m alembic upgrade head        # Si hay migraciones nuevas
git add . && git commit -m "..."      # Commit
```

---

## 🤔 Más información

- [QUICKSTART.md](QUICKSTART.md) - Instalación inicial
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guía de desarrollo
- [STRUCTURE.md](STRUCTURE.md) - Arquitectura del código

