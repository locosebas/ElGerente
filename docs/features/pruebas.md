# Catálogo de pruebas

Lista consolidada de **todas** las pruebas del proyecto. Sale de la sección "Casos de
prueba" de cada `spec.md`. Se contrasta con la realidad ejecutando, desde `backend/`:

```bash
pytest --collect-only -q
```

Leyenda de estado: ⬜ por escribir · ✅ escrito y pasando

**Estado actual: 56 pruebas, todas en verde** (`pytest` → 56 passed). Módulo 1 completo.

---

## Módulo 1 — motor contable

### contabilidad-nucleo — `tests/unit/contabilidad/` + `tests/integration/test_contabilidad.py`

| id | tipo | verifica | estado |
|---|---|---|---|
| `test_asiento_que_cuadra_se_guarda` | unit | débitos = créditos → se persiste con id | ✅ |
| `test_asiento_descuadrado_no_deja_filas` | unit | débitos ≠ créditos → `AsientoDesbalanceado`, 0 filas | ✅ |
| `test_oficial_sin_soporte_falla` | unit | `libro=oficial` sin soporte → `DocumentoSoporteRequerido` | ✅ |
| `test_oficial_con_soporte_ok` | unit | `libro=oficial` + soporte → OK | ✅ |
| `test_interna_ignora_soporte` | unit | `libro=interna` guarda `documento_soporte=None` aunque se envíe | ✅ |
| `test_cuadre_usa_decimal_exacto` | unit | `0.10 + 0.20 == 0.30` exacto con `Decimal` | ✅ |
| `test_seed_es_idempotente` | unit | sembrar dos veces no duplica cuentas | ✅ |
| `test_get_cuentas_devuelve_plan_completo` | integración | `GET /cuentas` → 10 cuentas, en orden de código | ✅ |
| `test_get_asientos_filtra_por_libro` | integración | `?libro=interna` / `?libro=oficial` | ✅ |
| `test_get_balance_vs_incluir_interna` | integración | los dos balances difieren en el monto interno | ✅ |
| `test_get_balance_refleja_factura_y_pago` | integración | balance tras registrar y pagar una factura recibida | ✅ |
| `test_invariante_todos_los_asientos_cuadran` | integración | cada asiento de `GET /asientos` cuadra línea a línea | ✅ |

### balance — `tests/unit/contabilidad/test_balance.py`

| id | tipo | verifica | estado |
|---|---|---|---|
| `test_balance_signo_por_naturaleza` | unit | activo con más débito → +; patrimonio con más crédito → + | ✅ |
| `test_balance_incluye_cuentas_sin_movimiento` | unit | las 10 cuentas aparecen, las sin líneas con saldo 0 | ✅ |
| `test_balance_ignora_interna_por_defecto` | unit | interno fuera por defecto, dentro con `incluir_interna=True` | ✅ |

### terceros — `tests/unit/terceros/` + `tests/integration/test_terceros.py`

| id | tipo | verifica | estado |
|---|---|---|---|
| `test_crear_tercero_devuelve_id` | unit | persiste y devuelve el tercero con id | ✅ |
| `test_listar_terceros_filtra_por_tipo` | unit | `listar(tipo="cliente")` no trae proveedores | ✅ |
| `test_obtener_tercero_inexistente` | unit | id inexistente → `NoEncontrado` | ✅ |
| `test_post_terceros_ok` | integración | `POST` → 200 y aparece en `GET /terceros` | ✅ |
| `test_post_terceros_tipo_invalido` | integración | `tipo` inválido → 422 | ✅ |

### facturas — `tests/unit/facturas/` + `tests/integration/test_facturas.py`

| id | tipo | verifica | estado |
|---|---|---|---|
| `test_total_se_calcula_en_servidor` | unit | `total = subtotal + iva` | ✅ |
| `test_factura_recibida_genera_asiento_correcto` | unit | 3 líneas: 5195 D, 2408 D, 2205 C; soporte autocompletado | ✅ |
| `test_factura_emitida_genera_asiento_correcto` | unit | 3 líneas: 1305 D, 4135 C, 2408 C | ✅ |
| `test_factura_sin_iva_cuadra` | unit | `iva=0` → asiento de 2 líneas que cuadra | ✅ |
| `test_factura_tercero_inexistente` | unit | `NoEncontrado` | ✅ |
| `test_factura_nace_pendiente_y_enlaza_asiento` | unit | `estado=pendiente`, `asiento_id` no nulo | ✅ |
| `test_post_factura_recibida_end_to_end` | integración | balance refleja 5195 / 2205 / 2408 | ✅ |
| `test_post_factura_emitida_end_to_end` | integración | balance refleja 1305 / 4135 / 2408 | ✅ |
| `test_post_factura_tercero_inexistente_404` | integración | 404 | ✅ |
| `test_get_facturas_filtra` | integración | `?estado=pendiente` no trae pagadas | ✅ |

### pagos — `tests/unit/pagos/` + `tests/integration/test_facturas.py`

| id | tipo | verifica | estado |
|---|---|---|---|
| `test_pago_recibida_genera_asiento` | unit | 2205 D / 1110 C; factura → `pagada` | ✅ |
| `test_cobro_emitida_genera_asiento` | unit | 1105 D / 1305 C | ✅ |
| `test_pagar_factura_inexistente` | unit | `NoEncontrado` | ✅ |
| `test_pagar_factura_ya_pagada` | unit | `Conflicto` | ✅ |
| `test_medio_pago_invalido` | unit | `DatosInvalidos` | ✅ |
| `test_pagar_end_to_end` | integración | 2205 → 0, Bancos baja `total` | ✅ |
| `test_pagar_dos_veces_409` | integración | segundo pago → 409 | ✅ |
| `test_cobrar_emitida_end_to_end` | integración | Bancos sube, 1305 → 0 | ✅ |

### contratos — `tests/unit/contratos/` + `tests/integration/test_contratos.py`

| id | tipo | verifica | estado |
|---|---|---|---|
| `test_crear_contrato_ok` | unit | persiste, nace `vigente` | ✅ |
| `test_contrato_tercero_inexistente` | unit | `NoEncontrado` | ✅ |
| `test_contrato_fecha_fin_antes_de_inicio` | unit | `DatosInvalidos` | ✅ |
| `test_contrato_no_genera_asiento` | unit | tras crear un contrato no hay asientos | ✅ |
| `test_post_contrato_end_to_end` | integración | 200, aparece en `GET /contratos`, no toca `/asientos` | ✅ |
| `test_post_contrato_tercero_inexistente_404` | integración | 404 | ✅ |

### movimientos — `tests/unit/movimientos/` + `tests/integration/test_movimientos_libros.py`

| id | tipo | verifica | estado |
|---|---|---|---|
| `test_movimiento_oficial_con_soporte_ok` | unit | asiento `origen=manual`, `libro=oficial` | ✅ |
| `test_movimiento_oficial_sin_soporte_falla` | unit | `DatosInvalidos` | ✅ |
| `test_movimiento_interno_sin_soporte_ok` | unit | OK | ✅ |
| `test_movimiento_menos_de_dos_lineas` | unit | `DatosInvalidos` | ✅ |
| `test_movimiento_lineas_no_cuadran` | unit | `DatosInvalidos`, 0 filas | ✅ |
| `test_movimiento_cuenta_inexistente` | unit | `NoEncontrado` | ✅ |
| `test_post_movimiento_oficial_sin_soporte_422` | integración | 422 | ✅ |
| `test_post_movimiento_interno_no_afecta_balance_oficial` | integración | balance oficial sin cambio; con flag sí | ✅ |
| `test_post_movimiento_cuenta_inexistente_404` | integración | 404 | ✅ |
| `test_post_movimiento_lineas_no_cuadran_422` | integración | 422 | ✅ |
| `test_get_asientos_libro_interna` | integración | `?libro=interna` trae solo los internos | ✅ |

### infraestructura — `tests/integration/test_migraciones.py`

| id | tipo | verifica | estado |
|---|---|---|---|
| `test_no_hay_migracion_pendiente` | integración | el esquema de los modelos = el de las migraciones Alembic | ✅ |

---

## Módulo 2 — WhatsApp

_(pendiente: se completa en la Etapa 3, al escribir los specs de las features 8–16)_

## Transversal

### web-ui — `tests/integration/test_web_ui.py`

| id | tipo | verifica | estado |
|---|---|---|---|
| `test_home_sirve_html` | integración | `GET /` → 200, `text/html` | ⬜ |
| `test_estaticos_se_sirven` | integración | `GET /static/app.js` y `/static/styles.css` → 200 | ⬜ |
