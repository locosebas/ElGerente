"""Prueba manual rápida (no es la suite de tests final del proyecto):
1. Registra una factura recibida y su asiento balanceado (Gastos débito / Cuentas por pagar crédito).
2. Verifica que `cuadra()` da True.
3. Arma a propósito un asiento desbalanceado y verifica que `cuadra()` da False.
Se corre una sola vez para confirmar que el modelo funciona antes de construir la API encima.
"""
from datetime import date
from decimal import Decimal

from app.db import SessionLocal
from app.models import (
    Asiento,
    Cuenta,
    Factura,
    LineaAsiento,
    OrigenAsiento,
    Tercero,
    TipoFactura,
    TipoTercero,
)

session = SessionLocal()

proveedor = Tercero(nombre="Proveedor de Prueba SAS", nit_cedula="900123456", tipo=TipoTercero.PROVEEDOR)
session.add(proveedor)
session.flush()

gastos = session.query(Cuenta).filter_by(codigo="5195").one()
cxp = session.query(Cuenta).filter_by(codigo="2205").one()

asiento_balanceado = Asiento(
    fecha=date.today(),
    descripcion="Factura recibida de prueba",
    origen=OrigenAsiento.FACTURA,
    lineas=[
        LineaAsiento(cuenta=gastos, debito=Decimal("500000"), credito=Decimal("0")),
        LineaAsiento(cuenta=cxp, debito=Decimal("0"), credito=Decimal("500000")),
    ],
)
session.add(asiento_balanceado)
session.flush()

factura = Factura(
    tipo=TipoFactura.RECIBIDA,
    numero="F-001",
    fecha=date.today(),
    tercero=proveedor,
    subtotal=Decimal("500000"),
    iva=Decimal("0"),
    total=Decimal("500000"),
    asiento_id=asiento_balanceado.id,
)
session.add(factura)
session.commit()

assert asiento_balanceado.cuadra() is True
print("OK: asiento balanceado -> cuadra() == True")

asiento_mal = Asiento(
    fecha=date.today(),
    descripcion="Asiento deliberadamente desbalanceado (para probar la validación)",
    origen=OrigenAsiento.MANUAL,
    lineas=[
        LineaAsiento(cuenta=gastos, debito=Decimal("100000"), credito=Decimal("0")),
        LineaAsiento(cuenta=cxp, debito=Decimal("0"), credito=Decimal("999999")),
    ],
)
assert asiento_mal.cuadra() is False
print("OK: asiento desbalanceado -> cuadra() == False")

session.rollback()
session.close()
print("Smoke test completo: el modelo funciona como se diseñó.")
