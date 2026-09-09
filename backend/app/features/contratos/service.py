"""Lógica de contratos (registro informativo, sin contabilidad).

Ver docs/features/contratos/spec.md §3.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import DatosInvalidos
from app.features.contratos.models import Contrato
from app.features.terceros.service import obtener_tercero


async def registrar_contrato(
    session: AsyncSession,
    *,
    tercero_id: int,
    objeto: str,
    valor: Decimal,
    fecha_inicio: date,
    fecha_fin: date | None = None,
) -> Contrato:
    await obtener_tercero(session, tercero_id)  # 404 si no existe

    if fecha_fin is not None and fecha_fin < fecha_inicio:
        raise DatosInvalidos("fecha_fin no puede ser anterior a fecha_inicio")

    contrato = Contrato(
        tercero_id=tercero_id,
        objeto=objeto,
        valor=valor,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    session.add(contrato)
    await session.commit()
    await session.refresh(contrato)
    return contrato


async def listar_contratos(session: AsyncSession) -> list[Contrato]:
    return list(
        (await session.execute(select(Contrato).order_by(Contrato.id))).scalars().all()
    )
