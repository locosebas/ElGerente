# Feature: contabilidad-nucleo

**Módulo**: 1 — motor contable
**Código**: `backend/app/contabilidad/`
**Estado**: hecho y verificado (56 tests en verde)

## 1. Propósito

Registrar y consultar hechos económicos como **asientos de partida doble** (cada asiento
mueve al menos dos cuentas y la suma de débitos siempre iguala la suma de créditos), sobre
un **plan de cuentas** fijo, separando dos libros: **oficial** (contabilidad real, exige
documento de soporte) e **interno** (para-contabilidad, sin soporte, fuera del balance
oficial por defecto).

Es el núcleo compartido: **ninguna otra feature escribe en las tablas contables sin pasar
por aquí** (`crear_asiento`).

## 2. Alcance

**Sí incluye en v1:**
- Modelos `cuenta`, `asiento`, `linea_asiento` y sus enums.
- `crear_asiento(...)`: único punto de escritura, con validación de cuadre y de documento
  de soporte.
- `calcular_balance(...)`: saldo acumulado por cuenta (ver también la feature `balance`).
- Siembra idempotente del plan de cuentas.
- Endpoints de solo lectura: `/cuentas`, `/asientos`, `/balance`.

**No incluye (queda para después):**
- Crear/editar cuentas por API (el plan de cuentas se siembra y se edita en código).
- Balance con corte por periodo / fecha (Módulo 4).
- Anulación o reversión de asientos ya guardados.
- Separar el IVA en dos cuentas (IVA generado / descontable) — ver §8.

## 3. Reglas de negocio

1. **Partida doble.** Un asiento no se persiste si `suma(débitos) ≠ suma(créditos)`. Se
   valida **antes** de guardar; si falla, no queda ninguna fila (`AsientoDesbalanceado`).
2. **Comparación exacta con `Decimal`.** Todos los montos son `decimal.Decimal`, nunca
   `float`. `0.1 + 0.2` debe dar exactamente `0.3`.
3. **Libro oficial ⇒ `documento_soporte` obligatorio.** Si `libro = oficial` y
   `documento_soporte` es nulo o vacío → `DocumentoSoporteRequerido`. Sin excepción,
   incluso para asientos generados automáticamente (ahí el soporte se autocompleta con la
   referencia del documento, p. ej. `"Factura recibida F-001"`).
4. **Libro interno ⇒ `documento_soporte` no aplica.** Se ignora aunque se envíe.
5. **`crear_asiento` hace `flush`, no `commit`.** Deja el `id` disponible pero la decisión
   de confirmar la transacción es de quien llama (el servicio de la feature).
6. **Signo del saldo según la naturaleza de la cuenta:**
   - naturaleza **deudora** (activo, gasto): `saldo = débitos − créditos`;
   - naturaleza **acreedora** (pasivo, patrimonio, ingreso): `saldo = créditos − débitos`.
7. **El balance por defecto solo suma `libro = oficial`.** `incluir_interna=true` devuelve
   el combinado (oficial + interno).
8. **Sin filtro por periodo en v1.** El balance es el acumulado histórico completo.
9. **El plan de cuentas se siembra una sola vez.** `sembrar_plan_de_cuentas` es
   idempotente: si `cuenta` ya tiene filas, no hace nada.

## 4. Modelo de datos

### `cuenta` — el plan de cuentas

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | int, PK | |
| `codigo` | str(10), único | inspirado en el PUC colombiano (evita choque futuro con la DIAN) |
| `nombre` | str(100) | |
| `tipo` | enum `TipoCuenta` | `activo` \| `pasivo` \| `patrimonio` \| `ingreso` \| `gasto` |

Propiedad derivada (no es columna) `naturaleza` → `"deudora"` para `activo`/`gasto`,
`"acreedora"` para el resto.

### `asiento` — encabezado del comprobante contable

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | int, PK | |
| `fecha` | date | fecha del hecho económico; la aporta quien registra, no es `now()` |
| `descripcion` | text | |
| `origen` | enum `OrigenAsiento` | `factura` \| `contrato` \| `manual` — de qué feature nació |
| `libro` | enum `LibroContable` | `oficial` \| `interna`; por defecto `oficial` |
| `documento_soporte` | str(255), nullable | obligatorio si `libro = oficial` (regla 3) |
| `created_at` | datetime | `utcnow` al crear (auditoría; distinto de `fecha`) |

Relación: `asiento.lineas` → lista de `linea_asiento`, con `cascade="all, delete-orphan"`.

### `linea_asiento` — las líneas débito/crédito

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | int, PK | |
| `asiento_id` | FK → `asiento.id` | |
| `cuenta_id` | FK → `cuenta.id` | |
| `debito` | Numeric(14,2) | ≥ 0, por defecto `0` |
| `credito` | Numeric(14,2) | ≥ 0, por defecto `0` |

`Numeric(14,2)` = hasta 999.999.999.999,99.

## 5. Interfaz

### Plan de cuentas sembrado

| Código | Nombre | Tipo | Uso principal |
|---|---|---|---|
| 1105 | Caja | activo | efectivo |
| 1110 | Bancos | activo | transferencias / consignaciones |
| 1305 | Cuentas por cobrar | activo | facturas emitidas pendientes de cobro |
| 2205 | Cuentas por pagar | pasivo | facturas recibidas pendientes de pago |
| 2408 | Impuestos por pagar - IVA | pasivo | IVA neteado (ver §8) |
| 2905 | Cuentas con el dueño | pasivo | puente dueño ↔ empresa (libro interno); puede quedar negativo |
| 3115 | Capital | patrimonio | aportes del dueño |
| 4135 | Ingresos por ventas | ingreso | subtotal de facturas emitidas |
| 5195 | Gastos diversos | gasto | subtotal de facturas recibidas |
| 5905 | Gastos internos sin soporte | gasto | gastos sin factura (libro interno) |

### Funciones del núcleo (todas `async`)

```
crear_asiento(session, *, fecha, descripcion, origen, lineas,
              libro=OFICIAL, documento_soporte=None) -> Asiento
```
Orden: (1) valida documento de soporte si es oficial → `DocumentoSoporteRequerido`;
(2) arma el asiento en memoria; (3) valida cuadre → `AsientoDesbalanceado`;
(4) `session.add` + `session.flush()`.

```
calcular_balance(session, *, incluir_interna=False) -> list[SaldoCuenta]
```
Una sola consulta de agregación:

```sql
SELECT c.codigo, c.nombre, c.tipo,
       COALESCE(SUM(l.debito), 0)  AS td,
       COALESCE(SUM(l.credito), 0) AS tc
FROM cuenta c
LEFT JOIN linea_asiento l ON l.cuenta_id = c.id
LEFT JOIN asiento a       ON a.id = l.asiento_id
WHERE :incluir_interna = 1 OR a.libro = 'oficial' OR a.id IS NULL
GROUP BY c.id
ORDER BY c.codigo
```
Luego, en Python, aplica el signo de la regla 6. Devuelve **todas** las cuentas, incluidas
las de saldo 0.

```
sembrar_plan_de_cuentas(session) -> None      # idempotente
```

### Endpoints (router del núcleo)

| Método | Ruta | Query | Respuesta |
|---|---|---|---|
| `GET` | `/cuentas` | — | plan de cuentas ordenado por `codigo` (`CuentaOut[]`) |
| `GET` | `/asientos` | `libro` opcional (`oficial`\|`interna`) | `AsientoOut[]`: cada asiento con sus líneas; cada línea trae `cuenta_codigo` y `cuenta_nombre` |
| `GET` | `/balance` | `incluir_interna` bool (default `false`) | `SaldoCuenta[]`: `cuenta_codigo`, `cuenta_nombre`, `tipo`, `saldo` |

La consulta de `/asientos` usa `selectinload(Asiento.lineas).selectinload(LineaAsiento.cuenta)`
para no disparar carga perezosa (async).

## 6. Errores

| Caso | Excepción de dominio | HTTP |
|---|---|---|
| Asiento oficial sin `documento_soporte` | `DocumentoSoporteRequerido` (`DatosInvalidos`) | 422 |
| Asiento que no cuadra (no debería pasar si las reglas de las features son correctas — red de seguridad) | `AsientoDesbalanceado` | 500, con mensaje explícito y rollback |
| `libro` inválido en el filtro de `/asientos` | — | 422 (Pydantic) |

## 7. Casos de prueba

| id del test | tipo | qué verifica | archivo |
|---|---|---|---|
| `test_asiento_que_cuadra_se_guarda` | unit | débitos = créditos → se persiste con id | `tests/unit/contabilidad/test_asientos.py` |
| `test_asiento_descuadrado_no_deja_filas` | unit | débitos ≠ créditos → `AsientoDesbalanceado` y 0 filas | `tests/unit/contabilidad/test_asientos.py` |
| `test_oficial_sin_soporte_falla` | unit | `libro=oficial`, sin soporte → `DocumentoSoporteRequerido` | `tests/unit/contabilidad/test_asientos.py` |
| `test_oficial_con_soporte_ok` | unit | `libro=oficial` + soporte → OK | `tests/unit/contabilidad/test_asientos.py` |
| `test_interna_sin_soporte_ok` | unit | `libro=interna`, sin soporte → OK | `tests/unit/contabilidad/test_asientos.py` |
| `test_cuadre_usa_decimal_exacto` | unit | `0.1 + 0.2` en líneas cuadra exactamente | `tests/unit/contabilidad/test_asientos.py` |
| `test_balance_signo_por_naturaleza` | unit | activo con más débito → saldo positivo; pasivo con más crédito → saldo positivo | `tests/unit/contabilidad/test_balance.py` |
| `test_balance_incluye_cuentas_sin_movimiento` | unit | una cuenta sin líneas aparece con saldo 0 | `tests/unit/contabilidad/test_balance.py` |
| `test_balance_ignora_interna_por_defecto` | unit | asiento interno no afecta; con `incluir_interna=True` sí | `tests/unit/contabilidad/test_balance.py` |
| `test_seed_es_idempotente` | unit | sembrar dos veces no duplica cuentas | `tests/unit/contabilidad/test_plan_cuentas.py` |
| `test_get_cuentas_devuelve_plan_completo` | integración | `GET /cuentas` → 10 cuentas, ordenadas por código | `tests/integration/test_contabilidad.py` |
| `test_get_asientos_filtra_por_libro` | integración | `GET /asientos?libro=interna` tras un movimiento interno → solo ese | `tests/integration/test_contabilidad.py` |
| `test_get_balance_vs_incluir_interna` | integración | los dos balances difieren exactamente en el monto interno registrado | `tests/integration/test_contabilidad.py` |
| `test_invariante_todos_los_asientos_cuadran` | integración | tras toda la suite, cada asiento de `GET /asientos` cuadra línea a línea | `tests/integration/test_contabilidad.py` |

## 8. Notas / decisiones abiertas

- **IVA neteado (simplificación consciente).** Todo el IVA —el pagado en compras y el
  cobrado en ventas— va a una sola cuenta, `2408`. La contabilidad formal NIIF separa "IVA
  generado" (pasivo) e "IVA descontable" (activo). Si más adelante hay que declarar IVA a
  la DIAN con ese detalle, `2408` se parte en dos: es una migración acotada + ajustar dos
  reglas de la feature `facturas`, no una reescritura.
- **El plan de cuentas es fijo en v1.** Si el negocio necesita una cuenta nueva, se agrega
  a `plan_cuentas.py` y se siembra. No hay ABM de cuentas por interfaz todavía.
