"""Integración — enlaces a documentos. Ver docs/features/documentos/spec.md §7."""
from __future__ import annotations

URL = "https://drive.google.com/file/d/abc/view"


async def _tercero(client, tipo="proveedor", **extra) -> dict:
    r = await client.post(
        "/terceros", json={"nombre": "X", "nit_cedula": "1", "tipo": tipo, **extra}
    )
    return r.json()


async def _factura(client, tercero_id: int, **extra) -> dict:
    r = await client.post(
        "/facturas",
        json={
            "tipo": "recibida",
            "numero": "F1",
            "fecha": "2026-09-01",
            "tercero_id": tercero_id,
            "subtotal": "1000",
            "iva": "0",
            **extra,
        },
    )
    return r.json()


async def test_crear_tercero_con_enlace_rut(client):
    creado = await _tercero(client, enlace_rut=URL)
    assert creado["enlace_rut"] == URL
    lista = (await client.get("/terceros")).json()
    assert next(t for t in lista if t["id"] == creado["id"])["enlace_rut"] == URL


async def test_patch_factura_enlace(client):
    t = await _tercero(client)
    f = await _factura(client, t["id"])
    assert f["enlace_documento"] is None

    r = await client.patch(f"/facturas/{f['id']}", json={"enlace_documento": URL})
    assert r.status_code == 200
    assert r.json()["enlace_documento"] == URL

    assert (await client.get(f"/facturas/{f['id']}")).json()["enlace_documento"] == URL


async def test_patch_contrato_quitar_enlace(client):
    t = await _tercero(client)
    r = await client.post(
        "/contratos",
        json={
            "tercero_id": t["id"],
            "objeto": "x",
            "valor": "1",
            "fecha_inicio": "2026-09-01",
            "enlace_documento": URL,
        },
    )
    contrato_id = r.json()["id"]
    assert r.json()["enlace_documento"] == URL

    r = await client.patch(f"/contratos/{contrato_id}", json={"enlace_documento": None})
    assert r.status_code == 200
    assert r.json()["enlace_documento"] is None


async def test_post_factura_enlace_invalido_422(client):
    t = await _tercero(client)
    f = await client.post(
        "/facturas",
        json={
            "tipo": "recibida",
            "numero": "F2",
            "fecha": "2026-09-01",
            "tercero_id": t["id"],
            "subtotal": "1000",
            "iva": "0",
            "enlace_documento": "drive.google.com/sin-esquema",
        },
    )
    assert f.status_code == 422


async def test_patch_tercero_inexistente_404(client):
    r = await client.patch("/terceros/9999", json={"enlace_rut": URL})
    assert r.status_code == 404
