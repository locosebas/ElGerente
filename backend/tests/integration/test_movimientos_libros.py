"""Integración — movimientos manuales y libros. Ver docs/features/movimientos/spec.md §7."""
from __future__ import annotations

from decimal import Decimal


async def test_post_movimiento_oficial_sin_soporte_422(client):
    r = await client.post(
        "/movimientos",
        json={
            "fecha": "2026-09-11",
            "descripcion": "Ajuste oficial sin soporte",
            "libro": "oficial",
            "documento_soporte": None,
            "lineas": [
                {"cuenta_codigo": "5195", "debito": "10000", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "10000"},
            ],
        },
    )
    assert r.status_code == 422


async def test_post_movimiento_interno_no_afecta_balance_oficial(client, saldos):
    await client.post(
        "/movimientos",
        json={
            "fecha": "2026-09-12",
            "descripcion": "Retiro del dueño",
            "libro": "interna",
            "lineas": [
                {"cuenta_codigo": "2905", "debito": "50000", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "50000"},
            ],
        },
    )
    oficial = saldos((await client.get("/balance")).json())
    total = saldos((await client.get("/balance", params={"libro": "todos"})).json())
    assert oficial["1105"] == Decimal("0.00")
    assert total["1105"] == Decimal("-50000.00")


async def test_post_movimiento_cuenta_inexistente_404(client):
    r = await client.post(
        "/movimientos",
        json={
            "fecha": "2026-09-12",
            "descripcion": "cuenta mala",
            "libro": "interna",
            "lineas": [
                {"cuenta_codigo": "9999", "debito": "1", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "1"},
            ],
        },
    )
    assert r.status_code == 404


async def test_post_movimiento_lineas_no_cuadran_422(client):
    r = await client.post(
        "/movimientos",
        json={
            "fecha": "2026-09-12",
            "descripcion": "descuadrado",
            "libro": "interna",
            "lineas": [
                {"cuenta_codigo": "5195", "debito": "100", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "90"},
            ],
        },
    )
    assert r.status_code == 422


async def test_get_asientos_libro_interna(client):
    await client.post(
        "/movimientos",
        json={
            "fecha": "2026-09-12",
            "descripcion": "Retiro",
            "libro": "interna",
            "lineas": [
                {"cuenta_codigo": "2905", "debito": "1", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "1"},
            ],
        },
    )
    await client.post(
        "/movimientos",
        json={
            "fecha": "2026-09-12",
            "descripcion": "Ajuste oficial",
            "libro": "oficial",
            "documento_soporte": "Recibo #1",
            "lineas": [
                {"cuenta_codigo": "5195", "debito": "1", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "1"},
            ],
        },
    )
    internos = (await client.get("/asientos", params={"libro": "interna"})).json()
    assert len(internos) == 1
