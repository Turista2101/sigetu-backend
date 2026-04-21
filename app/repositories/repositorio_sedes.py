"""Repositorios de acceso a datos para contextos, categorias y sedes."""

from sqlalchemy.orm import Session

from app.models.modelo_categoria import Categoria
from app.models.modelo_contexto import Contexto
from app.models.modelo_horario_sede import HorarioSede
from app.models.modelo_sede import Sede


class RepositorioContextos:
    """Operaciones CRUD para contextos."""

    def listar(
        self,
        db: Session,
        solo_activos: bool | None = None,
        categoria_id: int | None = None,
    ) -> list[Contexto]:
        consulta = db.query(Contexto)
        if solo_activos is not None:
            consulta = consulta.filter(Contexto.activo == solo_activos)
        if categoria_id is not None:
            consulta = consulta.filter(Contexto.categoria_id == categoria_id)
        return consulta.order_by(Contexto.nombre.asc()).all()

    def obtener_por_id(self, db: Session, contexto_id: int) -> Contexto | None:
        return db.query(Contexto).filter(Contexto.id == contexto_id).first()

    def obtener_por_codigo_en_categoria(self, db: Session, categoria_id: int, codigo: str) -> Contexto | None:
        return (
            db.query(Contexto)
            .filter(Contexto.categoria_id == categoria_id, Contexto.codigo == codigo)
            .first()
        )

    def obtener_por_nombre_en_categoria(self, db: Session, categoria_id: int, nombre: str) -> Contexto | None:
        return (
            db.query(Contexto)
            .filter(Contexto.categoria_id == categoria_id, Contexto.nombre == nombre)
            .first()
        )

    def crear(self, db: Session, **campos) -> Contexto:
        contexto = Contexto(**campos)
        db.add(contexto)
        db.commit()
        db.refresh(contexto)
        return contexto

    def actualizar(self, db: Session, contexto: Contexto, **campos) -> Contexto:
        for campo, valor in campos.items():
            if valor is not None:
                setattr(contexto, campo, valor)
        db.commit()
        db.refresh(contexto)
        return contexto

    def eliminar(self, db: Session, contexto: Contexto) -> None:
        db.delete(contexto)
        db.commit()


class RepositorioCategorias:
    """Operaciones CRUD para categorias."""

    def listar(
        self,
        db: Session,
        solo_activos: bool | None = None,
        sede_id: int | None = None,
    ) -> list[Categoria]:
        consulta = db.query(Categoria)
        if solo_activos is not None:
            consulta = consulta.filter(Categoria.activo == solo_activos)
        if sede_id is not None:
            consulta = consulta.filter(Categoria.sede_id == sede_id)
        return consulta.order_by(Categoria.nombre.asc()).all()

    def obtener_por_id(self, db: Session, categoria_id: int) -> Categoria | None:
        return db.query(Categoria).filter(Categoria.id == categoria_id).first()

    def obtener_por_codigo_en_sede(self, db: Session, sede_id: int, codigo: str) -> Categoria | None:
        return (
            db.query(Categoria)
            .filter(Categoria.sede_id == sede_id, Categoria.codigo == codigo)
            .first()
        )

    def obtener_por_nombre_en_sede(self, db: Session, sede_id: int, nombre: str) -> Categoria | None:
        return (
            db.query(Categoria)
            .filter(Categoria.sede_id == sede_id, Categoria.nombre == nombre)
            .first()
        )

    def crear(self, db: Session, **campos) -> Categoria:
        categoria = Categoria(**campos)
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
        return categoria

    def actualizar(self, db: Session, categoria: Categoria, **campos) -> Categoria:
        for campo, valor in campos.items():
            if valor is not None:
                setattr(categoria, campo, valor)
        db.commit()
        db.refresh(categoria)
        return categoria

    def eliminar(self, db: Session, categoria: Categoria) -> None:
        db.delete(categoria)
        db.commit()


class RepositorioSedes:
    """Operaciones CRUD para sedes."""

    def listar(
        self,
        db: Session,
        solo_activos: bool | None = None,
    ) -> list[Sede]:
        consulta = db.query(Sede)
        if solo_activos is not None:
            consulta = consulta.filter(Sede.activo == solo_activos)
        return consulta.order_by(Sede.nombre.asc()).all()

    def obtener_por_id(self, db: Session, sede_id: int) -> Sede | None:
        return db.query(Sede).filter(Sede.id == sede_id).first()

    def obtener_por_codigo(self, db: Session, codigo: str) -> Sede | None:
        return db.query(Sede).filter(Sede.codigo == codigo).first()

    def obtener_por_nombre(self, db: Session, nombre: str) -> Sede | None:
        return db.query(Sede).filter(Sede.nombre == nombre).first()

    def crear(self, db: Session, **campos) -> Sede:
        sede = Sede(**campos)
        db.add(sede)
        db.commit()
        db.refresh(sede)
        return sede

    def actualizar(self, db: Session, sede: Sede, **campos) -> Sede:
        for campo, valor in campos.items():
            if valor is not None:
                setattr(sede, campo, valor)
        db.commit()
        db.refresh(sede)
        return sede

    def eliminar(self, db: Session, sede: Sede) -> None:
        db.delete(sede)
        db.commit()


class RepositorioHorariosSede:
    """Operaciones CRUD para bloques horarios de sedes."""

    def listar_por_sede(
        self,
        db: Session,
        sede_id: int,
        solo_activos: bool | None = None,
    ) -> list[HorarioSede]:
        consulta = db.query(HorarioSede).filter(HorarioSede.sede_id == sede_id)
        if solo_activos is not None:
            consulta = consulta.filter(HorarioSede.activo == solo_activos)
        return consulta.order_by(HorarioSede.dia_semana.asc(), HorarioSede.hora_inicio.asc()).all()

    def obtener_por_id(self, db: Session, horario_id: int) -> HorarioSede | None:
        return db.query(HorarioSede).filter(HorarioSede.id == horario_id).first()

    def crear(self, db: Session, **campos) -> HorarioSede:
        horario = HorarioSede(**campos)
        db.add(horario)
        db.commit()
        db.refresh(horario)
        return horario

    def crear_lote(self, db: Session, bloques: list[dict]) -> list[HorarioSede]:
        horarios = [HorarioSede(**bloque) for bloque in bloques]
        db.add_all(horarios)
        db.commit()
        for horario in horarios:
            db.refresh(horario)
        return horarios

    def actualizar(self, db: Session, horario: HorarioSede, **campos) -> HorarioSede:
        for campo, valor in campos.items():
            if valor is not None:
                setattr(horario, campo, valor)
        db.commit()
        db.refresh(horario)
        return horario

    def eliminar(self, db: Session, horario: HorarioSede) -> None:
        db.delete(horario)
        db.commit()
