"""contratos — servicio. Ver docs/features/contratos/spec.md §7."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.contabilidad.models import Asiento
from app.core.errors import DatosInvalidos, NoEncontrado
from app.features.contratos.models import EstadoContrato
from app.features.contratos.service import registrar_contrato
from app.features.terceros.models import TipoTercero
from app.features.terceros.service import crear_tercero


async def _tercero(session):
    return await crear_tercero(
        session, nombre="Arrendador", nit_cedula="1", tipo=TipoTercero.PROVEEDOR
    )


async def test_crear_contrato_ok(db_session):
    t = await _tercero(db_session)
    c = await registrar_contrato(
        db_session,
        tercero_id=t.id,
        objeto="Arriendo bodega",
        valor=Decimal("2000000"),
        fecha_inicio=date(2026, 9, 1),
        fecha_fin=date(2027, 9, 1),
    )
    assert c.id is not None
    assert c.estado is EstadoContrato.VIGENTE


async def test_contrato_tercero_inexistente(db_session):
    with pytest.raises(NoEncontrado):
        await registrar_contrato(
            db_session,
            tercero_id=9999,
            objeto="x",
            valor=Decimal("1"),
            fecha_inicio=date(2026, 9, 1),
        )


async def test_contrato_fecha_fin_antes_de_inicio(db_session):
    t = await _tercero(db_session)
    with pytest.raises(DatosInvalidos):
        await registrar_contrato(
            db_session,
            tercero_id=t.id,
            objeto="x",
            valor=Decimal("1"),
            fecha_inicio=date(2026, 9, 1),
            fecha_fin=date(2026, 8, 1),
        )


async def test_contrato_no_genera_asiento(db_session):
    t = await _tercero(db_session)
    await registrar_contrato(
        db_session,
        tercero_id=t.id,
        objeto="x",
        valor=Decimal("1"),
        fecha_inicio=date(2026, 9, 1),
    )
    n = (await db_session.execute(select(func.count()).select_from(Asiento))).scalar_one()
    assert n == 0
