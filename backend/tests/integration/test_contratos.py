"""Integración — contratos. Ver docs/features/contratos/spec.md §7."""
from __future__ import annotations


async def _proveedor(client) -> int:
    r = await client.post(
        "/terceros", json={"nombre": "Arrendador", "nit_cedula": "1", "tipo": "proveedor"}
    )
    return r.json()["id"]


async def test_post_contrato_end_to_end(client):
    prov = await _proveedor(client)
    r = await client.post(
        "/contratos",
        json={
            "tercero_id": prov,
            "objeto": "Arriendo bodega",
            "valor": "2000000",
            "fecha_inicio": "2026-09-01",
            "fecha_fin": "2027-09-01",
        },
    )
    assert r.status_code == 200
    creado = r.json()

    lista = (await client.get("/contratos")).json()
    assert creado["id"] in [c["id"] for c in lista]
    assert creado["estado"] == "vigente"

    # Un contrato no toca la contabilidad.
    assert (await client.get("/asientos")).json() == []


async def test_post_contrato_tercero_inexistente_404(client):
    r = await client.post(
        "/contratos",
        json={
            "tercero_id": 9999,
            "objeto": "x",
            "valor": "1",
            "fecha_inicio": "2026-09-01",
        },
    )
    assert r.status_code == 404
