# Feature: facturas

**Módulo**: 1 — motor contable
**Código**: `backend/app/features/facturas/`
**Estado**: hecho y verificado (56 tests en verde)

## 1. Propósito

Registrar facturas **emitidas** (le vendemos a un cliente, a crédito) y **recibidas** (nos
compra un proveedor, a crédito), generando **automáticamente** el asiento contable
correspondiente. El usuario nunca captura débito/crédito para una factura.

El cobro/pago posterior es otra feature: [`pagos`](../pagos/spec.md).

## 2. Alcance

**Sí incluye en v1:**
- Registrar factura emitida o recibida con `numero`, `fecha`, `tercero`, `subtotal`, `iva`.
- Generar el asiento automático (libro oficial, soporte autocompletado).
- Listar facturas (filtros `tipo`, `estado`) y ver el detalle de una.

**No incluye:**
- Líneas de detalle (ítems/productos) de la factura — solo subtotal e IVA globales.
- Retenciones (retefuente, reteica).
- Notas crédito / anulación.
- Subir el archivo PDF (hoy solo se guarda un **enlace** — ver
  [`documentos/spec.md`](../documentos/spec.md)).
- Numeración automática: el `numero` lo provee quien registra.

## 3. Reglas de negocio

1. **`total` lo calcula el servidor:** `total = subtotal + iva`. Nunca se recibe del
   cliente; así una factura no puede quedar con el total inconsistente con sus partes.
2. **El tercero debe existir.** Si no → `NoEncontrado` (404).
3. **La factura nace en estado `pendiente`.**
4. **Genera un asiento automático, `origen = factura`, `libro = oficial`,** con
   `documento_soporte` autocompletado: `"Factura recibida <numero>"` o
   `"Factura emitida <numero>"`.
5. **Factura RECIBIDA** (compra a crédito):

   | Cuenta | Débito | Crédito |
   |---|---|---|
   | 5195 Gastos diversos | `subtotal` | |
   | 2408 Impuestos por pagar - IVA | `iva` | |
   | 2205 Cuentas por pagar | | `total` |

   El IVA va al **débito** de 2408 porque el IVA pagado en compras es descontable: reduce
   lo que se le debe a la DIAN por el IVA cobrado en ventas.

6. **Factura EMITIDA** (venta a crédito):

   | Cuenta | Débito | Crédito |
   |---|---|---|
   | 1305 Cuentas por cobrar | `total` | |
   | 4135 Ingresos por ventas | | `subtotal` |
   | 2408 Impuestos por pagar - IVA | | `iva` |

7. **`iva` puede ser 0** (factura sin IVA): la línea de 2408 se omite o va en 0 — el asiento
   igual debe cuadrar con las otras dos líneas.
8. La factura queda enlazada a su asiento (`factura.asiento_id`).

## 4. Modelo de datos

### `factura`

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | int, PK | |
| `tipo` | enum `TipoFactura` | `emitida` \| `recibida` |
| `numero` | str(50) | lo provee el usuario |
| `fecha` | date | |
| `tercero_id` | FK → `tercero.id` | debe existir |
| `subtotal` | Numeric(14,2) | ≥ 0 |
| `iva` | Numeric(14,2) | ≥ 0, default 0 |
| `total` | Numeric(14,2) | calculado por el servidor |
| `estado` | enum `EstadoFactura` | `pendiente` \| `pagada` \| `anulada`; nace `pendiente` |
| `asiento_id` | FK → `asiento.id`, nullable | se llena al contabilizar |
| `enlace_documento` | str(500), nullable | URL al PDF de la factura — ver [`documentos/spec.md`](../documentos/spec.md) |

## 5. Interfaz

| Método | Ruta | Cuerpo / query | Respuesta |
|---|---|---|---|
| `POST` | `/facturas` | `{ "tipo": "recibida", "numero": "F-001", "fecha": "2026-09-01", "tercero_id": 1, "subtotal": "500000", "iva": "95000" }` | `FacturaOut` (200) |
| `GET` | `/facturas` | `tipo`, `estado` opcionales | `FacturaOut[]` |
| `GET` | `/facturas/{id}` | — | `FacturaOut` (404 si no existe) |

`FacturaOut`: `id`, `tipo`, `numero`, `fecha`, `tercero_id`, `subtotal`, `iva`, `total`,
`estado`, `asiento_id`.

## 6. Errores

| Caso | Respuesta |
|---|---|
| `tercero_id` no existe | `404` |
| Falta un campo / tipo inválido | `422` (Pydantic) |
| El asiento generado no cuadra (no debería pasar — red de seguridad) | `500`, sin guardar nada |

## 7. Casos de prueba

| id del test | tipo | qué verifica | archivo |
|---|---|---|---|
| `test_total_se_calcula_en_servidor` | unit | `total = subtotal + iva`, ignora cualquier total enviado | `tests/unit/facturas/test_service.py` |
| `test_factura_recibida_genera_asiento_correcto` | unit | 3 líneas: débito 5195=subtotal, débito 2408=iva, crédito 2205=total | `tests/unit/facturas/test_service.py` |
| `test_factura_emitida_genera_asiento_correcto` | unit | débito 1305=total, crédito 4135=subtotal, crédito 2408=iva | `tests/unit/facturas/test_service.py` |
| `test_factura_sin_iva_cuadra` | unit | `iva=0` → asiento de 2 líneas que cuadra | `tests/unit/facturas/test_service.py` |
| `test_factura_tercero_inexistente` | unit | `tercero_id` inexistente → `NoEncontrado` | `tests/unit/facturas/test_service.py` |
| `test_factura_nace_pendiente_y_enlaza_asiento` | unit | `estado=pendiente`, `asiento_id` no nulo | `tests/unit/facturas/test_service.py` |
| `test_post_factura_recibida_end_to_end` | integración | `POST /facturas` → 200; `GET /balance` refleja 5195, 2205, 2408 | `tests/integration/test_facturas.py` |
| `test_post_factura_emitida_end_to_end` | integración | `POST /facturas` emitida → 200; balance refleja 1305, 4135, 2408 | `tests/integration/test_facturas.py` |
| `test_post_factura_tercero_inexistente_404` | integración | `tercero_id=9999` → 404 | `tests/integration/test_facturas.py` |
| `test_get_facturas_filtra` | integración | `GET /facturas?estado=pendiente` no trae pagadas | `tests/integration/test_facturas.py` |

## 8. Notas / decisiones abiertas

- **Sin ítems de detalle:** la factura electrónica DIAN exige líneas de producto. En v1 se
  registra solo el resumen (subtotal/IVA). Cuando el proyecto se acerque a facturación
  electrónica se agrega `factura_item` — es aditivo, no rompe lo existente.
- **Retenciones:** frecuentes en Colombia; hoy no se modelan. Se agregarían como líneas
  extra en las tablas de asiento de las reglas 5 y 6.
