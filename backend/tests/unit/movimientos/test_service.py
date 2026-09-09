"""movimientos — servicio. Ver docs/features/movimientos/spec.md §7."""
from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import func, select

from app.contabilidad.models import Asiento, LibroContable, OrigenAsiento
from app.core.errors import DatosInvalidos, NoEncontrado
from app.features.movimientos.service import registrar_movimiento_manual

HOY = date(2026, 9, 1)


def _l(codigo, debito="0", credito="0") -> dict:
    return {"cuenta_codigo": codigo, "debito": debito, "credito": credito}


async def _contar(session) -> int:
    return (await session.execute(select(func.count()).select_from(Asiento))).scalar_one()


async def test_movimiento_oficial_con_soporte_ok(db_session):
    asiento = await registrar_movimiento_manual(
        db_session,
        fecha=HOY,
        descripcion="Ajuste caja menor",
        libro=LibroContable.OFICIAL,
        documento_soporte="Recibo #45",
        lineas=[_l("5195", debito="10000"), _l("1105", credito="10000")],
    )
    assert asiento.origen is OrigenAsiento.MANUAL
    assert asiento.libro is LibroContable.OFICIAL


async def test_movimiento_oficial_sin_soporte_falla(db_session):
    with pytest.raises(DatosInvalidos):
        await registrar_movimiento_manual(
            db_session,
            fecha=HOY,
            descripcion="sin soporte",
            libro=LibroContable.OFICIAL,
            documento_soporte=None,
            lineas=[_l("5195", debito="10000"), _l("1105", credito="10000")],
        )


async def test_movimiento_interno_sin_soporte_ok(db_session):
    asiento = await registrar_movimiento_manual(
        db_session,
        fecha=HOY,
        descripcion="Retiro del dueño",
        libro=LibroContable.INTERNA,
        documento_soporte=None,
        lineas=[_l("2905", debito="50000"), _l("1105", credito="50000")],
    )
    assert asiento.libro is LibroContable.INTERNA


async def test_movimiento_menos_de_dos_lineas(db_session):
    with pytest.raises(DatosInvalidos):
        await registrar_movimiento_manual(
            db_session,
            fecha=HOY,
            descripcion="una línea",
            libro=LibroContable.INTERNA,
            documento_soporte=None,
            lineas=[_l("1105", debito="1")],
        )


async def test_movimiento_lineas_no_cuadran(db_session):
    with pytest.raises(DatosInvalidos):
        await registrar_movimiento_manual(
            db_session,
            fecha=HOY,
            descripcion="descuadrado",
            libro=LibroContable.INTERNA,
            documento_soporte=None,
            lineas=[_l("5195", debito="100"), _l("1105", credito="90")],
        )
    await db_session.rollback()
    assert await _contar(db_session) == 0


async def test_movimiento_cuenta_inexistente(db_session):
    with pytest.raises(NoEncontrado):
        await registrar_movimiento_manual(
            db_session,
            fecha=HOY,
            descripcion="cuenta mala",
            libro=LibroContable.INTERNA,
            documento_soporte=None,
            lineas=[_l("9999", debito="1"), _l("1105", credito="1")],
        )
