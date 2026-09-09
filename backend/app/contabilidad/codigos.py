"""Códigos de cuenta usados por las reglas automáticas de asientos.

Centralizados aquí para que facturas, pagos y movimientos referencien el
mismo sitio. Deben existir en el plan de cuentas (plan_cuentas.py).
"""
CAJA = "1105"
BANCOS = "1110"
CUENTAS_POR_COBRAR = "1305"
CUENTAS_POR_PAGAR = "2205"
IVA = "2408"
INGRESOS_VENTAS = "4135"
GASTOS_DIVERSOS = "5195"

# medio de pago (string que llega por la API) -> código de cuenta
MEDIOS_PAGO = {"caja": CAJA, "bancos": BANCOS}
