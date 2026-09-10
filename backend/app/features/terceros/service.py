"""Lógica de terceros. Ver docs/features/terceros/spec.md."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NoEncontrado
from app.core.logging import log
from app.documentos.enlace import validar_enlace
from app.features.terceros.models import Tercero, TipoTercero

_log = log("terceros")


async def crear_tercero(
    session: AsyncSession,
    *,
    nombre: str,
    nit_cedula: str,
    tipo: TipoTercero,
    enlace_rut: str | None = None,
) -> Tercero:
    tercero = Tercero(
        nombre=nombre,
        nit_cedula=nit_cedula,
        tipo=tipo,
        enlace_rut=validar_enlace(enlace_rut),
    )
    session.add(tercero)
    await session.commit()
    await session.refresh(tercero)
    _log.info("Tercero #%d creado — %s (%s)", tercero.id, nombre, tipo.value)
    return tercero


async def actualizar_enlace_rut(
    session: AsyncSession, tercero_id: int, enlace_rut: str | None
) -> Tercero:
    tercero = await obtener_tercero(session, tercero_id)
    tercero.enlace_rut = validar_enlace(enlace_rut)
    await session.commit()
    await session.refresh(tercero)
    _log.info("Tercero #%d — enlace RUT actualizado", tercero_id)
    return tercero


async def listar_terceros(
    session: AsyncSession, *, tipo: TipoTercero | None = None
) -> list[Tercero]:
    stmt = select(Tercero).order_by(Tercero.id)
    if tipo is not None:
        stmt = stmt.where(Tercero.tipo == tipo)
    return list((await session.execute(stmt)).scalars().all())


async def obtener_tercero(session: AsyncSession, tercero_id: int) -> Tercero:
    tercero = await session.get(Tercero, tercero_id)
    if tercero is None:
        raise NoEncontrado(f"Tercero {tercero_id} no existe")
    return tercero
