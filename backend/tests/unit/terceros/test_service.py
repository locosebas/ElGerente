"""terceros — servicio. Ver docs/features/terceros/spec.md §7."""
from __future__ import annotations

import pytest

from app.core.errors import NoEncontrado
from app.features.terceros.models import TipoTercero
from app.features.terceros.service import (
    crear_tercero,
    listar_terceros,
    obtener_tercero,
)


async def test_crear_tercero_devuelve_id(db_session):
    t = await crear_tercero(
        db_session, nombre="Proveedor SAS", nit_cedula="900111", tipo=TipoTercero.PROVEEDOR
    )
    assert t.id is not None
    assert t.tipo is TipoTercero.PROVEEDOR


async def test_listar_terceros_filtra_por_tipo(db_session):
    await crear_tercero(db_session, nombre="Cli", nit_cedula="1", tipo=TipoTercero.CLIENTE)
    await crear_tercero(db_session, nombre="Prov", nit_cedula="2", tipo=TipoTercero.PROVEEDOR)
    clientes = await listar_terceros(db_session, tipo=TipoTercero.CLIENTE)
    assert [t.nombre for t in clientes] == ["Cli"]


async def test_obtener_tercero_inexistente(db_session):
    with pytest.raises(NoEncontrado):
        await obtener_tercero(db_session, 9999)
