# Feature: balance

**Módulo**: 1 — motor contable
**Código**: `backend/app/contabilidad/balance.py` + endpoints en `app/contabilidad/router.py`
**Estado**: hecho y verificado

## 1. Propósito

Dar el **saldo de cada cuenta** para poder ver "cómo va la empresa", con tres ejes de
consulta que el dueño pidió:

1. **Libro**: solo lo **oficial** (contabilidad real / externa), solo lo **interno**
   (para-contabilidad), o el **total** (ambos).
2. **Periodo**: todo el histórico, un **año**, o un **mes** concreto.
3. **Detalle progresivo**: del total por tipo de cuenta → a cada cuenta → a los movimientos
   que la componen (como un extracto).

## 2. Alcance

**Sí incluye en v1:**
- `GET /balance` con filtros `libro` y `desde`/`hasta` (fechas).
- `GET /cuentas/{codigo}/movimientos` — el detalle de una cuenta (extracto con saldo
  acumulado), con los mismos filtros.
- Todas las cuentas del plan en la respuesta de `/balance`, incluso con saldo 0.

**No incluye:**
- Sub-cuentas / agrupaciones más finas que el tipo (ej. "Bancos → Banco A / Banco B"). El
  plan de cuentas es plano en v1; el árbol llega hasta `tipo → cuenta → movimientos`.
- Estados financieros formales (balance general, estado de resultados con su estructura
  NIIF). Eso es Módulo 4.
- Comparar dos periodos lado a lado.

## 3. Reglas de negocio

1. **Signo del saldo por naturaleza** (ver `contabilidad-nucleo`): deudora
   `débitos − créditos`; acreedora `créditos − débitos`.
2. **Filtro `libro`** (default `oficial`):
   - `oficial` → solo asientos `libro = oficial`;
   - `interna` → solo asientos `libro = interna`;
   - `todos` → ambos.
3. **Filtro de periodo**: `desde` y `hasta` (fechas, inclusivas) se aplican sobre
   `asiento.fecha`. Cualquiera de las dos puede omitirse (sin límite por ese lado).
   Si `desde > hasta` → `DatosInvalidos` (422).
4. `/balance` se calcula con **una sola consulta de agregación** (no itera objetos).
5. `/balance` devuelve **todas** las cuentas del plan, ordenadas por código, incluso con
   saldo 0 — para que la interfaz muestre siempre el árbol completo.
6. **Saldo acumulado en el detalle**: en `/cuentas/{codigo}/movimientos`, los movimientos
   van ordenados por fecha y luego por id de asiento, y cada uno trae el saldo de la cuenta
   **después** de ese movimiento (respetando la naturaleza). El primer saldo parte de 0
   dentro del periodo consultado (no arrastra saldo anterior — es un extracto del periodo).

## 4. Modelo de datos

No crea tablas. Lee de `cuenta`, `asiento` y `linea_asiento`.

## 5. Interfaz

### `GET /balance`

| Query | Valores | Default |
|---|---|---|
| `libro` | `oficial` \| `interna` \| `todos` | `oficial` |
| `desde` | fecha `AAAA-MM-DD` | sin límite |
| `hasta` | fecha `AAAA-MM-DD` | sin límite |

Respuesta: `SaldoCuenta[]` → `{ "cuenta_codigo", "cuenta_nombre", "tipo", "saldo" }`.
La interfaz agrupa por `tipo` y calcula el subtotal de cada grupo.

### `GET /cuentas/{codigo}/movimientos`

Mismos filtros (`libro`, `desde`, `hasta`). Respuesta:

```json
{
  "cuenta_codigo": "2205",
  "cuenta_nombre": "Cuentas por pagar",
  "tipo": "pasivo",
  "saldo_final": "11853400.00",
  "movimientos": [
    {
      "asiento_id": 1, "fecha": "2026-06-03",
      "descripcion": "Factura recibida ARR-2606", "origen": "factura",
      "libro": "oficial", "documento_soporte": "Factura recibida ARR-2606",
      "debito": "0.00", "credito": "2500000.00",
      "saldo_acumulado": "2500000.00"
    }
  ]
}
```

`404` si `codigo` no está en el plan de cuentas.

## 6. Errores

| Caso | Respuesta |
|---|---|
| `desde > hasta` | `422` |
| `libro` con un valor distinto de los tres | `422` (Pydantic) |
| `/cuentas/{codigo}/movimientos` con código inexistente | `404` |
| fecha mal formada | `422` (Pydantic) |

## 7. Casos de prueba

| id del test | tipo | qué verifica | archivo |
|---|---|---|---|
| `test_balance_signo_por_naturaleza` | unit | activo con más débito → +; pasivo con más crédito → + | `tests/unit/contabilidad/test_balance.py` |
| `test_balance_incluye_cuentas_sin_movimiento` | unit | las 10 cuentas presentes, sin líneas → saldo 0 | `tests/unit/contabilidad/test_balance.py` |
| `test_balance_libro_oficial_interna_todos` | unit | los tres modos dan saldos distintos según el asiento | `tests/unit/contabilidad/test_balance.py` |
| `test_balance_filtra_por_periodo` | unit | `desde`/`hasta` deja fuera los asientos de otras fechas | `tests/unit/contabilidad/test_balance.py` |
| `test_balance_desde_mayor_que_hasta` | unit | `DatosInvalidos` | `tests/unit/contabilidad/test_balance.py` |
| `test_movimientos_de_cuenta_saldo_acumulado` | unit | el saldo acumulado avanza movimiento a movimiento | `tests/unit/contabilidad/test_detalle_cuenta.py` |
| `test_movimientos_de_cuenta_codigo_inexistente` | unit | `NoEncontrado` | `tests/unit/contabilidad/test_detalle_cuenta.py` |
| `test_get_balance_libro_y_periodo` | integración | `GET /balance?libro=todos&desde=...&hasta=...` filtra bien | `tests/integration/test_contabilidad.py` |
| `test_get_cuenta_movimientos_end_to_end` | integración | `GET /cuentas/2205/movimientos` tras registrar facturas → extracto correcto | `tests/integration/test_contabilidad.py` |
| `test_get_cuenta_movimientos_404` | integración | código inexistente → 404 | `tests/integration/test_contabilidad.py` |

## 8. Notas / decisiones abiertas

- El detalle es un **extracto del periodo** (el saldo acumulado parte de 0 dentro del rango
  consultado). Si se quiere "saldo inicial + movimientos + saldo final" arrastrando lo
  anterior, es un añadido acotado.
- Sub-cuentas ("Bancos → Banco A / Banco B"): requiere que el plan de cuentas deje de ser
  plano (una cuenta con `cuenta_padre_id`). Queda para cuando el negocio lo necesite; el
  árbol de la interfaz ya está pensado para sumar un nivel.
- El parámetro viejo `incluir_interna` de `/balance` se reemplazó por `libro`.
