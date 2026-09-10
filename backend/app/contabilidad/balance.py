"""Cálculo del balance: saldo de cada cuenta, con filtro de libro y de periodo.

Una sola consulta de agregación (no itera objetos Python). Ver
docs/features/balance/spec.md.
"""
from __future__ import annotations

import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contabilidad.models import (
    Asiento,
    Cuenta,
    LibroContable,
    LineaAsiento,
    Naturaleza,
)
from app.core.errors import DatosInvalidos


class FiltroLibro(str, enum.Enum):
    OFICIAL = "oficial"
    INTERNA = "interna"
    TODOS = "todos"


def condiciones_asiento(
    libro: FiltroLibro, desde: date | None, hasta: date | None
) -> list:
    """Filtros a aplicar sobre `asiento` (libro + rango de fechas).

    Se usan en el ON de un LEFT JOIN, no en el WHERE, para que las cuentas
    sin movimientos que cumplan el filtro sigan apareciendo con saldo 0.
    """
    if desde is not None and hasta is not None and desde > hasta:
        raise DatosInvalidos("La fecha 'desde' no puede ser posterior a 'hasta'")
    cond: list = []
    if libro == FiltroLibro.OFICIAL:
        cond.append(Asiento.libro == LibroContable.OFICIAL)
    elif libro == FiltroLibro.INTERNA:
        cond.append(Asiento.libro == LibroContable.INTERNA)
    if desde is not None:
        cond.append(Asiento.fecha >= desde)
    if hasta is not None:
        cond.append(Asiento.fecha <= hasta)
    return cond


def _saldo(tipo, total_debito, total_credito) -> Decimal:
    td = Decimal(str(total_debito))
    tc = Decimal(str(total_credito))
    return td - tc if tipo.naturaleza is Naturaleza.DEUDORA else tc - td


async def calcular_balance(
    session: AsyncSession,
    *,
    libro: FiltroLibro = FiltroLibro.OFICIAL,
    desde: date | None = None,
    hasta: date | None = None,
) -> list[dict]:
    """Devuelve TODAS las cuentas del plan (incluso con saldo 0), ordenadas
    por código, con su saldo según la naturaleza de la cuenta y los filtros.
    """
    cond = condiciones_asiento(libro, desde, hasta)
    incluye = Asiento.id.isnot(None)  # el asiento pasó el filtro del JOIN
    monto_debito = case((incluye, LineaAsiento.debito), else_=0)
    monto_credito = case((incluye, LineaAsiento.credito), else_=0)

    stmt = (
        select(
            Cuenta.codigo,
            Cuenta.nombre,
            Cuenta.tipo,
            func.coalesce(func.sum(monto_debito), 0),
            func.coalesce(func.sum(monto_credito), 0),
        )
        .select_from(Cuenta)
        .outerjoin(LineaAsiento, LineaAsiento.cuenta_id == Cuenta.id)
        .outerjoin(Asiento, and_(Asiento.id == LineaAsiento.asiento_id, *cond))
        .group_by(Cuenta.id)
        .order_by(Cuenta.codigo)
    )

    return [
        {
            "cuenta_codigo": codigo,
            "cuenta_nombre": nombre,
            "tipo": tipo,
            "saldo": _saldo(tipo, td, tc),
        }
        for codigo, nombre, tipo, td, tc in await session.execute(stmt)
    ]
