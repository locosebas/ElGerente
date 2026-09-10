"""Integración — núcleo contable / balance. Ver specs §7."""
from __future__ import annotations

from decimal import Decimal


async def _proveedor(client) -> int:
    r = await client.post(
        "/terceros", json={"nombre": "Prov", "nit_cedula": "1", "tipo": "proveedor"}
    )
    return r.json()["id"]


async def test_get_cuentas_devuelve_plan_completo(client):
    r = await client.get("/cuentas")
    assert r.status_code == 200
    cuentas = r.json()
    assert [c["codigo"] for c in cuentas] == [
        "1105", "1110", "1305", "2105", "2205", "2408", "2905", "3115", "4135", "5195", "5905"
    ]


async def test_get_balance_refleja_factura_y_pago(client, saldos):
    prov = await _proveedor(client)
    r = await client.post(
        "/facturas",
        json={
            "tipo": "recibida",
            "numero": "F1",
            "fecha": "2026-09-01",
            "tercero_id": prov,
            "subtotal": "500000",
            "iva": "95000",
        },
    )
    assert r.status_code == 200
    factura_id = r.json()["id"]

    b = saldos((await client.get("/balance")).json())
    assert b["5195"] == Decimal("500000.00")
    assert b["2205"] == Decimal("595000.00")
    assert b["2408"] == Decimal("-95000.00")

    r = await client.post(
        f"/facturas/{factura_id}/pagar",
        json={"medio_pago": "bancos", "fecha": "2026-09-05"},
    )
    assert r.status_code == 200

    b = saldos((await client.get("/balance")).json())
    assert b["2205"] == Decimal("0.00")
    assert b["1110"] == Decimal("-595000.00")


async def test_get_asientos_filtra_por_libro(client, actor):
    r = await client.post(
        "/movimientos",
        json={
            "fecha": "2026-09-10",
            "descripcion": "Retiro del dueño",
            "libro": "interna",
            "tercero_id": actor,
            "documento_soporte": None,
            "lineas": [
                {"cuenta_codigo": "2905", "debito": "50000", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "50000"},
            ],
        },
    )
    assert r.status_code == 200

    internos = (await client.get("/asientos", params={"libro": "interna"})).json()
    assert len(internos) == 1
    assert internos[0]["libro"] == "interna"

    oficiales = (await client.get("/asientos", params={"libro": "oficial"})).json()
    assert oficiales == []


async def test_get_balance_libro_y_periodo(client, saldos, actor):
    await client.post(
        "/movimientos",
        json={
            "fecha": "2026-09-12",
            "descripcion": "Retiro",
            "libro": "interna",
            "tercero_id": actor,
            "lineas": [
                {"cuenta_codigo": "2905", "debito": "50000", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "50000"},
            ],
        },
    )
    oficial = saldos((await client.get("/balance")).json())
    interno = saldos((await client.get("/balance", params={"libro": "interna"})).json())
    total = saldos((await client.get("/balance", params={"libro": "todos"})).json())
    assert oficial["1105"] == Decimal("0.00")
    assert interno["1105"] == Decimal("-50000.00")
    assert total["1105"] == Decimal("-50000.00")

    # el movimiento es de septiembre: un periodo de agosto lo deja fuera
    agosto = saldos(
        (
            await client.get(
                "/balance",
                params={"libro": "todos", "desde": "2026-08-01", "hasta": "2026-08-31"},
            )
        ).json()
    )
    assert agosto["1105"] == Decimal("0.00")

    r = await client.get("/balance", params={"desde": "2026-09-30", "hasta": "2026-09-01"})
    assert r.status_code == 422


async def test_get_cuenta_movimientos_end_to_end(client):
    prov = await _proveedor(client)
    for numero, sub in [("F1", "100000"), ("F2", "200000")]:
        await client.post(
            "/facturas",
            json={
                "tipo": "recibida",
                "numero": numero,
                "fecha": "2026-09-01",
                "tercero_id": prov,
                "subtotal": sub,
                "iva": "0",
            },
        )
    r = await client.get("/cuentas/2205/movimientos")
    assert r.status_code == 200
    d = r.json()
    assert d["cuenta_codigo"] == "2205"
    assert [m["credito"] for m in d["movimientos"]] == ["100000.00", "200000.00"]
    assert [m["saldo_acumulado"] for m in d["movimientos"]] == ["100000.00", "300000.00"]
    assert d["saldo_final"] == "300000.00"


async def test_get_cuenta_movimientos_404(client):
    r = await client.get("/cuentas/9999/movimientos")
    assert r.status_code == 404


async def test_balance_y_extracto_filtran_por_tercero(client, saldos):
    # Dos proveedores, una factura recibida cada uno.
    ids = []
    for i, sub in enumerate(["100000", "300000"]):
        r = await client.post(
            "/terceros",
            json={"nombre": f"Prov {i}", "nit_cedula": str(i), "tipo": "proveedor"},
        )
        ids.append(r.json()["id"])
        await client.post(
            "/facturas",
            json={
                "tipo": "recibida",
                "numero": f"F{i}",
                "fecha": "2026-09-01",
                "tercero_id": r.json()["id"],
                "subtotal": sub,
                "iva": "0",
            },
        )

    todos = saldos((await client.get("/balance")).json())
    solo_p0 = saldos(
        (await client.get("/balance", params={"tercero_id": ids[0]})).json()
    )
    assert todos["2205"] == Decimal("400000.00")
    assert solo_p0["2205"] == Decimal("100000.00")

    d = (
        await client.get(
            "/cuentas/2205/movimientos", params={"tercero_id": ids[1]}
        )
    ).json()
    assert d["saldo_final"] == "300000.00"
    assert all(m["tercero_id"] == ids[1] for m in d["movimientos"])
    assert d["movimientos"][0]["tercero_nombre"] == "Prov 1"


async def test_invariante_todos_los_asientos_cuadran(client):
    # Genera varios asientos de distinta procedencia.
    prov = await _proveedor(client)
    r = await client.post(
        "/facturas",
        json={
            "tipo": "recibida",
            "numero": "F9",
            "fecha": "2026-09-01",
            "tercero_id": prov,
            "subtotal": "100000",
            "iva": "19000",
        },
    )
    await client.post(
        f"/facturas/{r.json()['id']}/pagar",
        json={"medio_pago": "caja", "fecha": "2026-09-02"},
    )
    await client.post(
        "/movimientos",
        json={
            "fecha": "2026-09-03",
            "descripcion": "Ajuste",
            "libro": "oficial",
            "tercero_id": prov,
            "documento_soporte": "Recibo #1",
            "lineas": [
                {"cuenta_codigo": "5195", "debito": "1000", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "1000"},
            ],
        },
    )

    asientos = (await client.get("/asientos")).json()
    assert len(asientos) >= 3
    for a in asientos:
        td = sum(Decimal(str(ln["debito"])) for ln in a["lineas"])
        tc = sum(Decimal(str(ln["credito"])) for ln in a["lineas"])
        assert td == tc, f"asiento {a['id']} no cuadra: {td} != {tc}"
