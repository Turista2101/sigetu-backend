"""Servicios de negocio para catalogos de contextos, categorias y sedes."""

from datetime import time

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.repositorio_sedes import (
    RepositorioCategorias,
    RepositorioContextos,
    RepositorioHorariosSede,
    RepositorioSedes,
)
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
)


class ServicioContextos:
    """Reglas de negocio para CRUD de contextos."""

    def __init__(self) -> None:
        self.repositorio = RepositorioContextos()
        self.repo_categorias = RepositorioCategorias()

    @staticmethod
    def _normalizar_codigo(codigo: str) -> str:
        return codigo.strip().lower()

    @staticmethod
    def _normalizar_nombre(nombre: str) -> str:
        return nombre.strip()

    def listar(
        self,
        db: Session,
        solo_activos: bool | None = None,
        categoria_id: int | None = None,
    ):
        return self.repositorio.listar(
            db=db,
            solo_activos=solo_activos,
            categoria_id=categoria_id,
        )

    def obtener(self, db: Session, contexto_id: int):
        contexto = self.repositorio.obtener_por_id(db=db, contexto_id=contexto_id)
        if not contexto:
            raise HTTPException(status_code=404, detail="Contexto no encontrado")
        return contexto

    def crear(self, db: Session, payload: CrearContexto):
        if not self.repo_categorias.obtener_por_id(db=db, categoria_id=payload.categoria_id):
            raise HTTPException(status_code=404, detail="Categoria no encontrada")

        codigo = self._normalizar_codigo(payload.codigo)
        nombre = self._normalizar_nombre(payload.nombre)

        if self.repositorio.obtener_por_codigo_en_categoria(db=db, categoria_id=payload.categoria_id, codigo=codigo):
            raise HTTPException(status_code=400, detail="Ya existe un contexto con ese codigo en la categoria")

        if self.repositorio.obtener_por_nombre_en_categoria(db=db, categoria_id=payload.categoria_id, nombre=nombre):
            raise HTTPException(status_code=400, detail="Ya existe un contexto con ese nombre en la categoria")

        return self.repositorio.crear(
            db=db,
            categoria_id=payload.categoria_id,
            codigo=codigo,
            nombre=nombre,
            descripcion=payload.descripcion,
            activo=payload.activo,
        )

    def actualizar(self, db: Session, contexto_id: int, payload: ActualizarContexto):
        contexto = self.repositorio.obtener_por_id(db=db, contexto_id=contexto_id)
        if not contexto:
            raise HTTPException(status_code=404, detail="Contexto no encontrado")

        categoria_id_objetivo = payload.categoria_id if payload.categoria_id is not None else contexto.categoria_id
        if not self.repo_categorias.obtener_por_id(db=db, categoria_id=categoria_id_objetivo):
            raise HTTPException(status_code=404, detail="Categoria no encontrada")

        codigo = self._normalizar_codigo(payload.codigo) if payload.codigo is not None else None
        nombre = self._normalizar_nombre(payload.nombre) if payload.nombre is not None else None

        if codigo is not None:
            existente = self.repositorio.obtener_por_codigo_en_categoria(
                db=db,
                categoria_id=categoria_id_objetivo,
                codigo=codigo,
            )
            if existente and existente.id != contexto.id:
                raise HTTPException(status_code=400, detail="Ya existe un contexto con ese codigo en la categoria")

        if nombre is not None:
            existente = self.repositorio.obtener_por_nombre_en_categoria(
                db=db,
                categoria_id=categoria_id_objetivo,
                nombre=nombre,
            )
            if existente and existente.id != contexto.id:
                raise HTTPException(status_code=400, detail="Ya existe un contexto con ese nombre en la categoria")

        return self.repositorio.actualizar(
            db=db,
            contexto=contexto,
            categoria_id=payload.categoria_id,
            codigo=codigo,
            nombre=nombre,
            descripcion=payload.descripcion,
            activo=payload.activo,
        )

    def eliminar(self, db: Session, contexto_id: int) -> None:
        contexto = self.repositorio.obtener_por_id(db=db, contexto_id=contexto_id)
        if not contexto:
            raise HTTPException(status_code=404, detail="Contexto no encontrado")
        self.repositorio.eliminar(db=db, contexto=contexto)


class ServicioCategorias:
    """Reglas de negocio para CRUD de categorias."""

    def __init__(self) -> None:
        self.repositorio = RepositorioCategorias()
        self.repo_sedes = RepositorioSedes()

    @staticmethod
    def _normalizar_codigo(codigo: str) -> str:
        return codigo.strip().lower()

    @staticmethod
    def _normalizar_nombre(nombre: str) -> str:
        return nombre.strip()

    def listar(
        self,
        db: Session,
        solo_activos: bool | None = None,
        sede_id: int | None = None,
    ):
        return self.repositorio.listar(
            db=db,
            solo_activos=solo_activos,
            sede_id=sede_id,
        )

    def obtener(self, db: Session, categoria_id: int):
        categoria = self.repositorio.obtener_por_id(db=db, categoria_id=categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")
        return categoria

    def crear(self, db: Session, payload: CrearCategoria):
        if not self.repo_sedes.obtener_por_id(db=db, sede_id=payload.sede_id):
            raise HTTPException(status_code=404, detail="Sede no encontrada")

        codigo = self._normalizar_codigo(payload.codigo)
        nombre = self._normalizar_nombre(payload.nombre)

        if self.repositorio.obtener_por_codigo_en_sede(db=db, sede_id=payload.sede_id, codigo=codigo):
            raise HTTPException(status_code=400, detail="Ya existe una categoria con ese codigo en la sede")

        if self.repositorio.obtener_por_nombre_en_sede(db=db, sede_id=payload.sede_id, nombre=nombre):
            raise HTTPException(status_code=400, detail="Ya existe una categoria con ese nombre en la sede")

        return self.repositorio.crear(
            db=db,
            sede_id=payload.sede_id,
            codigo=codigo,
            nombre=nombre,
            descripcion=payload.descripcion,
            activo=payload.activo,
        )

    def actualizar(self, db: Session, categoria_id: int, payload: ActualizarCategoria):
        categoria = self.repositorio.obtener_por_id(db=db, categoria_id=categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")

        sede_id_objetivo = payload.sede_id if payload.sede_id is not None else categoria.sede_id
        if not self.repo_sedes.obtener_por_id(db=db, sede_id=sede_id_objetivo):
            raise HTTPException(status_code=404, detail="Sede no encontrada")

        codigo = self._normalizar_codigo(payload.codigo) if payload.codigo is not None else None
        nombre = self._normalizar_nombre(payload.nombre) if payload.nombre is not None else None

        if codigo is not None:
            existente = self.repositorio.obtener_por_codigo_en_sede(
                db=db,
                sede_id=sede_id_objetivo,
                codigo=codigo,
            )
            if existente and existente.id != categoria.id:
                raise HTTPException(status_code=400, detail="Ya existe una categoria con ese codigo en la sede")

        if nombre is not None:
            existente = self.repositorio.obtener_por_nombre_en_sede(
                db=db,
                sede_id=sede_id_objetivo,
                nombre=nombre,
            )
            if existente and existente.id != categoria.id:
                raise HTTPException(status_code=400, detail="Ya existe una categoria con ese nombre en la sede")

        return self.repositorio.actualizar(
            db=db,
            categoria=categoria,
            sede_id=payload.sede_id,
            codigo=codigo,
            nombre=nombre,
            descripcion=payload.descripcion,
            activo=payload.activo,
        )

    def eliminar(self, db: Session, categoria_id: int) -> None:
        categoria = self.repositorio.obtener_por_id(db=db, categoria_id=categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")
        try:
            self.repositorio.eliminar(db=db, categoria=categoria)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar la categoria porque tiene citas o historial asociado",
            )


class ServicioSedes:
    """Reglas de negocio para CRUD de sedes."""

    def __init__(self) -> None:
        self.repositorio = RepositorioSedes()
        self.repo_categorias = RepositorioCategorias()

    @staticmethod
    def _normalizar_codigo(codigo: str) -> str:
        return codigo.strip().lower()

    @staticmethod
    def _normalizar_nombre(nombre: str) -> str:
        return nombre.strip()

    def listar(
        self,
        db: Session,
        solo_activos: bool | None = None,
    ):
        return self.repositorio.listar(
            db=db,
            solo_activos=solo_activos,
        )

    def obtener(self, db: Session, sede_id: int):
        sede = self.repositorio.obtener_por_id(db=db, sede_id=sede_id)
        if not sede:
            raise HTTPException(status_code=404, detail="Sede no encontrada")
        return sede

    def crear(self, db: Session, payload: CrearSede):
        codigo = self._normalizar_codigo(payload.codigo)
        nombre = self._normalizar_nombre(payload.nombre)

        if self.repositorio.obtener_por_codigo(db=db, codigo=codigo):
            raise HTTPException(status_code=400, detail="Ya existe una sede con ese codigo")

        if self.repositorio.obtener_por_nombre(db=db, nombre=nombre):
            raise HTTPException(status_code=400, detail="Ya existe una sede con ese nombre")

        return self.repositorio.crear(
            db=db,
            codigo=codigo,
            nombre=nombre,
            ubicacion=payload.ubicacion,
            descripcion=payload.descripcion,
            es_publica=payload.es_publica,
            filtrar_citas_por_programa=payload.filtrar_citas_por_programa,
            activo=payload.activo,
        )

    def actualizar(self, db: Session, sede_id: int, payload: ActualizarSede):
        sede = self.repositorio.obtener_por_id(db=db, sede_id=sede_id)
        if not sede:
            raise HTTPException(status_code=404, detail="Sede no encontrada")

        codigo = self._normalizar_codigo(payload.codigo) if payload.codigo is not None else None
        nombre = self._normalizar_nombre(payload.nombre) if payload.nombre is not None else None

        if codigo is not None:
            existente = self.repositorio.obtener_por_codigo(db=db, codigo=codigo)
            if existente and existente.id != sede.id:
                raise HTTPException(status_code=400, detail="Ya existe una sede con ese codigo")

        if nombre is not None:
            existente = self.repositorio.obtener_por_nombre(db=db, nombre=nombre)
            if existente and existente.id != sede.id:
                raise HTTPException(status_code=400, detail="Ya existe una sede con ese nombre")

        return self.repositorio.actualizar(
            db=db,
            sede=sede,
            codigo=codigo,
            nombre=nombre,
            ubicacion=payload.ubicacion,
            descripcion=payload.descripcion,
            es_publica=payload.es_publica,
            filtrar_citas_por_programa=payload.filtrar_citas_por_programa,
            activo=payload.activo,
        )

    def eliminar(self, db: Session, sede_id: int) -> None:
        sede = self.repositorio.obtener_por_id(db=db, sede_id=sede_id)
        if not sede:
            raise HTTPException(status_code=404, detail="Sede no encontrada")
        try:
            self.repositorio.eliminar(db=db, sede=sede)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar la sede porque existen citas o historial asociado en sus contextos",
            )


class ServicioHorariosSede:
    """Reglas de negocio para CRUD de bloques horarios por sede."""

    def __init__(self) -> None:
        self.repositorio = RepositorioHorariosSede()
        self.repo_sedes = RepositorioSedes()

    @staticmethod
    def _validar_rango_horas(hora_inicio: time, hora_fin: time) -> None:
        if hora_inicio >= hora_fin:
            raise HTTPException(
                status_code=400,
                detail="La hora de inicio debe ser menor a la hora de fin",
            )

    @staticmethod
    def _se_solapan(inicio_a: time, fin_a: time, inicio_b: time, fin_b: time) -> bool:
        return inicio_a < fin_b and fin_a > inicio_b

    def _validar_sin_solapes(
        self,
        db: Session,
        sede_id: int,
        dia_semana: int,
        hora_inicio: time,
        hora_fin: time,
        excluir_horario_id: int | None = None,
    ) -> None:
        horarios_mismo_dia = self.repositorio.listar_por_sede(db=db, sede_id=sede_id, solo_activos=None)
        for horario in horarios_mismo_dia:
            if horario.dia_semana != dia_semana:
                continue
            if excluir_horario_id is not None and horario.id == excluir_horario_id:
                continue
            if self._se_solapan(hora_inicio, hora_fin, horario.hora_inicio, horario.hora_fin):
                raise HTTPException(
                    status_code=400,
                    detail="El bloque horario se solapa con otro bloque existente para ese día",
                )

    def listar(self, db: Session, sede_id: int, solo_activos: bool | None = None):
        sede = self.repo_sedes.obtener_por_id(db=db, sede_id=sede_id)
        if not sede:
            raise HTTPException(status_code=404, detail="Sede no encontrada")
        return self.repositorio.listar_por_sede(db=db, sede_id=sede_id, solo_activos=solo_activos)

    def crear(self, db: Session, sede_id: int, payload: CrearHorarioSede):
        sede = self.repo_sedes.obtener_por_id(db=db, sede_id=sede_id)
        if not sede:
            raise HTTPException(status_code=404, detail="Sede no encontrada")

        self._validar_rango_horas(payload.hora_inicio, payload.hora_fin)
        self._validar_sin_solapes(
            db=db,
            sede_id=sede_id,
            dia_semana=payload.dia_semana,
            hora_inicio=payload.hora_inicio,
            hora_fin=payload.hora_fin,
        )

        return self.repositorio.crear(
            db=db,
            sede_id=sede_id,
            dia_semana=payload.dia_semana,
            hora_inicio=payload.hora_inicio,
            hora_fin=payload.hora_fin,
            activo=payload.activo,
        )

    def crear_lote(self, db: Session, sede_id: int, payload: CrearHorarioSedeLote):
        sede = self.repo_sedes.obtener_por_id(db=db, sede_id=sede_id)
        if not sede:
            raise HTTPException(status_code=404, detail="Sede no encontrada")

        horarios_existentes = self.repositorio.listar_por_sede(db=db, sede_id=sede_id, solo_activos=None)
        rangos_por_dia: dict[int, list[tuple[time, time]]] = {}

        for horario in horarios_existentes:
            rangos_por_dia.setdefault(horario.dia_semana, []).append((horario.hora_inicio, horario.hora_fin))

        bloques_a_crear: list[dict] = []
        for bloque in payload.bloques:
            self._validar_rango_horas(bloque.hora_inicio, bloque.hora_fin)

            rangos_dia = rangos_por_dia.setdefault(bloque.dia_semana, [])
            for inicio_existente, fin_existente in rangos_dia:
                if self._se_solapan(bloque.hora_inicio, bloque.hora_fin, inicio_existente, fin_existente):
                    raise HTTPException(
                        status_code=400,
                        detail="El lote contiene bloques solapados con horarios existentes o entre sí",
                    )

            rangos_dia.append((bloque.hora_inicio, bloque.hora_fin))
            bloques_a_crear.append(
                {
                    "sede_id": sede_id,
                    "dia_semana": bloque.dia_semana,
                    "hora_inicio": bloque.hora_inicio,
                    "hora_fin": bloque.hora_fin,
                    "activo": bloque.activo,
                }
            )

        return self.repositorio.crear_lote(db=db, bloques=bloques_a_crear)

    def actualizar(self, db: Session, sede_id: int, horario_id: int, payload: ActualizarHorarioSede):
        sede = self.repo_sedes.obtener_por_id(db=db, sede_id=sede_id)
        if not sede:
            raise HTTPException(status_code=404, detail="Sede no encontrada")

        horario = self.repositorio.obtener_por_id(db=db, horario_id=horario_id)
        if not horario or horario.sede_id != sede_id:
            raise HTTPException(status_code=404, detail="Horario no encontrado para la sede indicada")

        dia_objetivo = payload.dia_semana if payload.dia_semana is not None else horario.dia_semana
        inicio_objetivo = payload.hora_inicio if payload.hora_inicio is not None else horario.hora_inicio
        fin_objetivo = payload.hora_fin if payload.hora_fin is not None else horario.hora_fin

        self._validar_rango_horas(inicio_objetivo, fin_objetivo)
        self._validar_sin_solapes(
            db=db,
            sede_id=sede_id,
            dia_semana=dia_objetivo,
            hora_inicio=inicio_objetivo,
            hora_fin=fin_objetivo,
            excluir_horario_id=horario.id,
        )

        return self.repositorio.actualizar(
            db=db,
            horario=horario,
            dia_semana=payload.dia_semana,
            hora_inicio=payload.hora_inicio,
            hora_fin=payload.hora_fin,
            activo=payload.activo,
        )

    def eliminar(self, db: Session, sede_id: int, horario_id: int) -> None:
        sede = self.repo_sedes.obtener_por_id(db=db, sede_id=sede_id)
        if not sede:
            raise HTTPException(status_code=404, detail="Sede no encontrada")

        horario = self.repositorio.obtener_por_id(db=db, horario_id=horario_id)
        if not horario or horario.sede_id != sede_id:
            raise HTTPException(status_code=404, detail="Horario no encontrado para la sede indicada")

        self.repositorio.eliminar(db=db, horario=horario)
