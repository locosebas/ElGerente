# Testing

## Dos tipos de prueba, y por qué las dos

| Tipo | Qué prueba | Ejemplo |
|---|---|---|
| **Unitario** | Una regla de negocio aislada, llamando directo a la función | "el total de una factura es `subtotal + iva`, nunca lo que mande el cliente" |
| **Integración** | Un flujo completo, cruzando varias features, como lo viviría un usuario real | "crear un tercero, registrarle una factura, pagarla, y ver el balance moverse dos veces" |

El dueño pidió explícitamente **las dos**: los unitarios dan diagnóstico fino (dicen
exactamente qué regla se rompió); los de integración dan confianza de que las piezas
encajan de verdad.

## Dónde vive cada test

```
backend/tests/
  conftest.py            # fixtures compartidas (ver abajo)
  unit/
    contabilidad/        # espejo de la estructura de features
    facturas/
    ...
  integration/
    test_facturas.py
    test_movimientos_libros.py
    test_whatsapp_flujo_factura.py
    test_migraciones.py
```

Regla: **los unitarios de una feature van en `tests/unit/<feature>/`**; los que tocan
varias features van en `tests/integration/`.

## Cómo se corre

Desde `backend/`, con el entorno activado:

```bash
pytest                          # toda la suite
pytest -m "not integration"     # solo unitarios (rápido)
pytest tests/integration -q     # solo integración
pytest tests/unit/facturas -q   # solo una feature
pytest --collect-only -q        # lista todos los tests sin ejecutarlos
```

Todos los tests son `async def`. `pytest-asyncio` está en modo `auto` (configurado en
`pyproject.toml`), así que no hace falta ningún decorador.

## Las fixtures (en `conftest.py`)

Una "fixture" es algo que el test recibe ya listo (una base de datos limpia, un cliente
HTTP...). Las principales:

| Fixture | Qué entrega |
|---|---|
| `engine` | Un motor SQLite **en memoria** con el esquema ya creado, que dura toda la sesión de tests |
| `db_session` | Una sesión de base de datos que hace *rollback* al terminar cada test (los tests no se pisan entre sí) |
| `plan_cuentas` | *(autouse)* siembra el plan de cuentas antes de cada test |
| `client` | Un `httpx.AsyncClient` apuntando a la app real, con la base de datos de test enchufada |
| `whatsapp_fake` | Un proveedor de WhatsApp falso que **no envía nada**, solo guarda los mensajes salientes en una lista `.enviados` para poder revisarlos |

## Catálogo de pruebas

Cada `spec.md` de feature tiene una sección "Casos de prueba" con la lista de sus tests.
Todo eso está consolidado en un solo documento navegable:
[`../features/pruebas.md`](../features/pruebas.md).

Ese catálogo se mantiene a mano y se contrasta con la realidad corriendo
`pytest --collect-only -q`: si aparece un test que no está en el catálogo (o al revés), se
actualiza.

## Qué NO se prueba en v1

- La interfaz gráfica HTML no tiene tests de navegador (Playwright/Selenium). Su lógica es
  la de la API, que ya está cubierta. Solo hay un test de que las páginas se sirven.
- El envío real de mensajes por WhatsApp: se usa el proveedor falso. El adaptador real de
  Meta se prueba a mano cuando se conecte un número.
