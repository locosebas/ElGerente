"""facturas — servicio. Ver docs/features/facturas/spec.md §7."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.contabilidad.models import Asiento
from app.core.errors import NoEncontrado
from app.features.facturas.models import EstadoFactura, TipoFactura
from app.features.facturas.service import registrar_factura
from app.features.terceros.models import TipoTercero
from app.features.terceros.service import crear_tercero

HOY = date(2026, 9, 1)


async def _tercero(session, tipo=TipoTercero.PROVEEDOR):
    return await crear_tercero(session, nombre="X", nit_cedula="1", tipo=tipo)


async def _asiento_de(session, factura) -> Asiento:
    return (
        await session.execute(select(Asiento).where(Asiento.id == factura.asiento_id))
    ).scalar_one()


def _mov(asiento: Asiento, codigo: str) -> tuple[Decimal, Decimal]:
    linea = next(ln for ln in asiento.lineas if ln.cuenta.codigo == codigo)
    return linea.debito, linea.credito


async def test_total_se_calcula_en_servidor(db_session):
    t = await _tercero(db_session)
    f = await registrar_factura(
        db_session,
        tipo=TipoFactura.RECIBIDA,
        numero="F1",
        fecha=HOY,
        tercero_id=t.id,
        subtotal=Decimal("500000"),
        iva=Decimal("95000"),
    )
    assert f.total == Decimal("595000")


async def test_factura_recibida_genera_asiento_correcto(db_session):
    t = await _tercero(db_session)
    f = await registrar_factura(
        db_session,
        tipo=TipoFactura.RECIBIDA,
        numero="F1",
        fecha=HOY,
        tercero_id=t.id,
        subtotal=Decimal("500000"),
        iva=Decimal("95000"),
    )
    asiento = await _asiento_de(db_session, f)
    assert _mov(asiento, "5195") == (Decimal("500000.00"), Decimal("0.00"))
    assert _mov(asiento, "2408") == (Decimal("95000.00"), Decimal("0.00"))
    assert _mov(asiento, "2205") == (Decimal("0.00"), Decimal("595000.00"))
    assert asiento.cuadra()
    assert asiento.documento_soporte == "Factura recibida F1"


async def test_factura_emitida_genera_asiento_correcto(db_session):
    t = await _tercero(db_session, TipoTercero.CLIENTE)
    f = await registrar_factura(
        db_session,
        tipo=TipoFactura.EMITIDA,
        numero="E1",
        fecha=HOY,
        tercero_id=t.id,
        subtotal=Decimal("1000000"),
        iva=Decimal("190000"),
    )
    asiento = await _asiento_de(db_session, f)
    assert _mov(asiento, "1305") == (Decimal("1190000.00"), Decimal("0.00"))
    assert _mov(asiento, "4135") == (Decimal("0.00"), Decimal("1000000.00"))
    assert _mov(asiento, "2408") == (Decimal("0.00"), Decimal("190000.00"))
    assert asiento.cuadra()


async def test_factura_sin_iva_cuadra(db_session):
    t = await _tercero(db_session)
    f = await registrar_factura(
        db_session,
        tipo=TipoFactura.RECIBIDA,
        numero="F0",
        fecha=HOY,
        tercero_id=t.id,
        subtotal=Decimal("100000"),
        iva=Decimal("0"),
    )
    asiento = await _asiento_de(db_session, f)
    assert len(asiento.lineas) == 2
    assert asiento.cuadra()


async def test_factura_tercero_inexistente(db_session):
    with pytest.raises(NoEncontrado):
        await registrar_factura(
            db_session,
            tipo=TipoFactura.RECIBIDA,
            numero="F1",
            fecha=HOY,
            tercero_id=9999,
            subtotal=Decimal("1000"),
            iva=Decimal("0"),
        )


async def test_factura_nace_pendiente_y_enlaza_asiento(db_session):
    t = await _tercero(db_session)
    f = await registrar_factura(
        db_session,
        tipo=TipoFactura.RECIBIDA,
        numero="F1",
        fecha=HOY,
        tercero_id=t.id,
        subtotal=Decimal("1000"),
        iva=Decimal("0"),
    )
    assert f.estado is EstadoFactura.PENDIENTE
    assert f.asiento_id is not None
