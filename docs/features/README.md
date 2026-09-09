# Índice de features

Cada feature es una parte funcional del programa: una carpeta de código autocontenida
(`router` + `service` + `schemas` + `models` + `exceptions`) y esta carpeta de
documentación espejo con su `spec.md`.

Ver la [plantilla de spec](_PLANTILLA-spec.md) y el [catálogo de pruebas](pruebas.md).

## Estado

Leyenda: ⬜ pendiente · 🟨 en progreso · ✅ hecho y verificado

### Módulo 1 — motor contable

| # | Feature | Estado | Spec | Código | Tests |
|---|---|---|---|---|---|
| 1 | `contabilidad-nucleo` | ✅ | [spec](contabilidad-nucleo/spec.md) | `app/contabilidad/` | `pytest tests/unit/contabilidad tests/integration/test_contabilidad.py` |
| 2 | `balance` | ✅ | [spec](balance/spec.md) | `app/contabilidad/balance.py` | `pytest tests/unit/contabilidad/test_balance.py` |
| 3 | `terceros` | ✅ | [spec](terceros/spec.md) | `app/features/terceros/` | `pytest tests/unit/terceros tests/integration/test_terceros.py` |
| 4 | `facturas` | ✅ | [spec](facturas/spec.md) | `app/features/facturas/` | `pytest tests/unit/facturas tests/integration/test_facturas.py` |
| 5 | `pagos` | ✅ | [spec](pagos/spec.md) | `app/features/pagos/` | `pytest tests/unit/pagos tests/integration/test_facturas.py` |
| 6 | `contratos` | ✅ | [spec](contratos/spec.md) | `app/features/contratos/` | `pytest tests/unit/contratos tests/integration/test_contratos.py` |
| 7 | `movimientos` | ✅ | [spec](movimientos/spec.md) | `app/features/movimientos/` | `pytest tests/unit/movimientos tests/integration/test_movimientos_libros.py` |

### Módulo 2 — WhatsApp

| # | Feature | Estado | Spec | Código | Tests |
|---|---|---|---|---|---|
| 8 | `whatsapp-proveedor` | ⬜ | _(pendiente de escribir)_ | `app/features/whatsapp/provider.py` | — |
| 9 | `whatsapp-webhook` | ⬜ | _(pendiente)_ | `app/features/whatsapp/router.py` | — |
| 10 | `whatsapp-conversaciones` (motor de máquina de estados + persistencia) | ⬜ | _(pendiente)_ | `app/features/whatsapp/conversaciones/` | — |
| 11 | `whatsapp-asistente` (menú, ayuda, cancelar, intención — **determinístico**) | ⬜ | _(pendiente)_ | `app/features/whatsapp/asistente/` | — |
| 12 | `whatsapp-flujo-factura` | ⬜ | _(pendiente)_ | `app/features/whatsapp/flows/factura.py` | — |
| 13 | `whatsapp-flujo-pago` | ⬜ | _(pendiente)_ | `app/features/whatsapp/flows/pago.py` | — |
| 14 | `whatsapp-flujo-contrato` | ⬜ | _(pendiente)_ | `app/features/whatsapp/flows/contrato.py` | — |
| 15 | `whatsapp-flujo-movimiento` | ⬜ | _(pendiente)_ | `app/features/whatsapp/flows/movimiento.py` | — |
| 16 | `whatsapp-consulta-balance` | ⬜ | _(pendiente)_ | `app/features/whatsapp/flows/consulta_balance.py` | — |

> **El chatbot de WhatsApp es 100 % determinístico**: ninguna feature del Módulo 2 usa IA
> ni modelos de lenguaje. Ver [`../aprendizaje/deterministico-vs-ia.md`](../aprendizaje/deterministico-vs-ia.md).

### Transversal

| # | Feature | Estado | Spec | Código | Tests |
|---|---|---|---|---|---|
| 17 | `web-ui` (interfaz gráfica HTML del Módulo 1) | ✅ | [spec](web-ui/spec.md) | `app/web/` | `pytest tests/integration/test_web_ui.py` |

## Orden de construcción

1. Esqueleto y herramientas *(Etapa 0)*.
2. Documentación de features 1–7 *(Etapa 1 — este momento)*.
3. Código + tests de features 1–7 *(Etapa 2)*.
4. Interfaz gráfica del Módulo 1 *(Etapa 2b)*.
5. Documentación de features 8–16 *(Etapa 3)*.
6. Código + tests de features 8–17 *(Etapa 4)*.
7. Cierre: catálogo de pruebas, script de simulación, READMEs *(Etapa 5)*.

Detalle en el plan de implementación aprobado.
