"""contabilidad-nucleo — reglas de crear_asiento. Ver spec §7."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.contabilidad.asientos import (
    AsientoDesbalanceado,
    DocumentoSoporteRequerido,
    crear_asiento,
    cuenta_requerida,
)
from app.contabilidad.models import Asiento, LibroContable, LineaAsiento, OrigenAsiento

HOY = date(2026, 9, 1)


async def _linea(session, codigo, debito="0", credito="0") -> LineaAsiento:
    cuenta = await cuenta_requerida(session, codigo)
    return LineaAsiento(cuenta=cuenta, debito=Decimal(debito), credito=Decimal(credito))


async def _contar_asientos(session) -> int:
    return (await session.execute(select(func.count()).select_from(Asiento))).scalar_one()


async def test_asiento_que_cuadra_se_guarda(db_session):
    lineas = [
        await _linea(db_session, "5195", debito="100"),
        await _linea(db_session, "1105", credito="100"),
    ]
    asiento = await crear_asiento(
        db_session,
        fecha=HOY,
        descripcion="prueba",
        origen=OrigenAsiento.MANUAL,
        lineas=lineas,
        libro=LibroContable.INTERNA,
    )
    assert asiento.id is not None


async def test_asiento_descuadrado_no_deja_filas(db_session):
    lineas = [
        await _linea(db_session, "5195", debito="100"),
        await _linea(db_session, "1105", credito="99"),
    ]
    with pytest.raises(AsientoDesbalanceado):
        await crear_asiento(
            db_session,
            fecha=HOY,
            descripcion="descuadrado",
            origen=OrigenAsiento.MANUAL,
            lineas=lineas,
            libro=LibroContable.INTERNA,
        )
    await db_session.rollback()
    assert await _contar_asientos(db_session) == 0


async def test_oficial_sin_soporte_falla(db_session):
    lineas = [
        await _linea(db_session, "5195", debito="10"),
        await _linea(db_session, "1105", credito="10"),
    ]
    with pytest.raises(DocumentoSoporteRequerido):
        await crear_asiento(
            db_session,
            fecha=HOY,
            descripcion="oficial sin soporte",
            origen=OrigenAsiento.MANUAL,
            lineas=lineas,
            libro=LibroContable.OFICIAL,
            documento_soporte="   ",
        )


async def test_oficial_con_soporte_ok(db_session):
    lineas = [
        await _linea(db_session, "5195", debito="10"),
        await _linea(db_session, "1105", credito="10"),
    ]
    asiento = await crear_asiento(
        db_session,
        fecha=HOY,
        descripcion="oficial con soporte",
        origen=OrigenAsiento.MANUAL,
        lineas=lineas,
        libro=LibroContable.OFICIAL,
        documento_soporte="Recibo caja menor #1",
    )
    assert asiento.documento_soporte == "Recibo caja menor #1"


async def test_interna_ignora_soporte(db_session):
    lineas = [
        await _linea(db_session, "5195", debito="10"),
        await _linea(db_session, "1105", credito="10"),
    ]
    asiento = await crear_asiento(
        db_session,
        fecha=HOY,
        descripcion="interna",
        origen=OrigenAsiento.MANUAL,
        lineas=lineas,
        libro=LibroContable.INTERNA,
        documento_soporte="se ignora",
    )
    assert asiento.documento_soporte is None


async def test_cuadre_usa_decimal_exacto(db_session):
    # 0.10 + 0.20 == 0.30 exacto con Decimal (con float fallaría).
    lineas = [
        await _linea(db_session, "5195", debito="0.10"),
        await _linea(db_session, "5905", debito="0.20"),
        await _linea(db_session, "1105", credito="0.30"),
    ]
    asiento = await crear_asiento(
        db_session,
        fecha=HOY,
        descripcion="decimales",
        origen=OrigenAsiento.MANUAL,
        lineas=lineas,
        libro=LibroContable.INTERNA,
    )
    assert asiento.cuadra()
