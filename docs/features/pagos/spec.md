# Feature: pagos

**Módulo**: 1 — motor contable
**Código**: `backend/app/features/pagos/`
**Estado**: hecho y verificado (56 tests en verde)

## 1. Propósito

Registrar el **pago** de una factura recibida (le pagamos al proveedor) o el **cobro** de
una factura emitida (el cliente nos paga / consigna), generando automáticamente el asiento
y pasando la factura a estado `pagada`.

> Contablemente, "registrar una consignación que nos hace un cliente" es exactamente el
> cobro de una factura emitida: dinero que entra a Caja o Bancos.

## 2. Alcance

**Sí incluye en v1:**
- Pagar/cobrar una factura completa, en un solo movimiento, eligiendo medio de pago
  (`caja` o `bancos`).
- Generar el asiento automático y marcar la factura `pagada`.

**No incluye:**
- Pagos parciales (abonos). En v1 el pago salda la factura entera.
- Otros medios de pago (tarjeta, cheque) — solo `caja` y `bancos`.
- Anular un pago ya registrado.

## 3. Reglas de negocio

1. **La factura debe existir** → si no, `NoEncontrado` (404).
2. **La factura debe estar `pendiente`.** Si ya está `pagada` o `anulada` → `Conflicto`
   (409). No se paga dos veces.
3. **`medio_pago` es `caja` o `bancos`.** Otro valor → `DatosInvalidos` (422).
   `caja` → cuenta 1105; `bancos` → cuenta 1110.
4. **Genera un asiento automático**, `origen = factura`, `libro = oficial`,
   `documento_soporte` = `"Pago factura recibida <numero>"` o
   `"Cobro factura emitida <numero>"`.
5. **Pago de factura RECIBIDA:**

   | Cuenta | Débito | Crédito |
   |---|---|---|
   | 2205 Cuentas por pagar | `total` | |
   | 1105 Caja **o** 1110 Bancos | | `total` |

6. **Cobro de factura EMITIDA:**

   | Cuenta | Débito | Crédito |
   |---|---|---|
   | 1105 Caja **o** 1110 Bancos | `total` | |
   | 1305 Cuentas por cobrar | | `total` |

7. **Efecto:** `factura.estado` pasa a `pagada`.

## 4. Modelo de datos

No crea tablas. Modifica `factura.estado` y crea un `asiento` (+ sus líneas). No se guarda
una entidad "pago" separada en v1 — el asiento con su descripción y fecha es el registro
del pago. (Ver §8.)

## 5. Interfaz

| Método | Ruta | Cuerpo | Respuesta |
|---|---|---|---|
| `POST` | `/facturas/{id}/pagar` | `{ "medio_pago": "bancos", "fecha": "2026-09-05" }` | `FacturaOut` con `estado: "pagada"` (200) |

Sirve tanto para pagar (recibida) como para cobrar (emitida): el sistema sabe cuál es por
`factura.tipo`.

## 6. Errores

| Caso | Respuesta |
|---|---|
| Factura no existe | `404` |
| Factura ya `pagada` o `anulada` | `409` |
| `medio_pago` distinto de `caja`/`bancos` | `422` |
| El asiento generado no cuadra (red de seguridad) | `500`, sin guardar nada |

## 7. Casos de prueba

| id del test | tipo | qué verifica | archivo |
|---|---|---|---|
| `test_pago_recibida_genera_asiento` | unit | débito 2205=total, crédito 1110=total; factura → `pagada` | `tests/unit/pagos/test_service.py` |
| `test_cobro_emitida_genera_asiento` | unit | débito 1105/1110=total, crédito 1305=total | `tests/unit/pagos/test_service.py` |
| `test_pagar_factura_inexistente` | unit | `NoEncontrado` | `tests/unit/pagos/test_service.py` |
| `test_pagar_factura_ya_pagada` | unit | `Conflicto` | `tests/unit/pagos/test_service.py` |
| `test_medio_pago_invalido` | unit | `DatosInvalidos` | `tests/unit/pagos/test_service.py` |
| `test_pagar_end_to_end` | integración | registrar factura recibida → pagar → `GET /balance`: 2205 vuelve a 0, Bancos baja `total` | `tests/integration/test_facturas.py` |
| `test_pagar_dos_veces_409` | integración | segundo `POST /facturas/{id}/pagar` → 409 | `tests/integration/test_facturas.py` |
| `test_cobrar_emitida_end_to_end` | integración | registrar emitida → cobrar → Bancos sube, 1305 vuelve a 0 | `tests/integration/test_facturas.py` |

## 8. Notas / decisiones abiertas

- **¿Entidad `pago` separada?** Hoy no existe: el asiento es el registro. Si se necesitan
  pagos parciales, conciliación bancaria o anulación de pagos, conviene crear una tabla
  `pago` (factura_id, monto, fecha, medio, asiento_id). Es aditivo.
- **Pagos parciales:** la decisión de no soportarlos en v1 simplifica mucho el flujo de
  WhatsApp. Se revisará según el uso real.
