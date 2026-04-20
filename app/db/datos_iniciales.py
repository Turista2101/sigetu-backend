"""Semillas de roles y usuarios base para entornos de desarrollo."""

from sqlalchemy.orm import Session
from app.models.modelo_categoria import Categoria
from app.models.modelo_contexto import Contexto
from app.models.modelo_rol import Role
from app.models.modelo_programa_academico import ProgramaAcademico
from app.models.modelo_sede import Sede
from app.models.modelo_staff import Staff
from app.models.modelo_usuario import User
from app.core.seguridad import hashear_contrasena


SEED_PASSWORD = "12345678"
PROGRAMAS_ACADEMICOS = ["ingenierias", "derecho", "finanzas"]


def _upsert_by_codigo(db: Session, model, codigo: str, defaults: dict):
    existente = db.query(model).filter(model.codigo == codigo).first()
    if existente:
        for campo, valor in defaults.items():
            setattr(existente, campo, valor)
        return existente

    entidad = model(codigo=codigo, **defaults)
    db.add(entidad)
    return entidad


def seed_programas_academicos(db: Session):
    """Crea/actualiza el catalogo base de programas academicos para entornos locales."""
    catalogo = [
        {"codigo": "ingenierias", "nombre": "Ingenierias", "descripcion": "Facultad de Ingenierias"},
        {"codigo": "derecho", "nombre": "Derecho", "descripcion": "Facultad de Derecho"},
        {"codigo": "finanzas", "nombre": "Finanzas", "descripcion": "Facultad de Finanzas"},
    ]

    for item in catalogo:
        existente = db.query(ProgramaAcademico).filter(ProgramaAcademico.codigo == item["codigo"]).first()
        if existente:
            existente.nombre = item["nombre"]
            existente.descripcion = item["descripcion"]
            existente.activo = True
            continue

        db.add(
            ProgramaAcademico(
                codigo=item["codigo"],
                nombre=item["nombre"],
                descripcion=item["descripcion"],
                activo=True,
            )
        )

    db.commit()


def seed_contextos(db: Session):
    """Crea/actualiza contextos base agrupados por categoria."""
    categorias = {(categoria.sede_id, categoria.codigo): categoria for categoria in db.query(Categoria).all()}
    catalogo = [
        {
            "sede": "asistencia_estudiantil",
            "categoria": "general",
            "codigo": "atencion_estudiantil",
            "nombre": "Atencion Estudiantil",
            "descripcion": "Contexto para asistencia al estudiante",
        },
        {
            "sede": "sede_administrativa",
            "categoria": "pagos_facturacion",
            "codigo": "atencion_administrativa",
            "nombre": "Atencion Administrativa",
            "descripcion": "Contexto para tramites administrativos",
        },
        {
            "sede": "sede_admisiones_mercadeo",
            "categoria": "informacion_academica",
            "codigo": "admisiones_mercadeo",
            "nombre": "Admisiones y Mercadeo",
            "descripcion": "Contexto para admisiones y mercadeo",
        },
    ]

    for item in catalogo:
        sede = db.query(Sede).filter(Sede.codigo == item["sede"]).first()
        if not sede:
            continue
        categoria = categorias.get((sede.id, item["categoria"]))
        if not categoria:
            continue

        existente = (
            db.query(Contexto)
            .filter(Contexto.categoria_id == categoria.id, Contexto.codigo == item["codigo"])
            .first()
        )
        if existente:
            existente.nombre = item["nombre"]
            existente.descripcion = item["descripcion"]
            existente.activo = True
            continue

        db.add(
            Contexto(
                categoria_id=categoria.id,
                codigo=item["codigo"],
                nombre=item["nombre"],
                descripcion=item["descripcion"],
                activo=True,
            )
        )

    db.commit()


def seed_categorias(db: Session):
    """Crea/actualiza categorias base agrupadas por sede."""
    sedes = {sede.codigo: sede for sede in db.query(Sede).all()}
    catalogo = [
        {"sede": "asistencia_estudiantil", "codigo": "general", "nombre": "General", "descripcion": "Atencion general a estudiantes"},
        {"sede": "sede_administrativa", "codigo": "pagos_facturacion", "nombre": "Pagos y Facturacion", "descripcion": "Pagos, facturacion y recaudos"},
        {"sede": "sede_administrativa", "codigo": "recibos_certificados", "nombre": "Recibos y Certificados", "descripcion": "Recibos, constancias y certificados"},
        {"sede": "sede_administrativa", "codigo": "creditos_financiacion", "nombre": "Creditos y Financiacion", "descripcion": "Creditos, financiacion e ICETEX"},
        {"sede": "sede_administrativa", "codigo": "problemas_soporte_financiero", "nombre": "Soporte Financiero", "descripcion": "Soporte sobre problemas financieros"},
        {"sede": "sede_administrativa", "codigo": "plataformas_servicios", "nombre": "Plataformas y Servicios", "descripcion": "Habilitacion de plataformas"},
        {"sede": "sede_admisiones_mercadeo", "codigo": "informacion_academica", "nombre": "Informacion Academica", "descripcion": "Informacion de programas y oferta academica"},
        {"sede": "sede_admisiones_mercadeo", "codigo": "inscripcion_matricula", "nombre": "Inscripcion y Matricula", "descripcion": "Procesos de inscripcion y matricula"},
    ]

    for item in catalogo:
        sede = sedes.get(item["sede"])
        if not sede:
            continue

        existente = (
            db.query(Categoria)
            .filter(Categoria.sede_id == sede.id, Categoria.codigo == item["codigo"])
            .first()
        )
        if existente:
            existente.nombre = item["nombre"]
            existente.descripcion = item["descripcion"]
            existente.activo = True
            continue

        db.add(
            Categoria(
                sede_id=sede.id,
                codigo=item["codigo"],
                nombre=item["nombre"],
                descripcion=item["descripcion"],
                activo=True,
            )
        )

    db.commit()


def seed_sedes(db: Session):
    """Crea/actualiza sedes base."""
    catalogo = [
        {
            "codigo": "asistencia_estudiantil",
            "nombre": "Asistencia Estudiantil",
            "ubicacion": "Bloque principal",
            "descripcion": "Sede de asistencia estudiantil",
        },
        {
            "codigo": "sede_administrativa",
            "nombre": "Sede Administrativa",
            "ubicacion": "Bloque administrativo",
            "descripcion": "Sede administrativa para tramites financieros",
        },
        {
            "codigo": "sede_admisiones_mercadeo",
            "nombre": "Sede Admisiones y Mercadeo",
            "ubicacion": "Bloque de admisiones",
            "descripcion": "Sede para admisiones y mercadeo",
        },
    ]

    for item in catalogo:
        existente = db.query(Sede).filter(Sede.codigo == item["codigo"]).first()
        if existente:
            existente.nombre = item["nombre"]
            existente.ubicacion = item["ubicacion"]
            existente.descripcion = item["descripcion"]
            existente.activo = True
            continue

        db.add(
            Sede(
                codigo=item["codigo"],
                nombre=item["nombre"],
                ubicacion=item["ubicacion"],
                descripcion=item["descripcion"],
                activo=True,
            )
        )

    db.commit()

def seed_roles(db: Session):
    """Crea los roles mínimos requeridos por el flujo de autenticación y sedes."""
    roles = [
        "admin",
        "estudiante",
        "staff",
    ]

    for role_name in roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            new_role = Role(name=role_name)
            db.add(new_role)

    db.commit()


def seed_default_users(db: Session):
    """Crea/actualiza usuarios de prueba para cada rol y programa académico."""
    role_admin = db.query(Role).filter(Role.name == "admin").first()
    role_estudiante = db.query(Role).filter(Role.name == "estudiante").first()
    role_staff = db.query(Role).filter(Role.name == "staff").first()

    if not role_admin or not role_estudiante or not role_staff:
        return

    programas_por_codigo = {
        programa.codigo: programa
        for programa in db.query(ProgramaAcademico).all()
    }

    programa_default = programas_por_codigo.get("ingenierias")
    if not programa_default:
        return

    sedes_por_codigo = {
        sede.codigo: sede
        for sede in db.query(Sede).all()
    }

    sede_asistencia = sedes_por_codigo.get("asistencia_estudiantil")
    sede_administrativa = sedes_por_codigo.get("sede_administrativa")
    sede_admisiones = sedes_por_codigo.get("sede_admisiones_mercadeo")

    def upsert_user(email: str, full_name: str, role_id: int, programa_academico_id: int):
        """Inserta o sincroniza un usuario semilla conservando credenciales de desarrollo."""
        existing_user = db.query(User).filter(User.email == email).first()
        hashed = hashear_contrasena(SEED_PASSWORD)

        if existing_user:
            existing_user.full_name = full_name
            existing_user.role_id = role_id
            existing_user.programa_academico_id = programa_academico_id
            existing_user.is_active = True
            existing_user.hashed_password = hashed
            db.commit()
            return

        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed,
            programa_academico_id=programa_academico_id,
            is_active=True,
            role_id=role_id,
        )
        db.add(user)
        db.commit()

    upsert_user(
        email="admin@uniautonoma.edu.co",
        full_name="Administrador SIGETU",
        role_id=role_admin.id,
        programa_academico_id=programa_default.id,
    )

    # Staff principal
    staff_users = [
        {
            "email": "staff@uniautonoma.edu.co",
            "full_name": "Staff Ingenierias",
            "programa": programa_default,
            "sede": sede_asistencia
        },
    ]

    # Staff por programa
    for programa in PROGRAMAS_ACADEMICOS:
        programa_obj = programas_por_codigo.get(programa)
        if not programa_obj:
            continue
        upsert_user(
            email=f"estudiante.{programa}@uniautonoma.edu.co",
            full_name=f"Estudiante {programa.capitalize()}",
            role_id=role_estudiante.id,
            programa_academico_id=programa_obj.id,
        )
        staff_users.append({
            "email": f"staff.{programa}@uniautonoma.edu.co",
            "full_name": f"Staff {programa.capitalize()}",
            "programa": programa_obj,
            "sede": sede_asistencia
        })

    # Crear usuarios staff y asignar a sede
    for staff_data in staff_users:
        upsert_user(
            email=staff_data["email"],
            full_name=staff_data["full_name"],
            role_id=role_staff.id,
            programa_academico_id=staff_data["programa"].id,
        )
        user = db.query(User).filter(User.email == staff_data["email"]).first()
        if user and staff_data["sede"]:
            asignacion = db.query(Staff).filter(Staff.user_id == user.id).first()
            if not asignacion:
                db.add(Staff(user_id=user.id, sede_id=staff_data["sede"].id, activo=True))
            else:
                asignacion.sede_id = staff_data["sede"].id
                asignacion.activo = True
        db.commit()


