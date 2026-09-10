"""balance / detalle de cuenta — extracto con saldo acumulado. Ver spec §7."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.contabilidad.asientos import crear_asiento, cuenta_requerida
from app.contabilidad.detalle_cuenta import movimientos_de_cuenta
from app.contabilidad.models import LibroContable, LineaAsiento, OrigenAsiento
from app.core.errors import NoEncontrado


async def _linea(session, codigo, debito="0", credito="0") -> LineaAsiento:
    cuenta = await cuenta_requerida(session, codigo)
    return LineaAsiento(cuenta=cuenta, debito=Decimal(debito), credito=Decimal(credito))


async def test_movimientos_de_cuenta_saldo_acumulado(db_session):
    # Dos gastos a Caja: -30 y luego -50 acumulado (Caja es activo).
    for monto, fecha in [("30", date(2026, 6, 1)), ("20", date(2026, 6, 10))]:
        await crear_asiento(
            db_session,
            fecha=fecha,
            descripcion=f"gasto {monto}",
            origen=OrigenAsiento.MANUAL,
            lineas=[
                await _linea(db_session, "5195", debito=monto),
                await _linea(db_session, "1105", credito=monto),
            ],
            libro=LibroContable.OFICIAL,
            documento_soporte="x",
        )
    await db_session.commit()

    detalle = await movimientos_de_cuenta(db_session, "1105")
    saldos = [m["saldo_acumulado"] for m in detalle["movimientos"]]
    assert saldos == [Decimal("-30.00"), Decimal("-50.00")]
    assert detalle["saldo_final"] == Decimal("-50.00")
    assert detalle["cuenta_nombre"] == "Caja"


async def test_movimientos_de_cuenta_codigo_inexistente(db_session):
    with pytest.raises(NoEncontrado):
        await movimientos_de_cuenta(db_session, "9999")
