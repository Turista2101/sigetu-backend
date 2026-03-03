# 🚀 SIGETU Backend - START HERE

Bienvenido al backend de gestión de citas académicas de SIGETU. Lee este archivo primero para orientarte rápidamente.

## ¿Qué es SIGETU Backend?

Sistema de gestión de citas académicas construido con **FastAPI**, **SQLAlchemy** y **PostgreSQL**. 

Permite a:
- **Estudiantes**: Crear, consultar, editar y cancelar sus citas académicas
- **Secretaría**: Gestionar la cola de atención y actualizar estados de citas

## 📋 Lo primero que debes hacer

### 1. Leer la documentación clave (en orden):
1. **Este archivo** (contexto rápido)
2. [QUICKSTART.md](QUICKSTART.md) (instalación en 5 minutos)
3. [STRUCTURE.md](STRUCTURE.md) (cómo está organizado el código)
4. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) (detalles del proyecto)

### 2. Luego, según tu rol:
- **Desarrollador backend**: Lee [CONTRIBUTING.md](CONTRIBUTING.md)
- **Necesitas ejecutar comandos**: Ve a [COMMANDS.md](COMMANDS.md)
- **Quieres consultar todo**: Usa [INDEX.md](INDEX.md)

## 🏃 Quick Setup (2 minutos)

Si querés correr el proyecto ahora:

```powershell
# 1. Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# 2. Configurar base de datos (en .env)
# - DATABASE_URL=postgresql://user:pass@localhost:5432/sigetu
# - SECRET_KEY=tu_clave_secreta

# 3. Ejecutar migraciones
python -m alembic upgrade head

# 4. Iniciar servidor
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

## 📁 Estructura de carpetas (resumen)

```
sigetu-backend/
├── app/
│   ├── api/routes/          # Endpoints HTTP y WebSocket
│   ├── services/            # Lógica de negocio
│   ├── repositories/        # Acceso a datos
│   ├── models/              # Entidades ORM (SQLAlchemy)
│   ├── schemas/             # Contratos Pydantic
│   ├── core/                # Configuración, auth, seguridad
│   └── db/                  # Sesiones, seeds
├── alembic/                 # Migraciones de BD
└── requirements.txt         # Dependencias Python
```

Ver más detalles en [STRUCTURE.md](STRUCTURE.md).

## 👥 Roles del sistema

| Rol | Capacidades |
|-----|------------|
| **Estudiante** | Crear citas, ver sus citas actuales e historial, editar/cancelar propias citas |
| **Secretaría** | Ver cola de citas, cambiar estado, ver historial de atendidas |
| **Admin** | Acceso total (no implementado aún) |

## 🔐 Autenticación

La API usa **tokens JWT** con dos tipos:
- **Access token**: Válido 7 días (por defecto)
- **Refresh token**: Válido 7 días para renovar access token

```bash
# Login
POST /auth/login
{
  "email": "estudiante@example.com",
  "password": "12345678"
}

# Response
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {...}
}
```

## 🗄️ Estados de cita

```
pendiente → llamando → en_atencion → atendido
         ↓
       cancelada (en cualquier momento)
       
       no_asistio (si no llegó)
```

## 🛠️ Stack Técnico

| Componente | Versión/Herramienta |
|-----------|-------------------|
| **Framework** | FastAPI 0.131.0 |
| **ORM** | SQLAlchemy 2.0.46 |
| **BD** | PostgreSQL |
| **Migraciones** | Alembic 1.18.4 |
| **Validación** | Pydantic 2.12.5 |
| **Auth** | JWT (python-jose) |
| **Async** | AsyncIO + WebSockets |

## 📚 Documentación disponible

- 📖 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Visión general del proyecto
- 🏗️ [STRUCTURE.md](STRUCTURE.md) - Estructura detallada de carpetas y módulos
- ⚡ [QUICKSTART.md](QUICKSTART.md) - Guía de instalación y primeros pasos
- 💻 [COMMANDS.md](COMMANDS.md) - Comandos útiles para desarrollo
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) - Guía para contribuidores
- 🎯 [INDEX.md](INDEX.md) - Índice con todos los enlaces
- 📋 [README.md](README.md) - Información general del repositorio

## ❓ Preguntas frecuentes

**¿Cómo creo una cita?**  
Los estudiantes usan `POST /appointments` con su token JWT.

**¿Cómo veo la cola?**  
La secretaría usa `GET /appointments/queue` de su rol específico.

**¿Dónde está la lógica de negocio?**  
En `app/services/` - especialmente en `AppointmentService`.

**¿Cómo agrego un nuevo endpoint?**  
1. Crea el método en el servicio (`app/services/`)
2. Expónlo en las rutas (`app/api/routes/`)
3. Crea una migración si cambias el modelo

**¿Cómo ejecuto migraciones?**  
```powershell
python -m alembic upgrade head      # Aplicar todas
python -m alembic downgrade -1      # Revertir última
python -m alembic current           # Ver versión actual
```

## 🚀 Próximos pasos

1. ✅ Lee [QUICKSTART.md](QUICKSTART.md)
2. ✅ Instala las dependencias
3. ✅ Configura la base de datos
4. ✅ Ejecuta `python -m alembic upgrade head`
5. ✅ Inicia el servidor con `uvicorn app.main:app --reload`
6. ✅ Prueba los endpoints en `http://localhost:8000/docs`

## 📞 Soporte

- Revisa [CONTRIBUTING.md](CONTRIBUTING.md) para problemas comunes
- Consulta [COMMANDS.md](COMMANDS.md) para comandos útiles
- Usa `http://localhost:8000/docs` para explorar la API

---

**¿Listo para comenzar?** → [QUICKSTART.md](QUICKSTART.md)
