# 🚀 SIGETU Backend - START HERE

Bienvenido al backend de gestión de citas académicas de SIGETU. Lee este archivo primero para orientarte rápidamente.

## ¿Qué es SIGETU Backend?

Sistema de gestión de citas académicas construido con **FastAPI**, **SQLAlchemy** y **PostgreSQL**.

Permite a:
- **Estudiantes**: Crear, consultar, editar y cancelar sus citas académicas/administrativas
- **Secretaría**: Gestionar la cola de atención de Asistencia Estudiantil
- **Administrativos**: Gestionar la cola de atención de sede Administrativa (financiera)

## 📋 Lo primero que debes hacer

### 1. Leer la documentación clave (en orden):
1. **Este archivo** (contexto rápido)
2. [QUICKSTART.md](QUICKSTART.md) (instalación en 5 minutos con Docker o manual)
3. [STRUCTURE.md](STRUCTURE.md) (cómo está organizado el código)
4. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) (detalles completos del proyecto)

### 2. Luego, según tu rol:
- **Desarrollador backend**: Lee [CONTRIBUTING.md](CONTRIBUTING.md)
- **Necesitas ejecutar comandos**: Ve a [COMMANDS.md](COMMANDS.md)
- **Quieres consultar todo**: Usa [INDEX.md](INDEX.md)

## 🏃 Quick Setup (2 minutos con Docker)

Si quieres correr el proyecto ahora mismo:

\\\powershell
# 1. Clonar
git clone <repo_url>
cd sigetu-backend

# 2. Configurar .env (editar con tus valores)
DATABASE_URL=postgresql://postgres:2101@db:5432/sigetu
SECRET_KEY=tu_clave_secreta

# 3. Ejecutar con Docker
docker-compose up -d

# 4. Ver logs
docker-compose logs -f api
\\\

El servidor estará disponible en \http://localhost:8000\

**Sin Docker:**
\\\powershell
# Activar entorno virtual
.\\venv\\Scripts\\Activate.ps1

# Crear BD PostgreSQL
psql -U postgres -c \"CREATE DATABASE sigetu;\"

# Configurar .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/sigetu

# Ejecutar migraciones
python -m alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
\\\

## 📁 Estructura de carpetas (resumen)

\\\
sigetu-backend/
├── app/
│   ├── api/routes/              # Endpoints HTTP y WebSocket
│   │   ├── estudiante/          # Rutas de estudiantes
│   │   ├── secretaria/          # Rutas de secretaría/admin
│   │   ├── rutas_autenticacion.py
│   │   ├── rutas_notificaciones.py
│   │   └── rutas_ws_citas.py
│   ├── services/                # Lógica de negocio
│   ├── repositories/            # Acceso a datos
│   ├── models/                  # Entidades ORM (SQLAlchemy)
│   │   ├── modelo_usuario.py
│   │   ├── modelo_cita.py
│   │   ├── modelo_historial_cita.py
│   │   ├── modelo_token_dispositivo_fcm.py
│   │   └── ...
│   ├── schemas/                 # Contratos Pydantic
│   ├── core/                    # Configuración, auth, seguridad
│   └── db/                      # Sesiones, seeds
├── alembic/                     # Migraciones de BD
├── docker-compose.yml           # Docker Compose (API + PostgreSQL)
├── Dockerfile                   # Imagen Docker
├── start.sh                     # Script de inicio
└── requirements.txt             # Dependencias Python
\\\

Ver más detalles en [STRUCTURE.md](STRUCTURE.md).

## 👥 Roles del sistema

| Rol | Capacidades |
|-----|------------|
| **Estudiante** | Crear citas, ver sus citas actuales e historial, editar/cancelar propias citas |
| **Secretaría** | Ver cola de citas, cambiar estado, ver historial de atendidas |
| **Administrativo** | Ver cola de citas, cambiar estado, ver historial de atendidas |

## 🔐 Autenticación

La API usa **tokens JWT** con dos tipos:
- **Access token**: Válido 7 días (por defecto)
- **Refresh token**: Válido 7 días para renovar access token

\\\ash
# Login
POST /auth/login
{
  \"email\": \"estudiante@example.com\",
  \"password\": \"12345678\"
}

# Response
{
  \"access_token\": \"...\",
  \"refresh_token\": \"...\",
  \"token_type\": \"bearer\",
  \"user\": {...}
}
\\\

## 🗄️ Estados de cita

\\\
pendiente → llamando → en_atencion → atendido
         ↓
       cancelada (en cualquier momento)
       
       no_asistio (si no llegó)
\\\

## 🏢 Sedes y categorías

### Asistencia Estudiantil
- Categorías: \cademico\, \dministrativo\, \inanciero\, \otro\

### Administrativa (Financiera)
- \pagos_facturacion\: Pagos con tarjeta, validación pagos, facturación electrónica
- \
ecibos_certificados\: Generación recibos, certificado valores pagados
- \creditos_financiacion\: Trámites crédito, ICETEX
- \problemas_soporte_financiero\: Problemas matrículas financieras
- \plataformas_servicios\: Habilitación plataformas

## 🛠️ Stack Técnico

| Componente | Versión/Herramienta |
|-----------|-------------------|
| **Framework** | FastAPI 0.131.0 |
| **ORM** | SQLAlchemy 2.0.46 |
| **BD** | PostgreSQL 16 |
| **Migraciones** | Alembic 1.18.4 |
| **Validación** | Pydantic 2.12.5 |
| **Auth** | JWT (python-jose) |
| **Notificaciones** | Firebase Admin SDK |
| **Async** | AsyncIO + WebSockets |
| **Contenedores** | Docker + Docker Compose |

## 📚 Documentación disponible

- 📖 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Visión general del proyecto
- 🏗️ [STRUCTURE.md](STRUCTURE.md) - Estructura detallada de carpetas y módulos
- ⚡ [QUICKSTART.md](QUICKSTART.md) - Guía de instalación y primeros pasos
- 💻 [COMMANDS.md](COMMANDS.md) - Comandos útiles para desarrollo
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) - Guía para contribuidores
- 🎯 [INDEX.md](INDEX.md) - Índice con todos los enlaces
- 📋 [README.md](../README.md) - Información general del repositorio

## ❓ Preguntas frecuentes

**¿Cómo creo una cita?**  
Los estudiantes usan \POST /appointments\ con su token JWT.

**¿Cómo veo la cola?**  
La secretaría/administrativo usa \GET /appointments/queue\ de su rol específico.

**¿Dónde está la lógica de negocio?**  
En \pp/services/\ - especialmente en \servicio_cita.py\.

**¿Cómo agrego un nuevo endpoint?**  
1. Crea el método en el servicio (\pp/services/\)
2. Expónlo en las rutas (\pp/api/routes/\)
3. Crea una migración si cambias el modelo

**¿Cómo ejecuto migraciones?**  
\\\powershell
# Con Docker
docker-compose exec api python -m alembic upgrade head

# Sin Docker
python -m alembic upgrade head
\\\

**¿Cómo veo los logs?**  
\\\powershell
# Con Docker
docker-compose logs -f api

# Sin Docker
# Los logs aparecen en la consola donde ejecutaste uvicorn
\\\

## 🚀 Próximos pasos

1. ✅ Lee [QUICKSTART.md](QUICKSTART.md)
2. ✅ Elige instalación (Docker o manual)
3. ✅ Ejecuta el servidor
4. ✅ Prueba los endpoints en \http://localhost:8000/docs\
5. ✅ Explora el código en \pp/\
6. ✅ Lee [STRUCTURE.md](STRUCTURE.md) para entender la arquitectura

## 📞 Soporte

- Revisa [CONTRIBUTING.md](CONTRIBUTING.md) para problemas comunes
- Consulta [COMMANDS.md](COMMANDS.md) para comandos útiles
- Usa \http://localhost:8000/docs\ para explorar la API
- Verifica [QUICKSTART.md#troubleshooting](QUICKSTART.md#-troubleshooting) para errores comunes

---

**¿Listo para comenzar?** → [QUICKSTART.md](QUICKSTART.md)
