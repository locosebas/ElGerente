"""Marca todo lo que está bajo tests/integration/ como `@pytest.mark.integration`
(para poder correr `pytest -m "not integration"`), y ayudas comunes.
"""
from __future__ import annotations

from decimal import Decimal

import pytest
import pytest_asyncio


def pytest_collection_modifyitems(items) -> None:
    for item in items:
        if "tests/integration/" in str(item.path).replace("\\", "/"):
            item.add_marker(pytest.mark.integration)


@pytest.fixture
def saldos():
    """Convierte la respuesta de GET /balance en {codigo: Decimal(saldo)}."""

    def _saldos(balance_json: list[dict]) -> dict[str, Decimal]:
        return {c["cuenta_codigo"]: Decimal(str(c["saldo"])) for c in balance_json}

    return _saldos


@pytest_asyncio.fixture
async def actor(client) -> int:
    """Un tercero cualquiera creado por la API — devuelve su id."""
    r = await client.post(
        "/terceros", json={"nombre": "Banco Test", "nit_cedula": "1", "tipo": "banco"}
    )
    return r.json()["id"]
