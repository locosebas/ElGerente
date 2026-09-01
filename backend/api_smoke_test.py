"""Prueba manual de extremo a extremo de la API del Módulo 1.

Usa el TestClient de FastAPI (no necesita un servidor corriendo aparte).
Borra la base de datos local antes de correr para partir de un estado limpio.
"""
import os

if os.path.exists("elgerente.db"):
    os.remove("elgerente.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.seed import seed  # noqa: E402

seed()

client = TestClient(app)


def esperar(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise AssertionError(mensaje)
    print(f"OK: {mensaje}")


# --- Terceros ---
r = client.post(
    "/terceros",
    json={"nombre": "Proveedor Test SAS", "nit_cedula": "900111222", "tipo": "proveedor"},
)
esperar(r.status_code == 200, "crear tercero proveedor -> 200")
proveedor_id = r.json()["id"]

r = client.post(
    "/terceros", json={"nombre": "Cliente Test", "nit_cedula": "1010101010", "tipo": "cliente"}
)
esperar(r.status_code == 200, "crear tercero cliente -> 200")
cliente_id = r.json()["id"]

# --- Factura recibida ---
r = client.post(
    "/facturas",
    json={
        "tipo": "recibida",
        "numero": "F-REC-001",
        "fecha": "2026-09-01",
        "tercero_id": proveedor_id,
        "subtotal": "500000",
        "iva": "95000",
    },
)
esperar(r.status_code == 200, "registrar factura recibida -> 200")
factura_recibida = r.json()
esperar(factura_recibida["total"] == "595000.00", f"total calculado correcto: {factura_recibida['total']}")
esperar(factura_recibida["estado"] == "pendiente", "factura recibida queda pendiente")

r = client.get("/balance")
balance = {c["cuenta_codigo"]: c["saldo"] for c in r.json()}
esperar(balance["5195"] == "500000.00", f"Gastos refleja subtotal: {balance['5195']}")
esperar(balance["2205"] == "595000.00", f"Cuentas por pagar refleja total: {balance['2205']}")
esperar(balance["2408"] == "-95000.00", f"IVA neto por pagar refleja el descontable: {balance['2408']}")

# --- Pagar la factura recibida desde Bancos ---
r = client.post(
    f"/facturas/{factura_recibida['id']}/pagar",
    json={"medio_pago": "bancos", "fecha": "2026-09-05"},
)
esperar(r.status_code == 200, "pagar factura recibida -> 200")
esperar(r.json()["estado"] == "pagada", "factura recibida queda pagada")

r = client.post(
    f"/facturas/{factura_recibida['id']}/pagar",
    json={"medio_pago": "bancos", "fecha": "2026-09-05"},
)
esperar(r.status_code == 409, "pagar de nuevo una factura ya pagada -> 409")

r = client.get("/balance")
balance = {c["cuenta_codigo"]: c["saldo"] for c in r.json()}
esperar(balance["2205"] == "0.00", "Cuentas por pagar vuelve a cero tras el pago")
esperar(balance["1110"] == "-595000.00", f"Bancos refleja la salida de dinero: {balance['1110']}")

# --- Factura emitida + cobro (esto es lo que antes se llamaba "consignación") ---
r = client.post(
    "/facturas",
    json={
        "tipo": "emitida",
        "numero": "F-EMI-001",
        "fecha": "2026-09-02",
        "tercero_id": cliente_id,
        "subtotal": "1000000",
        "iva": "190000",
    },
)
esperar(r.status_code == 200, "registrar factura emitida -> 200")
factura_emitida = r.json()

r = client.post(
    f"/facturas/{factura_emitida['id']}/pagar",
    json={"medio_pago": "bancos", "fecha": "2026-09-10"},
)
esperar(r.status_code == 200, "cobrar factura emitida -> 200")

r = client.get("/balance")
balance = {c["cuenta_codigo"]: c["saldo"] for c in r.json()}
esperar(
    balance["1110"] == "595000.00",
    f"Bancos neto (pago -595.000 + cobro +1.190.000) = 595.000: {balance['1110']}",
)
esperar(balance["1305"] == "0.00", "Cuentas por cobrar vuelve a cero tras el cobro")

# --- Tercero inexistente ---
r = client.post(
    "/facturas",
    json={
        "tipo": "recibida",
        "numero": "F-X",
        "fecha": "2026-09-01",
        "tercero_id": 9999,
        "subtotal": "1000",
        "iva": "0",
    },
)
esperar(r.status_code == 404, "factura con tercero inexistente -> 404")

# --- Contrato ---
r = client.post(
    "/contratos",
    json={
        "tercero_id": proveedor_id,
        "objeto": "Arrendamiento de bodega",
        "valor": "2000000",
        "fecha_inicio": "2026-09-01",
        "fecha_fin": "2027-09-01",
    },
)
esperar(r.status_code == 200, "registrar contrato -> 200")

# --- Movimiento manual oficial SIN documento_soporte -> rechazado ---
r = client.post(
    "/movimientos",
    json={
        "fecha": "2026-09-11",
        "descripcion": "Ajuste oficial sin soporte (debe fallar)",
        "libro": "oficial",
        "documento_soporte": None,
        "lineas": [
            {"cuenta_codigo": "5195", "debito": "10000", "credito": "0"},
            {"cuenta_codigo": "1105", "debito": "0", "credito": "10000"},
        ],
    },
)
esperar(r.status_code == 422, "movimiento oficial sin documento_soporte -> 422")

# --- Movimiento manual oficial CON documento_soporte -> aceptado ---
r = client.post(
    "/movimientos",
    json={
        "fecha": "2026-09-11",
        "descripcion": "Ajuste oficial de caja menor",
        "libro": "oficial",
        "documento_soporte": "Recibo caja menor #045",
        "lineas": [
            {"cuenta_codigo": "5195", "debito": "10000", "credito": "0"},
            {"cuenta_codigo": "1105", "debito": "0", "credito": "10000"},
        ],
    },
)
esperar(r.status_code == 200, "movimiento oficial con documento_soporte -> 200")

# --- Movimiento manual INTERNO (para-contabilidad) sin soporte -> aceptado ---
r = client.post(
    "/movimientos",
    json={
        "fecha": "2026-09-12",
        "descripcion": "El dueño retira efectivo para gasto personal",
        "libro": "interna",
        "documento_soporte": None,
        "lineas": [
            {"cuenta_codigo": "2905", "debito": "50000", "credito": "0"},
            {"cuenta_codigo": "1105", "debito": "0", "credito": "50000"},
        ],
    },
)
esperar(r.status_code == 200, "movimiento interno sin soporte -> 200")

# --- El balance oficial NO debe verse afectado por el movimiento interno ---
r = client.get("/balance")
balance_oficial = {c["cuenta_codigo"]: c["saldo"] for c in r.json()}
esperar(
    balance_oficial["1105"] == "-10000.00",
    f"Caja oficial solo refleja el ajuste oficial (-10.000), no el retiro interno: {balance_oficial['1105']}",
)
from decimal import Decimal  # noqa: E402

esperar(
    "2905" not in balance_oficial or Decimal(balance_oficial["2905"]) == 0,
    "Cuentas con el dueño no se mueve en el balance oficial",
)

# --- El balance CON incluir_interna=true sí debe reflejar ambos ---
r = client.get("/balance", params={"incluir_interna": "true"})
balance_total = {c["cuenta_codigo"]: c["saldo"] for c in r.json()}
esperar(
    balance_total["1105"] == "-60000.00",
    f"Caja total = oficial (-10.000) + interno (-50.000) = -60.000: {balance_total['1105']}",
)
esperar(
    balance_total["2905"] == "-50000.00",
    "Cuentas con el dueño queda en -50.000: el dueño le debe eso a la "
    f"empresa (saldo negativo en un pasivo = lo contrario de deberle a él): {balance_total['2905']}",
)

# --- Filtro de /asientos por libro ---
r = client.get("/asientos", params={"libro": "interna"})
asientos_internos = r.json()
esperar(len(asientos_internos) == 1, "filtro /asientos?libro=interna trae solo el asiento interno")

# --- Asientos: verificar que TODOS (incluidos los manuales) cuadran ---
r = client.get("/asientos")
asientos = r.json()
for a in asientos:
    total_debito = sum(float(l["debito"]) for l in a["lineas"])
    total_credito = sum(float(l["credito"]) for l in a["lineas"])
    esperar(
        abs(total_debito - total_credito) < 0.001,
        f"asiento {a['id']} [{a['libro']}] ({a['descripcion']}) cuadra: debito={total_debito} credito={total_credito}",
    )

print(f"\nTotal de asientos generados: {len(asientos)}")
print("Smoke test de la API completo: todo funciona como se diseñó.")
