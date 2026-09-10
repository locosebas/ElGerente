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
        "/terceros", json={"nombre": "X", "nit_cedula": "1", "tipo": "marciano"}
    )
    assert r.status_code == 422


async def test_post_terceros_tipos_nuevos(client):
    for tipo in ["banco", "empleado", "socio", "otro"]:
        r = await client.post(
            "/terceros", json={"nombre": tipo.title(), "nit_cedula": "1", "tipo": tipo}
        )
        assert r.status_code == 200, tipo
        assert r.json()["tipo"] == tipo
