# Diseño de API — Módulo 1 (Motor Contable Básico)

**Fecha**: 2026-09-01  
**Estado**: Diseño detallado — implementar tal cual está documentado aquí

## 1. Principio de capas

```
Router (FastAPI)  →  Service (lógica de negocio)  →  Modelos (SQLAlchemy)
```

El router solo recibe la petición HTTP, valida el formato (vía Pydantic) y llama al service. **Toda regla de negocio vive en `app/services.py`**, nunca en el router. Esto retoma una regla ya escrita en el análisis archivado (`analysis/_archive/2026-04-10-v1-plataforma-multitenant/microservices-migration-plan.md`): mantener la lógica separada del transporte HTTP hace que el código sea más fácil de auditar leyendo un solo archivo, y más fácil de mover a otro contexto (WhatsApp en el Módulo 2 llamará a los mismos services, no a los routers).

## 2. Reglas de negocio: generación automática de asientos

Esta es la parte más importante de auditar: **el usuario nunca captura débito/crédito a mano** para facturas — el sistema los deriva siempre de la misma forma, documentada aquí.

### Factura RECIBIDA (compramos algo, a crédito)

| Cuenta | Débito | Crédito |
|---|---|---|
| 5195 Gastos diversos | `subtotal` | |
| 2408 Impuestos por pagar - IVA | `iva` | |
| 2205 Cuentas por pagar | | `total` |

Razón del débito a 2408: el IVA que pagamos en una compra es descontable — reduce lo que le debemos a la DIAN por el IVA que cobramos en ventas.

### Factura EMITIDA (vendemos algo, a crédito)

| Cuenta | Débito | Crédito |
|---|---|---|
| 1305 Cuentas por cobrar | `total` | |
| 4135 Ingresos por ventas | | `subtotal` |
| 2408 Impuestos por pagar - IVA | | `iva` |

### Pago de una factura RECIBIDA (nosotros pagamos al proveedor)

| Cuenta | Débito | Crédito |
|---|---|---|
| 2205 Cuentas por pagar | `total` | |
| 1105 Caja **o** 1110 Bancos (según medio de pago elegido) | | `total` |

Efecto: `factura.estado` pasa a `pagada`.

### Cobro de una factura EMITIDA (el cliente nos paga / consigna)

| Cuenta | Débito | Crédito |
|---|---|---|
| 1105 Caja **o** 1110 Bancos (según medio de pago elegido) | `total` | |
| 1305 Cuentas por cobrar | | `total` |

Efecto: `factura.estado` pasa a `pagada`. Esta es la operación que cubre lo que en la idea original se llamaba "registrar una consignación" — una consignación es, contablemente, un cobro que entra a Caja o Bancos.

### Nota sobre la simplificación del IVA

Se neteó todo el IVA (el que pagamos y el que cobramos) en una sola cuenta (2408), en vez de separar "IVA generado" (pasivo) e "IVA descontable" (activo) como exige la contabilidad formal NIIF. Es una simplificación válida para llevar el control interno del Módulo 1. **Si más adelante se necesita declarar IVA ante la DIAN con el detalle exigido, esta cuenta se divide en dos** — es un cambio acotado (una migración + ajustar dos reglas de esta tabla), no una reescritura.

### `total` nunca se recibe del usuario

`total = subtotal + iva`, siempre calculado por el servidor al registrar la factura. Evita que una factura quede con un total inconsistente con sus propias partes.

### Asientos generados por factura/contrato siempre son `libro = oficial`

Y su `documento_soporte` se autocompleta con la referencia a la factura/contrato (ej. `"Factura recibida F-001"`). El usuario no lo captura para estos casos — ya está implícito en el propio registro.

## 3. Movimientos manuales (`POST /movimientos`) — libro oficial vs. interno

Para todo lo que no viene de una factura o contrato: ajustes oficiales con soporte propio, o **movimientos de contabilidad interna / no oficial** (lo que en la v1 archivada se llamaba "para-contabilidad"): retiros informales, préstamos del dueño, gastos sin factura, etc. Estos también llevan partida doble completa — el usuario elige las cuentas y montos de cada línea — pero con una regla distinta según el libro:

| `libro` | `documento_soporte` | Cuenta para el balance oficial |
|---|---|---|
| `oficial` | **Obligatorio** — si no se envía, `422` | Sí |
| `interna` | No aplica (se ignora aunque se envíe) | No, salvo que se pida explícitamente (ver `/balance` abajo) |

**Request** — `POST /movimientos`:
```json
{
  "fecha": "2026-09-10",
  "descripcion": "El dueño retira efectivo para gasto personal",
  "libro": "interna",
  "documento_soporte": null,
  "lineas": [
    {"cuenta_codigo": "2905", "debito": "50000", "credito": "0"},
    {"cuenta_codigo": "1105", "debito": "0", "credito": "50000"}
  ]
}
```

Validaciones (en `services.py`, no en el router):
- `libro = oficial` sin `documento_soporte` (vacío o nulo) → error, `422`
- Las líneas no cuadran (suma débito ≠ suma crédito) → error, `422` (se detecta antes de guardar, no después)
- Alguna `cuenta_codigo` no existe en el plan de cuentas → `404`
- Menos de 2 líneas → `422` (partida doble exige al menos dos)

## 4. Endpoints

| Método | Ruta | Qué hace | Genera asiento |
|---|---|---|---|
| `POST` | `/terceros` | Crea un cliente o proveedor | No |
| `GET` | `/terceros` | Lista terceros | No |
| `POST` | `/facturas` | Registra una factura (emitida o recibida) | Sí — automático, según tabla arriba |
| `GET` | `/facturas` | Lista facturas (filtros opcionales: `tipo`, `estado`) | No |
| `GET` | `/facturas/{id}` | Detalle de una factura | No |
| `POST` | `/facturas/{id}/pagar` | Marca una factura como pagada, con medio de pago (`caja` o `bancos`) | Sí — automático |
| `POST` | `/contratos` | Registra un contrato (sin lógica de pagos en este módulo) | No |
| `GET` | `/contratos` | Lista contratos | No |
| `GET` | `/cuentas` | Lista el plan de cuentas | No |
| `POST` | `/movimientos` | Asiento manual, oficial o interno (ver sección 3) | Sí |
| `GET` | `/asientos` | Lista todos los asientos con sus líneas (filtro opcional `libro`) | — |
| `GET` | `/balance` | Saldo acumulado por cuenta, a la fecha actual (sin filtro de periodo todavía) | — |

## 5. Cálculo del balance

Cada cuenta tiene una "naturaleza": para Activo y Gasto, el saldo normal es `débito − crédito`; para Pasivo, Patrimonio e Ingreso, es `crédito − débito`. El endpoint `/balance` sigue esta regla por cada cuenta usando las líneas de asiento existentes. No hay filtro por fecha en este módulo — es el saldo acumulado histórico completo (queda para el Módulo 4 el reporte con corte por periodo).

**Por defecto, `/balance` solo cuenta asientos de `libro = oficial`** — esta es la aclaración pedida: lo interno/no oficial no debe aparecer en la contabilidad real. Query param opcional `incluir_interna=true` para ver el balance combinado (oficial + interno) — útil para que el dueño vea la caja "real" total, no solo la oficial.

## 6. Manejo de errores

| Caso | Respuesta |
|---|---|
| Tercero no existe al registrar factura/contrato | `404` |
| Factura ya pagada o anulada, se intenta pagar de nuevo | `409` |
| Movimiento manual con `libro = oficial` sin `documento_soporte` | `422` |
| Movimiento manual con líneas que no cuadran, menos de 2 líneas, o cuenta inexistente | `422` / `404` según el caso (ver sección 3) |
| Un asiento generado por el servicio no cuadra (no debería pasar nunca si se sigue este diseño — se valida igual, como red de seguridad) | `500` con mensaje explícito, y no se guarda nada (rollback) |
| Datos de entrada inválidos (tipos, campos faltantes) | `422`, lo maneja FastAPI automáticamente vía Pydantic |

## 7. Cómo se prueba

`backend/api_smoke_test.py` — usa el `TestClient` de FastAPI (no necesita un servidor corriendo aparte) para simular: crear un tercero, registrar una factura recibida, verificar que el asiento generado cuadra y que el balance refleja el movimiento, pagarla, verificar que el balance vuelve a moverse, lo mismo para una factura emitida, y movimientos manuales oficiales/internos: que el interno no aparezca en `/balance` por defecto pero sí con `incluir_interna=true`, y que un movimiento oficial sin soporte sea rechazado. Se corre antes de dar el endpoint por terminado.
