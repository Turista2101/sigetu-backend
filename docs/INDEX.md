# 📑 INDEX - Índice completo de documentación

Índice de todos los archivos de documentación del proyecto SIGETU Backend.

## 📚 Documentación principal

### 🎯 Punto de inicio
- **[START_HERE.md](START_HERE.md)** - Comenzar aquí
  - Orientación rápida del proyecto
  - Descripción de roles (estudiante, secretaría)
  - Stack técnico
  - Preguntas frecuentes
  - Próximos pasos

### ⚡ Instalación y configuración
- **[QUICKSTART.md](QUICKSTART.md)** - Instalación en 5 minutos
  - Requisitos previos
  - Pasos de instalación
  - Configuración de base de datos
  - Usuarios de prueba
  - Troubleshooting
  - Verificar instalación

### 🏗️ Arquitectura y estructura
- **[STRUCTURE.md](STRUCTURE.md)** - Estructura detallada del proyecto
  - Distribución general de carpetas
  - Responsabilidades de cada capa
  - Modelos ORM (app/models/)
  - Schemas Pydantic (app/schemas/)
  - Servicios (app/services/)
  - Repositorios (app/repositories/)
  - Rutas HTTP/WS (app/api/routes/)
  - Configuración y core (app/core/)
  - Base de datos (app/db/)
  - Migraciones (alembic/)
  - Flujo de una petición típica
  - Diagrama de dependencias

### 📋 Descripción completa del proyecto
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Visión general completa
  - Propósito del proyecto
  - Arquitectura de capas
  - Modelo de datos (tablas)
  - Máquina de estados de citas
  - Sistema de autenticación y autorización
  - API REST endpoints
  - Stack técnico
  - Datos de prueba (seeds)
  - Ciclo de vida de una cita
  - Decisiones de diseño
  - Casos de uso principales
  - Validaciones de negocio
  - Características futuras

### 💻 Comandos y referencias
- **[COMMANDS.md](COMMANDS.md)** - Comandos útiles para desarrollo
  - Inicio rápido
  - Gestión de dependencias
  - Migraciones Alembic
  - Base de datos PostgreSQL
  - WebSockets
  - Testing
  - Debugging
  - Búsqueda de código
  - Seeding y datos de prueba
  - Git y control de versiones
  - Docker
  - Limpieza
  - Análisis de código
  - Documentación
  - Variables de entorno
  - Troubleshooting de comandos
  - Referencia rápida

### 🤝 Guía para contribuidores
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guía de desarrollo
  - Principios del proyecto
  - Workflow de desarrollo
  - Checklist antes de commit
  - Convenciones de código
  - Flujo de trabajo típico
  - Antipatrones a evitar
  - Validaciones obligatorias
  - Estándares de base de datos
  - Review checklist
  - Reportar bugs
  - Proponer features
  - Recursos útiles
  - Buen comportamiento del código
  - Arquitectura de capas
  - FAQs

### 📖 Información general
- **[README.md](README.md)** - Información general del repositorio
  - Descripción del proyecto
  - Quick start
  - Documentación disponible
  - Arquitectura
  - Roles y permisos
  - Endpoints principales
  - Tecnologías
  - Estructura del proyecto
  - Configuración
  - Desarrollo
  - Convenciones
  - Checklist
  - Problemas frecuentes
  - Estados de cita
  - Workflow de cambios

### 🔧 Configuración de ejemplo
- **[env.example](env.example)** - Archivo de variables de entorno
  - Variables requeridas
  - Explicación de cada variable
  - Valores por defecto
  - Cómo usar

## 🗺️ Mapa de navegación por rol

### 👨‍💻 Para desarrolladores nuevos
1. **Leer**: [START_HERE.md](START_HERE.md)
2. **Instalar**: [QUICKSTART.md](QUICKSTART.md)
3. **Entender**: [STRUCTURE.md](STRUCTURE.md)
4. **Aprender a contribuir**: [CONTRIBUTING.md](CONTRIBUTING.md)

### 🔧 Para desarrolladores experimentados
1. **Arquitectura**: [STRUCTURE.md](STRUCTURE.md)
2. **Reglas de negocio**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
3. **Comandos rápidos**: [COMMANDS.md](COMMANDS.md)
4. **Contribuir**: [CONTRIBUTING.md](CONTRIBUTING.md)

### 🚀 Para iniciar rápido
1. **Setup**: [QUICKSTART.md](QUICKSTART.md)
2. **Comandos**: [COMMANDS.md](COMMANDS.md)
3. **API Docs**: http://localhost:8000/docs

### 🐛 Para debugging/troubleshooting
1. **Problemas comunes**: [QUICKSTART.md#-troubleshooting](QUICKSTART.md#-troubleshooting)
2. **Comandos útiles**: [COMMANDS.md](COMMANDS.md)
3. **Logs y debugging**: [COMMANDS.md#-debugging](COMMANDS.md#-debugging)

## 📂 Estructura de carpetas del proyecto

```
sigetu-backend/
│
├── 📄 Documentación
│   ├── START_HERE.md           ← Comienza aquí
│   ├── QUICKSTART.md            ← Instalación
│   ├── STRUCTURE.md             ← Arquitectura
│   ├── PROJECT_SUMMARY.md       ← Visión completa
│   ├── COMMANDS.md              ← Comandos
│   ├── CONTRIBUTING.md          ← Desarrollo
│   ├── README.md                ← General
│   ├── INDEX.md                 ← Este archivo
│   └── env.example              ← Variables de env
│
├── 🔧 Configuración
│   ├── alembic.ini              ← Config Alembic
│   ├── requirements.txt         ← Dependencias
│   └── .env                     ← Variables (no commitear)
│
├── 📚 app/ (Código principal)
│   ├── main.py                  ← Punto de entrada FastAPI
│   ├── api/
│   │   └── routes/
│   │       ├── auth_routes.py
│   │       ├── appointments_ws_routes.py
│   │       ├── estudiante/
│   │       │   └── appointment_routes.py
│   │       └── secretaria/
│   │           └── appointment_routes.py
│   ├── services/
│   │   ├── appointment_service.py
│   │   └── auth_service.py
│   ├── repositories/
│   │   ├── appointment_repository.py
│   │   ├── user_repository.py
│   │   └── revoked_token_repository.py
│   ├── models/
│   │   ├── appointment_model.py
│   │   ├── appointment_history_model.py
│   │   ├── user_model.py
│   │   ├── role_model.py
│   │   └── revoked_token_model.py
│   ├── schemas/
│   │   ├── appointment_schema.py
│   │   └── user_schema.py
│   ├── core/
│   │   ├── config.py
│   │   ├── auth_dependencies.py
│   │   ├── security.py
│   │   └── realtime.py
│   └── db/
│       ├── session.py
│       ├── base.py
│       └── seed.py
│
├── 🗄️ alembic/ (Migraciones)
│   ├── env.py
│   │ versions/
│   │   ├── bd65e13f9cbb_initial_tables.py
│   │   ├── 9a4d2e7b1c30_add_programa_academico_to_users.py
│   │   ├── 1f2c3d4e5f6a_create_appointments_table.py
│   │   └── ... (más migraciones)
│   └── script.py.mako
│
└── 📋 docs/ (Documentación adicional)
    └── project-context.md
```

## 🔗 Enlaces rápidos por tema

### Instalación
- [QUICKSTART.md](QUICKSTART.md) - Guía completa
- [QUICKSTART.md#-requisitos-previos](QUICKSTART.md#-requisitos-previos)
- [QUICKSTART.md#-troubleshooting](QUICKSTART.md#-troubleshooting)
- [env.example](env.example) - Configuración

### Arquitectura
- [STRUCTURE.md](STRUCTURE.md) - Estructura de carpetas
- [STRUCTURE.md#-capa-de-presentación-httwebsocket](STRUCTURE.md#-capa-de-presentación-httwebsocket)
- [STRUCTURE.md#-servicios-lógica-de-negocio](STRUCTURE.md#-servicios-lógica-de-negocio)
- [STRUCTURE.md#-acceso-a-datos](STRUCTURE.md#-acceso-a-datos)
- [STRUCTURE.md#-modelos-orm-sqlalchemy](STRUCTURE.md#-modelos-orm-sqlalchemy)

### Desarrollo
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guía completa
- [CONTRIBUTING.md#-workflow-de-desarrollo](CONTRIBUTING.md#-workflow-de-desarrollo)
- [CONTRIBUTING.md#-checklist-antes-de-hacer-commit](CONTRIBUTING.md#-checklist-antes-de-hacer-commit)
- [CONTRIBUTING.md#-convenciones-de-código](CONTRIBUTING.md#-convenciones-de-código)
- [CONTRIBUTING.md#-flujo-de-trabajo-típico-agregar-nuevo-endpoint](CONTRIBUTING.md#-flujo-de-trabajo-típico-agregar-nuevo-endpoint)

### Autenticación
- [PROJECT_SUMMARY.md#-sistema-de-autenticación-y-autorización](PROJECT_SUMMARY.md#-sistema-de-autenticación-y-autorización)
- [STRUCTURE.md#-corauth_dependenciespy](STRUCTURE.md#-corauth_dependenciespy)

### Base de datos
- [PROJECT_SUMMARY.md#--modelo-de-datos](PROJECT_SUMMARY.md#--modelo-de-datos)
- [COMMANDS.md#--migraciones-de-base-de-datos-alembic](COMMANDS.md#--migraciones-de-base-de-datos-alembic)
- [COMMANDS.md#--base-de-datos-postgresql](COMMANDS.md#--base-de-datos-postgresql)

### API
- [PROJECT_SUMMARY.md#--api-rest](PROJECT_SUMMARY.md#--api-rest)
- [README.md#--api-endpoints-principales](README.md#--api-endpoints-principales)

### Comandos
- [COMMANDS.md](COMMANDS.md) - Todos los comandos
- [COMMANDS.md#-gestión-de-dependencias](COMMANDS.md#-gestión-de-dependencias)
- [COMMANDS.md#-migraciones-de-base-de-datos-alembic](COMMANDS.md#-migraciones-de-base-de-datos-alembic)

## 🎯 Búsqueda rápida

### ¿Cómo...?

#### ... instalar el proyecto?
→ [QUICKSTART.md](QUICKSTART.md)

#### ... agregar un nuevo endpoint?
→ [CONTRIBUTING.md#-flujo-de-trabajo-típico-agregar-nuevo-endpoint](CONTRIBUTING.md#-flujo-de-trabajo-típico-agregar-nuevo-endpoint)

#### ... entender la arquitectura?
→ [STRUCTURE.md](STRUCTURE.md)

#### ... hacer migraciones?
→ [COMMANDS.md#--migraciones-de-base-de-datos-alembic](COMMANDS.md#--migraciones-de-base-de-datos-alembic)

#### ... configurar la BD?
→ [QUICKSTART.md#-paso-4-crear-base-de-datos](QUICKSTART.md#-paso-4-crear-base-de-datos)

#### ... cambiar variables de entorno?
→ [env.example](env.example) y [QUICKSTART.md#-paso-5-configurar-variables-de-entorno](QUICKSTART.md#-paso-5-configurar-variables-de-entorno)

#### ... debuggear?
→ [COMMANDS.md#--debugging](COMMANDS.md#--debugging)

#### ... ver la documentación de API?
→ http://localhost:8000/docs (después de ejecutar servidor)

#### ... entender roles y permisos?
→ [PROJECT_SUMMARY.md#-roles-y-permisos](PROJECT_SUMMARY.md#-roles-y-permisos)

#### ... ver estados de cita?
→ [PROJECT_SUMMARY.md#--máquina-de-estados-de-citas](PROJECT_SUMMARY.md#--máquina-de-estados-de-citas)

#### ... reportar un bug?
→ [CONTRIBUTING.md#--reportar-bugs](CONTRIBUTING.md#--reportar-bugs)

#### ... proponer una feature?
→ [CONTRIBUTING.md#--proponer-features](CONTRIBUTING.md#--proponer-features)

## 📌 Archivos importantes

### Código
- [app/main.py](app/main.py) - Punto de entrada
- [app/services/appointment_service.py](app/services/appointment_service.py) - Lógica principal
- [app/models/appointment_model.py](app/models/appointment_model.py) - Modelo de citas
- [app/models/user_model.py](app/models/user_model.py) - Modelo de usuarios
- [app/core/auth_dependencies.py](app/core/auth_dependencies.py) - Validación de roles
- [app/core/config.py](app/core/config.py) - Configuración

### Migraciones
- [alembic.ini](alembic.ini) - Configuración de Alembic
- [alembic/env.py](alembic/env.py) - Entorno de migraciones

### Configuración
- [requirements.txt](requirements.txt) - Dependencias
- [.env](env.example) - Variables de entorno (ver env.example)

## 🎓 Rutas de aprendizaje

### Ruta 1: Principiante (0 experiencia con proyecto)
1. [START_HERE.md](START_HERE.md) (10 min)
2. [QUICKSTART.md](QUICKSTART.md) (15 min)
3. [STRUCTURE.md](STRUCTURE.md) (20 min)
4. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) (30 min)
5. Prueba los endpoints en http://localhost:8000/docs

### Ruta 2: Desarrollador (experiencia con FastAPI)
1. [STRUCTURE.md](STRUCTURE.md) (20 min)
2. [CONTRIBUTING.md](CONTRIBUTING.md) (20 min)
3. Comienza a desarrollar

### Ruta 3: DevOps/BD
1. [QUICKSTART.md](QUICKSTART.md#-paso-4-crear-base-de-datos)
2. [COMMANDS.md#--migraciones-de-base-de-datos-alembic](COMMANDS.md#--migraciones-de-base-de-datos-alembic)
3. [COMMANDS.md#--base-de-datos-postgresql](COMMANDS.md#--base-de-datos-postgresql)
4. [PROJECT_SUMMARY.md#--modelo-de-datos](PROJECT_SUMMARY.md#--modelo-de-datos)

### Ruta 4: Revisor de PRs
1. [CONTRIBUTING.md#--review-checklist-para-revisor](CONTRIBUTING.md#--review-checklist-para-revisor)
2. [CONTRIBUTING.md#-checklist-antes-de-hacer-commit](CONTRIBUTING.md#-checklist-antes-de-hacer-commit)
3. [STRUCTURE.md](STRUCTURE.md)

## 📞 Contacto rápido

### Problema con instalación?
→ [QUICKSTART.md#-troubleshooting](QUICKSTART.md#-troubleshooting)

### No sé por dónde empezar?
→ [START_HERE.md](START_HERE.md)

### Necesito referenciar arquitectura?
→ [STRUCTURE.md](STRUCTURE.md)

### Voy a hacer cambios al código?
→ [CONTRIBUTING.md](CONTRIBUTING.md)

### Necesito un comando específico?
→ [COMMANDS.md](COMMANDS.md)

### Quiero entender todo en detalle?
→ [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

**Última actualización**: 3 de marzo de 2026

Para ver toda la estructura del proyecto, visita la carpeta raíz del repositorio.
