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


async def _mov(session, tercero, **kw):
    kw.setdefault("fecha", HOY)
    kw.setdefault("descripcion", "prueba")
    kw.setdefault("libro", LibroContable.INTERNA)
    kw.setdefault("documento_soporte", None)
    return await registrar_movimiento_manual(session, tercero_id=tercero, **kw)


async def test_movimiento_oficial_con_soporte_ok(db_session, tercero_id):
    asiento = await _mov(
        db_session,
        tercero_id,
        descripcion="Ajuste caja menor",
        libro=LibroContable.OFICIAL,
        documento_soporte="Recibo #45",
        lineas=[_l("5195", debito="10000"), _l("1105", credito="10000")],
    )
    assert asiento.origen is OrigenAsiento.MANUAL
    assert asiento.tercero_id == tercero_id


async def test_movimiento_oficial_sin_soporte_falla(db_session, tercero_id):
    with pytest.raises(DatosInvalidos):
        await _mov(
            db_session,
            tercero_id,
            libro=LibroContable.OFICIAL,
            lineas=[_l("5195", debito="10000"), _l("1105", credito="10000")],
        )


async def test_movimiento_interno_sin_soporte_ok(db_session, tercero_id):
    asiento = await _mov(
        db_session,
        tercero_id,
        descripcion="Retiro del dueño",
        lineas=[_l("2905", debito="50000"), _l("1105", credito="50000")],
    )
    assert asiento.libro is LibroContable.INTERNA


async def test_movimiento_tercero_inexistente(db_session):
    with pytest.raises(NoEncontrado):
        await _mov(
            db_session,
            9999,
            lineas=[_l("2905", debito="1"), _l("1105", credito="1")],
        )


async def test_movimiento_menos_de_dos_lineas(db_session, tercero_id):
    with pytest.raises(DatosInvalidos):
        await _mov(db_session, tercero_id, lineas=[_l("1105", debito="1")])


async def test_movimiento_lineas_no_cuadran(db_session, tercero_id):
    with pytest.raises(DatosInvalidos):
        await _mov(
            db_session,
            tercero_id,
            lineas=[_l("5195", debito="100"), _l("1105", credito="90")],
        )
    await db_session.rollback()
    assert await _contar(db_session) == 0


async def test_movimiento_cuenta_inexistente(db_session, tercero_id):
    with pytest.raises(NoEncontrado):
        await _mov(
            db_session,
            tercero_id,
            lineas=[_l("9999", debito="1"), _l("1105", credito="1")],
        )
