"""Cálculo del balance: saldo acumulado por cuenta.

Una sola consulta de agregación (no itera objetos Python). Ver
docs/features/balance/spec.md.
"""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contabilidad.models import (
    Asiento,
    Cuenta,
    LibroContable,
    LineaAsiento,
    Naturaleza,
)


async def calcular_balance(
    session: AsyncSession, *, incluir_interna: bool = False
) -> list[dict]:
    """Devuelve TODAS las cuentas del plan (incluso con saldo 0), ordenadas
    por código, con su saldo según la naturaleza de la cuenta.

    Por defecto solo cuenta asientos de `libro = oficial`. Con
    `incluir_interna=True` suma también el libro interno.
    """
    if incluir_interna:
        monto_debito = LineaAsiento.debito
        monto_credito = LineaAsiento.credito
    else:
        es_oficial = Asiento.libro == LibroContable.OFICIAL
        monto_debito = case((es_oficial, LineaAsiento.debito), else_=0)
        monto_credito = case((es_oficial, LineaAsiento.credito), else_=0)

    stmt = (
        select(
            Cuenta.codigo,
            Cuenta.nombre,
            Cuenta.tipo,
            func.coalesce(func.sum(monto_debito), 0).label("total_debito"),
            func.coalesce(func.sum(monto_credito), 0).label("total_credito"),
        )
        .select_from(Cuenta)
        .outerjoin(LineaAsiento, LineaAsiento.cuenta_id == Cuenta.id)
        .outerjoin(Asiento, Asiento.id == LineaAsiento.asiento_id)
        .group_by(Cuenta.id)
        .order_by(Cuenta.codigo)
    )

    resultado: list[dict] = []
    for codigo, nombre, tipo, total_debito, total_credito in await session.execute(stmt):
        td = Decimal(str(total_debito))
        tc = Decimal(str(total_credito))
        if tipo.naturaleza is Naturaleza.DEUDORA:
            saldo = td - tc
        else:
            saldo = tc - td
        resultado.append(
            {
                "cuenta_codigo": codigo,
                "cuenta_nombre": nombre,
                "tipo": tipo,
                "saldo": saldo,
            }
        )
    return resultado
