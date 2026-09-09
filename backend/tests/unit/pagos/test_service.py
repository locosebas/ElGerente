"""pagos — servicio. Ver docs/features/pagos/spec.md §7."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.contabilidad.models import Asiento
from app.core.errors import Conflicto, DatosInvalidos, NoEncontrado
from app.features.facturas.models import EstadoFactura, TipoFactura
from app.features.facturas.service import registrar_factura
from app.features.pagos.service import pagar_factura
from app.features.terceros.models import TipoTercero
from app.features.terceros.service import crear_tercero

HOY = date(2026, 9, 1)


async def _factura(session, tipo: TipoFactura):
    tt = TipoTercero.PROVEEDOR if tipo is TipoFactura.RECIBIDA else TipoTercero.CLIENTE
    t = await crear_tercero(session, nombre="X", nit_cedula="1", tipo=tt)
    return await registrar_factura(
        session,
        tipo=tipo,
        numero="N1",
        fecha=HOY,
        tercero_id=t.id,
        subtotal=Decimal("100000"),
        iva=Decimal("0"),
    )


def _mov(asiento: Asiento, codigo: str) -> tuple[Decimal, Decimal]:
    linea = next(ln for ln in asiento.lineas if ln.cuenta.codigo == codigo)
    return linea.debito, linea.credito


async def _ultimo_asiento(session) -> Asiento:
    return (
        await session.execute(select(Asiento).order_by(Asiento.id.desc()).limit(1))
    ).scalar_one()


async def test_pago_recibida_genera_asiento(db_session):
    f = await _factura(db_session, TipoFactura.RECIBIDA)
    f = await pagar_factura(db_session, factura_id=f.id, medio_pago="bancos", fecha=HOY)
    assert f.estado is EstadoFactura.PAGADA
    asiento = await _ultimo_asiento(db_session)
    assert _mov(asiento, "2205") == (Decimal("100000.00"), Decimal("0.00"))
    assert _mov(asiento, "1110") == (Decimal("0.00"), Decimal("100000.00"))


async def test_cobro_emitida_genera_asiento(db_session):
    f = await _factura(db_session, TipoFactura.EMITIDA)
    await pagar_factura(db_session, factura_id=f.id, medio_pago="caja", fecha=HOY)
    asiento = await _ultimo_asiento(db_session)
    assert _mov(asiento, "1105") == (Decimal("100000.00"), Decimal("0.00"))
    assert _mov(asiento, "1305") == (Decimal("0.00"), Decimal("100000.00"))


async def test_pagar_factura_inexistente(db_session):
    with pytest.raises(NoEncontrado):
        await pagar_factura(db_session, factura_id=9999, medio_pago="caja", fecha=HOY)


async def test_pagar_factura_ya_pagada(db_session):
    f = await _factura(db_session, TipoFactura.RECIBIDA)
    await pagar_factura(db_session, factura_id=f.id, medio_pago="caja", fecha=HOY)
    with pytest.raises(Conflicto):
        await pagar_factura(db_session, factura_id=f.id, medio_pago="caja", fecha=HOY)


async def test_medio_pago_invalido(db_session):
    f = await _factura(db_session, TipoFactura.RECIBIDA)
    with pytest.raises(DatosInvalidos):
        await pagar_factura(db_session, factura_id=f.id, medio_pago="tarjeta", fecha=HOY)
