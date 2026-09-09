# Feature: balance

**Módulo**: 1 — motor contable
**Código**: `backend/app/contabilidad/balance.py` + endpoint en `app/contabilidad/router.py`
**Estado**: hecho y verificado (56 tests en verde)

## 1. Propósito

Dar el **saldo acumulado de cada cuenta** a partir de todas las líneas de asiento
existentes. Es la consulta principal para saber "cómo va la empresa": cuánto hay en caja y
bancos, cuánto se debe, cuánto se cobra.

Vive junto al núcleo contable pero se documenta aparte porque es una feature de consulta
con su propia regla (oficial vs. real) que conviene poder auditar sola.

## 2. Alcance

**Sí incluye en v1:**
- Saldo por cuenta, con el signo correcto según la naturaleza de la cuenta.
- Opción de incluir o no el libro interno.
- Todas las cuentas en la respuesta, incluso las de saldo 0.

**No incluye:**
- Corte por fecha / periodo (Módulo 4).
- Agrupación por tipo, totales de "activo total", "resultado del ejercicio", etc. (Módulo 4).
- Comparación entre periodos.

## 3. Reglas de negocio

1. **Signo según naturaleza** (ver `contabilidad-nucleo` regla 6): deudora
   `débitos − créditos`; acreedora `créditos − débitos`.
2. **Por defecto solo `libro = oficial`.** `incluir_interna=true` suma también el interno.
3. **Se calcula con una sola consulta SQL de agregación**, no iterando objetos Python.
4. **La respuesta lista todas las cuentas del plan**, ordenadas por código, incluso con
   saldo 0 — para que la interfaz muestre siempre la misma tabla.
5. Acumulado histórico completo: no hay filtro de fecha.

## 4. Modelo de datos

No crea tablas. Lee de `cuenta`, `asiento` y `linea_asiento`.

## 5. Interfaz

| Método | Ruta | Query | Respuesta |
|---|---|---|---|
| `GET` | `/balance` | `incluir_interna` bool (default `false`) | `SaldoCuenta[]` |

`SaldoCuenta`: `{ "cuenta_codigo": "1105", "cuenta_nombre": "Caja", "tipo": "activo", "saldo": "150000.00" }`

Interpretación de ejemplos:
- `1105 Caja` con saldo `595000.00` → hay $595.000 en caja.
- `2905 Cuentas con el dueño` (pasivo) con saldo `-50000.00` → saldo negativo en un pasivo
  = el dueño le debe $50.000 a la empresa.

## 6. Errores

Ninguno propio. `incluir_interna` mal tipado → `422` (Pydantic).

## 7. Casos de prueba

| id del test | tipo | qué verifica | archivo |
|---|---|---|---|
| `test_balance_signo_por_naturaleza` | unit | (compartido con `contabilidad-nucleo`) | `tests/unit/contabilidad/test_balance.py` |
| `test_balance_incluye_cuentas_sin_movimiento` | unit | cuenta sin líneas → saldo 0 y presente | `tests/unit/contabilidad/test_balance.py` |
| `test_balance_ignora_interna_por_defecto` | unit | interno fuera por defecto, dentro con el flag | `tests/unit/contabilidad/test_balance.py` |
| `test_balance_una_sola_consulta` | unit | `calcular_balance` no dispara N consultas (cuenta las sentencias emitidas) | `tests/unit/contabilidad/test_balance.py` |
| `test_get_balance_refleja_factura_y_pago` | integración | tras registrar y pagar una factura recibida, Caja/Bancos y Cuentas por pagar quedan como se espera | `tests/integration/test_contabilidad.py` |
| `test_get_balance_vs_incluir_interna` | integración | (compartido con `contabilidad-nucleo`) | `tests/integration/test_contabilidad.py` |

## 8. Notas / decisiones abiertas

- El nombre "balance" aquí es informal (saldos por cuenta). El **balance general** formal y
  el **estado de resultados** con su estructura contable son parte del Módulo 4.
