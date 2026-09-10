"""Extracto de una cuenta: sus movimientos con saldo acumulado.

Ver docs/features/balance/spec.md §3 (regla 6) y §5.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contabilidad.balance import FiltroLibro, condiciones_asiento
from app.contabilidad.models import Asiento, Cuenta, LineaAsiento, Naturaleza
from app.core.errors import NoEncontrado

_CERO = Decimal("0")


async def movimientos_de_cuenta(
    session: AsyncSession,
    codigo: str,
    *,
    libro: FiltroLibro = FiltroLibro.OFICIAL,
    desde: date | None = None,
    hasta: date | None = None,
) -> dict:
    cuenta = (
        await session.execute(select(Cuenta).where(Cuenta.codigo == codigo))
    ).scalar_one_or_none()
    if cuenta is None:
        raise NoEncontrado(f"La cuenta '{codigo}' no existe")

    cond = condiciones_asiento(libro, desde, hasta)
    stmt = (
        select(
            Asiento.id,
            Asiento.fecha,
            Asiento.descripcion,
            Asiento.origen,
            Asiento.libro,
            Asiento.documento_soporte,
            LineaAsiento.debito,
            LineaAsiento.credito,
        )
        .join(Asiento, Asiento.id == LineaAsiento.asiento_id)
        .where(LineaAsiento.cuenta_id == cuenta.id, *cond)
        .order_by(Asiento.fecha, Asiento.id)
    )

    deudora = cuenta.tipo.naturaleza is Naturaleza.DEUDORA
    saldo = _CERO
    movimientos: list[dict] = []
    for aid, fecha, desc, origen, lib, soporte, debito, credito in await session.execute(
        stmt
    ):
        saldo += (debito - credito) if deudora else (credito - debito)
        movimientos.append(
            {
                "asiento_id": aid,
                "fecha": fecha,
                "descripcion": desc,
                "origen": origen,
                "libro": lib,
                "documento_soporte": soporte,
                "debito": debito,
                "credito": credito,
                "saldo_acumulado": saldo,
            }
        )

    return {
        "cuenta_codigo": cuenta.codigo,
        "cuenta_nombre": cuenta.nombre,
        "tipo": cuenta.tipo,
        "saldo_final": saldo,
        "movimientos": movimientos,
    }
