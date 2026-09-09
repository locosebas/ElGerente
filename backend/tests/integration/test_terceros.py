"""Integración — terceros. Ver docs/features/terceros/spec.md §7."""
from __future__ import annotations


async def test_post_terceros_ok(client):
    r = await client.post(
        "/terceros",
        json={"nombre": "Proveedor Test", "nit_cedula": "900111", "tipo": "proveedor"},
    )
    assert r.status_code == 200
    creado = r.json()

    r = await client.get("/terceros")
    assert r.status_code == 200
    assert creado["id"] in [t["id"] for t in r.json()]


async def test_post_terceros_tipo_invalido(client):
    r = await client.post(
        "/terceros", json={"nombre": "X", "nit_cedula": "1", "tipo": "otro"}
    )
    assert r.status_code == 422
