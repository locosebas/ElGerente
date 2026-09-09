"""Integración — endpoints de servicio y resiliencia a fallos.

Ver docs/arquitectura/resiliencia-y-logs.md.
"""
from __future__ import annotations

import pytest

from app.contabilidad import router as contabilidad_router


async def test_salud_ok(client):
    r = await client.get("/salud")
    assert r.status_code == 200
    assert r.json() == {"estado": "ok", "base_de_datos": True}


async def test_error_inesperado_devuelve_500_generico(client, monkeypatch):
    """Un fallo no previsto en un servicio se traduce a un 500 con un mensaje
    genérico (sin filtrar detalles internos), no tumba el servidor."""

    async def _explota(*_args, **_kwargs):
        raise RuntimeError("fallo interno simulado")

    monkeypatch.setattr(contabilidad_router, "calcular_balance", _explota)

    r = await client.get("/balance")
    assert r.status_code == 500
    assert r.json() == {"detail": "Error interno del servidor. Revisá los logs."}
    assert "fallo interno simulado" not in r.text

    # El servidor sigue vivo: otra petición responde normal.
    r2 = await client.get("/cuentas")
    assert r2.status_code == 200


async def test_domain_error_se_registra_pero_responde_limpio(client, caplog):
    with caplog.at_level("INFO", logger="elgerente"):
        r = await client.get("/facturas/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Factura 9999 no existe"


@pytest.mark.parametrize("payload", [{}, {"nombre": "x"}, {"nombre": "x", "tipo": "raro"}])
async def test_validacion_devuelve_422_con_detalle(client, payload):
    r = await client.post("/terceros", json=payload)
    assert r.status_code == 422
    assert "detail" in r.json()
