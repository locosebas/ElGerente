"""Integración — facturas y pagos. Ver specs §7."""
from __future__ import annotations

from decimal import Decimal


async def _tercero(client, tipo: str) -> int:
    r = await client.post(
        "/terceros", json={"nombre": "X", "nit_cedula": "1", "tipo": tipo}
    )
    return r.json()["id"]


async def _factura(client, tipo: str, tercero_id: int, numero="N1") -> dict:
    r = await client.post(
        "/facturas",
        json={
            "tipo": tipo,
            "numero": numero,
            "fecha": "2026-09-01",
            "tercero_id": tercero_id,
            "subtotal": "1000000",
            "iva": "190000",
        },
    )
    return r.json()


async def test_post_factura_recibida_end_to_end(client, saldos):
    prov = await _tercero(client, "proveedor")
    f = await _factura(client, "recibida", prov)
    assert f["total"] in ("1190000.00", "1190000", 1190000.0)
    b = saldos((await client.get("/balance")).json())
    assert b["5195"] == Decimal("1000000.00")
    assert b["2205"] == Decimal("1190000.00")
    assert b["2408"] == Decimal("-190000.00")


async def test_post_factura_emitida_end_to_end(client, saldos):
    cli = await _tercero(client, "cliente")
    await _factura(client, "emitida", cli)
    b = saldos((await client.get("/balance")).json())
    assert b["1305"] == Decimal("1190000.00")
    assert b["4135"] == Decimal("1000000.00")
    assert b["2408"] == Decimal("190000.00")


async def test_post_factura_tercero_inexistente_404(client):
    r = await client.post(
        "/facturas",
        json={
            "tipo": "recibida",
            "numero": "F",
            "fecha": "2026-09-01",
            "tercero_id": 9999,
            "subtotal": "1000",
            "iva": "0",
        },
    )
    assert r.status_code == 404


async def test_get_facturas_filtra(client):
    prov = await _tercero(client, "proveedor")
    f1 = await _factura(client, "recibida", prov, numero="A")
    await _factura(client, "recibida", prov, numero="B")
    await client.post(
        f"/facturas/{f1['id']}/pagar", json={"medio_pago": "caja", "fecha": "2026-09-02"}
    )
    pendientes = (await client.get("/facturas", params={"estado": "pendiente"})).json()
    assert [f["numero"] for f in pendientes] == ["B"]


async def test_pagar_end_to_end(client, saldos):
    prov = await _tercero(client, "proveedor")
    f = await _factura(client, "recibida", prov)
    r = await client.post(
        f"/facturas/{f['id']}/pagar", json={"medio_pago": "bancos", "fecha": "2026-09-05"}
    )
    assert r.status_code == 200
    assert r.json()["estado"] == "pagada"
    b = saldos((await client.get("/balance")).json())
    assert b["2205"] == Decimal("0.00")
    assert b["1110"] == Decimal("-1190000.00")


async def test_pagar_dos_veces_409(client):
    prov = await _tercero(client, "proveedor")
    f = await _factura(client, "recibida", prov)
    await client.post(
        f"/facturas/{f['id']}/pagar", json={"medio_pago": "caja", "fecha": "2026-09-05"}
    )
    r = await client.post(
        f"/facturas/{f['id']}/pagar", json={"medio_pago": "caja", "fecha": "2026-09-05"}
    )
    assert r.status_code == 409


async def test_cobrar_emitida_end_to_end(client, saldos):
    cli = await _tercero(client, "cliente")
    f = await _factura(client, "emitida", cli)
    await client.post(
        f"/facturas/{f['id']}/pagar", json={"medio_pago": "bancos", "fecha": "2026-09-10"}
    )
    b = saldos((await client.get("/balance")).json())
    assert b["1110"] == Decimal("1190000.00")
    assert b["1305"] == Decimal("0.00")
