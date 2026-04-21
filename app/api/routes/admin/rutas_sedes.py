"""Endpoints CRUD para catalogos de contextos, categorias y sedes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencias_autenticacion import requerir_rol_admin
from app.db.sesion import obtener_db
from app.schemas.esquema_sedes import (
    ActualizarCategoria,
    ActualizarContexto,
    ActualizarHorarioSede,
    ActualizarSede,
    CrearCategoria,
    CrearContexto,
    CrearHorarioSede,
    CrearHorarioSedeLote,
    CrearSede,
    RespuestaCategoria,
    RespuestaContexto,
    RespuestaHorarioSede,
    RespuestaSede,
)
from app.services.servicio_sedes import ServicioCategorias, ServicioContextos, ServicioHorariosSede, ServicioSedes


router = APIRouter(tags=["Catalogos Sedes"])
servicio_contextos = ServicioContextos()
servicio_categorias = ServicioCategorias()
servicio_sedes = ServicioSedes()
servicio_horarios = ServicioHorariosSede()


@router.get("/contextos", response_model=list[RespuestaContexto])
def listar_contextos(
    activos: bool | None = Query(None, description="Filtra por estado activo/inactivo"),
    categoria_id: int | None = Query(None, description="Filtra contextos por categoria"),
    db: Session = Depends(obtener_db),
):
    """Lista contextos, opcionalmente filtrados por estado activo."""
    return servicio_contextos.listar(db=db, solo_activos=activos, categoria_id=categoria_id)


@router.get("/contextos/{contexto_id}", response_model=RespuestaContexto)
def obtener_contexto(
    contexto_id: int,
    db: Session = Depends(obtener_db),
):
    """Obtiene un contexto por su identificador."""
    return servicio_contextos.obtener(db=db, contexto_id=contexto_id)


@router.post("/contextos", response_model=RespuestaContexto, status_code=201)
def crear_contexto(
    payload: CrearContexto,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Crea un contexto nuevo en el catalogo."""
    return servicio_contextos.crear(db=db, payload=payload)


@router.patch("/contextos/{contexto_id}", response_model=RespuestaContexto)
def actualizar_contexto(
    contexto_id: int,
    payload: ActualizarContexto,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Actualiza campos de un contexto existente."""
    return servicio_contextos.actualizar(db=db, contexto_id=contexto_id, payload=payload)


@router.delete("/contextos/{contexto_id}", status_code=204)
def eliminar_contexto(
    contexto_id: int,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Elimina un contexto del catalogo."""
    servicio_contextos.eliminar(db=db, contexto_id=contexto_id)
    return None


@router.get("/categorias", response_model=list[RespuestaCategoria])
def listar_categorias(
    activos: bool | None = Query(None, description="Filtra por estado activo/inactivo"),
    sede_id: int | None = Query(None, description="Filtra categorias por sede"),
    db: Session = Depends(obtener_db),
):
    """Lista categorias, opcionalmente filtradas por estado y contexto."""
    return servicio_categorias.listar(
        db=db,
        solo_activos=activos,
        sede_id=sede_id,
    )


@router.get("/categorias/{categoria_id}", response_model=RespuestaCategoria)
def obtener_categoria(
    categoria_id: int,
    db: Session = Depends(obtener_db),
):
    """Obtiene una categoria por su identificador."""
    return servicio_categorias.obtener(db=db, categoria_id=categoria_id)


@router.post("/categorias", response_model=RespuestaCategoria, status_code=201)
def crear_categoria(
    payload: CrearCategoria,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Crea una categoria nueva en el catalogo."""
    return servicio_categorias.crear(db=db, payload=payload)


@router.patch("/categorias/{categoria_id}", response_model=RespuestaCategoria)
def actualizar_categoria(
    categoria_id: int,
    payload: ActualizarCategoria,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Actualiza campos de una categoria existente."""
    return servicio_categorias.actualizar(db=db, categoria_id=categoria_id, payload=payload)


@router.delete("/categorias/{categoria_id}", status_code=204)
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Elimina una categoria del catalogo."""
    servicio_categorias.eliminar(db=db, categoria_id=categoria_id)
    return None


@router.get("/sedes", response_model=list[RespuestaSede])
def listar_sedes(
    activos: bool | None = Query(None, description="Filtra por estado activo/inactivo"),
    db: Session = Depends(obtener_db),
):
    """Lista sedes, opcionalmente filtradas por estado."""
    return servicio_sedes.listar(
        db=db,
        solo_activos=activos,
    )


@router.get("/sedes/{sede_id}", response_model=RespuestaSede)
def obtener_sede(
    sede_id: int,
    db: Session = Depends(obtener_db),
):
    """Obtiene una sede por su identificador."""
    return servicio_sedes.obtener(db=db, sede_id=sede_id)


@router.post("/sedes", response_model=RespuestaSede, status_code=201)
def crear_sede(
    payload: CrearSede,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Crea una sede nueva en el catalogo."""
    return servicio_sedes.crear(db=db, payload=payload)


@router.patch("/sedes/{sede_id}", response_model=RespuestaSede)
def actualizar_sede(
    sede_id: int,
    payload: ActualizarSede,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Actualiza campos de una sede existente."""
    return servicio_sedes.actualizar(db=db, sede_id=sede_id, payload=payload)


@router.delete("/sedes/{sede_id}", status_code=204)
def eliminar_sede(
    sede_id: int,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Elimina una sede del catalogo."""
    servicio_sedes.eliminar(db=db, sede_id=sede_id)
    return None


@router.get("/sedes/{sede_id}/horarios", response_model=list[RespuestaHorarioSede])
def listar_horarios_sede(
    sede_id: int,
    activos: bool | None = Query(None, description="Filtra por estado activo/inactivo"),
    db: Session = Depends(obtener_db),
):
    """Lista bloques horarios configurados para una sede."""
    return servicio_horarios.listar(db=db, sede_id=sede_id, solo_activos=activos)


@router.post("/sedes/{sede_id}/horarios", response_model=RespuestaHorarioSede, status_code=201)
def crear_horario_sede(
    sede_id: int,
    payload: CrearHorarioSede,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Crea un bloque horario para una sede."""
    return servicio_horarios.crear(db=db, sede_id=sede_id, payload=payload)


@router.post("/sedes/{sede_id}/horarios/lote", response_model=list[RespuestaHorarioSede], status_code=201)
def crear_horarios_sede_lote(
    sede_id: int,
    payload: CrearHorarioSedeLote,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Crea varios bloques horarios para una sede en una sola operación."""
    return servicio_horarios.crear_lote(db=db, sede_id=sede_id, payload=payload)


@router.patch("/sedes/{sede_id}/horarios/{horario_id}", response_model=RespuestaHorarioSede)
def actualizar_horario_sede(
    sede_id: int,
    horario_id: int,
    payload: ActualizarHorarioSede,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Actualiza un bloque horario de una sede."""
    return servicio_horarios.actualizar(db=db, sede_id=sede_id, horario_id=horario_id, payload=payload)


@router.delete("/sedes/{sede_id}/horarios/{horario_id}", status_code=204)
def eliminar_horario_sede(
    sede_id: int,
    horario_id: int,
    db: Session = Depends(obtener_db),
    _: dict = Depends(requerir_rol_admin),
):
    """Elimina un bloque horario de una sede."""
    servicio_horarios.eliminar(db=db, sede_id=sede_id, horario_id=horario_id)
    return None
