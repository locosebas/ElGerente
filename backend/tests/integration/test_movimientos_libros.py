"""Integración — movimientos manuales y libros. Ver docs/features/movimientos/spec.md §7."""
from __future__ import annotations

from decimal import Decimal


def _mov(actor, **kw) -> dict:
    base = {
        "fecha": "2026-09-12",
        "descripcion": "prueba",
        "libro": "interna",
        "tercero_id": actor,
        "lineas": [
            {"cuenta_codigo": "2905", "debito": "50000", "credito": "0"},
            {"cuenta_codigo": "1105", "debito": "0", "credito": "50000"},
        ],
    }
    base.update(kw)
    return base


async def test_post_movimiento_oficial_sin_soporte_422(client, actor):
    r = await client.post(
        "/movimientos",
        json=_mov(
            actor,
            libro="oficial",
            documento_soporte=None,
            lineas=[
                {"cuenta_codigo": "5195", "debito": "10000", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "10000"},
            ],
        ),
    )
    assert r.status_code == 422


async def test_post_movimiento_sin_tercero_422(client):
    payload = _mov(1)
    del payload["tercero_id"]
    r = await client.post("/movimientos", json=payload)
    assert r.status_code == 422


async def test_post_movimiento_tercero_inexistente_404(client):
    r = await client.post("/movimientos", json=_mov(9999))
    assert r.status_code == 404


async def test_post_movimiento_interno_no_afecta_balance_oficial(client, actor, saldos):
    await client.post("/movimientos", json=_mov(actor, descripcion="Retiro del dueño"))
    oficial = saldos((await client.get("/balance")).json())
    total = saldos((await client.get("/balance", params={"libro": "todos"})).json())
    assert oficial["1105"] == Decimal("0.00")
    assert total["1105"] == Decimal("-50000.00")


async def test_post_movimiento_cuenta_inexistente_404(client, actor):
    r = await client.post(
        "/movimientos",
        json=_mov(
            actor,
            lineas=[
                {"cuenta_codigo": "9999", "debito": "1", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "1"},
            ],
        ),
    )
    assert r.status_code == 404


async def test_post_movimiento_lineas_no_cuadran_422(client, actor):
    r = await client.post(
        "/movimientos",
        json=_mov(
            actor,
            lineas=[
                {"cuenta_codigo": "5195", "debito": "100", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "90"},
            ],
        ),
    )
    assert r.status_code == 422


async def test_get_asientos_libro_interna(client, actor):
    await client.post("/movimientos", json=_mov(actor, descripcion="Retiro"))
    await client.post(
        "/movimientos",
        json=_mov(
            actor,
            libro="oficial",
            documento_soporte="Recibo #1",
            descripcion="Ajuste oficial",
            lineas=[
                {"cuenta_codigo": "5195", "debito": "1", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "1"},
            ],
        ),
    )
    internos = (await client.get("/asientos", params={"libro": "interna"})).json()
    assert len(internos) == 1
    assert internos[0]["tercero_id"] == actor
    assert internos[0]["tercero_nombre"] == "Banco Test"
