# Feature: movimientos

**Módulo**: 1 — motor contable
**Código**: `backend/app/features/movimientos/`
**Estado**: hecho y verificado (56 tests en verde)

## 1. Propósito

Registrar asientos **manuales** de partida doble para todo lo que no viene de una factura o
un contrato:

- ajustes **oficiales** con su propio documento de soporte (caja menor, corrección, aporte
  de capital...);
- movimientos del **libro interno** (para-contabilidad): retiros informales del dueño,
  préstamos sin papeles, gastos sin factura;
- **consignaciones sin factura asociada**: dinero que entra a Caja o Bancos y no corresponde
  al cobro de una factura registrada.

Aquí el usuario **sí elige las cuentas y montos** de cada línea (a diferencia de facturas y
pagos, donde el asiento es automático).

## 2. Alcance

**Sí incluye en v1:**
- `POST /movimientos` con `fecha`, `descripcion`, `libro`, `documento_soporte` (si aplica) y
  una lista de `lineas` (`cuenta_codigo`, `debito`, `credito`).
- Validación completa antes de guardar.

**No incluye:**
- Plantillas de movimientos frecuentes.
- Adjuntar archivo de soporte real (Módulo 3).
- Editar o revertir un movimiento guardado.

## 3. Reglas de negocio

1. **Mínimo 2 líneas.** Menos → `DatosInvalidos` (422).
2. **Cada línea tiene débito o crédito distinto de cero** (no ambas en 0). Si no →
   `DatosInvalidos` (422).
3. **Las líneas deben cuadrar:** `suma(débitos) = suma(créditos)`. Se comprueba **antes** de
   guardar → `DatosInvalidos` (422). (En el núcleo esto es `AsientoDesbalanceado`; para
   movimientos manuales se expone como 422 porque es error del usuario, no del sistema.)
4. **Toda `cuenta_codigo` debe existir** en el plan de cuentas → si no, `NoEncontrado` (404).
5. **`libro = oficial` ⇒ `documento_soporte` obligatorio** (nulo o vacío → `DatosInvalidos`
   422).
6. **`libro = interna` ⇒ `documento_soporte` se ignora.**
7. El asiento se crea con `origen = manual` y el `libro` indicado.

### Sobre las consignaciones

Una consignación puede registrarse de dos formas, según el caso:

- **Si corresponde al cobro de una factura emitida ya registrada** → se usa la feature
  [`pagos`](../pagos/spec.md) (`POST /facturas/{id}/pagar` con `medio_pago: bancos`).
- **Si no hay factura** (un anticipo, un aporte, un ingreso suelto) → se registra aquí como
  movimiento, típicamente: débito `1110 Bancos`, crédito la cuenta que corresponda
  (`4135 Ingresos`, `2905 Cuentas con el dueño`, `3115 Capital`...).

El flujo de WhatsApp [`whatsapp-flujo-movimiento`](../whatsapp-flujo-movimiento/spec.md)
preguntará "¿está asociada a una factura?" y encaminará a una u otra feature.

## 4. Modelo de datos

No crea tablas. Crea un `asiento` (`origen = manual`) y sus `linea_asiento`.

## 5. Interfaz

| Método | Ruta | Cuerpo | Respuesta |
|---|---|---|---|
| `POST` | `/movimientos` | ver abajo | `AsientoOut` (200) |

```json
{
  "fecha": "2026-09-12",
  "descripcion": "El dueño retira efectivo para gasto personal",
  "libro": "interna",
  "documento_soporte": null,
  "lineas": [
    { "cuenta_codigo": "2905", "debito": "50000", "credito": "0" },
    { "cuenta_codigo": "1105", "debito": "0", "credito": "50000" }
  ]
}
```

`AsientoOut`: `id`, `fecha`, `descripcion`, `origen`, `libro`, `documento_soporte`,
`created_at`, `lineas[]` (cada una con `cuenta_codigo`, `cuenta_nombre`, `debito`,
`credito`).

## 6. Errores

| Caso | Respuesta |
|---|---|
| Menos de 2 líneas | `422` |
| Una línea con débito y crédito ambos en 0 | `422` |
| Las líneas no cuadran | `422` |
| `libro = oficial` sin `documento_soporte` | `422` |
| Alguna `cuenta_codigo` no existe | `404` |
| Falta un campo / tipo inválido | `422` (Pydantic) |

## 7. Casos de prueba

| id del test | tipo | qué verifica | archivo |
|---|---|---|---|
| `test_movimiento_oficial_con_soporte_ok` | unit | asiento `origen=manual`, `libro=oficial`, guardado | `tests/unit/movimientos/test_service.py` |
| `test_movimiento_oficial_sin_soporte_falla` | unit | `DatosInvalidos` | `tests/unit/movimientos/test_service.py` |
| `test_movimiento_interno_sin_soporte_ok` | unit | `libro=interna` sin soporte → OK | `tests/unit/movimientos/test_service.py` |
| `test_movimiento_menos_de_dos_lineas` | unit | 1 línea → `DatosInvalidos` | `tests/unit/movimientos/test_service.py` |
| `test_movimiento_lineas_no_cuadran` | unit | débitos ≠ créditos → `DatosInvalidos`, 0 filas | `tests/unit/movimientos/test_service.py` |
| `test_movimiento_cuenta_inexistente` | unit | `cuenta_codigo="9999"` → `NoEncontrado` | `tests/unit/movimientos/test_service.py` |
| `test_post_movimiento_oficial_sin_soporte_422` | integración | `POST /movimientos` libro oficial sin soporte → 422 | `tests/integration/test_movimientos_libros.py` |
| `test_post_movimiento_interno_no_afecta_balance_oficial` | integración | tras un movimiento interno, `GET /balance` no cambia; `GET /balance?incluir_interna=true` sí | `tests/integration/test_movimientos_libros.py` |
| `test_post_movimiento_cuenta_inexistente_404` | integración | 404 | `tests/integration/test_movimientos_libros.py` |
| `test_get_asientos_libro_interna` | integración | `GET /asientos?libro=interna` trae solo los internos | `tests/integration/test_movimientos_libros.py` |

## 8. Notas / decisiones abiertas

- La distinción "consignación con factura" vs. "sin factura" se resuelve en la capa de
  WhatsApp; el motor solo ofrece las dos herramientas (`pagos` y `movimientos`).
- `documento_soporte` es hoy solo texto (número de recibo, nota). Cuando el Módulo 3 permita
  subir archivos, se conecta a un archivo real.
