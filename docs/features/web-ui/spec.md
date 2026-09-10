# Feature: web-ui (interfaz gráfica HTML)

**Módulo**: 1+2 (transversal)
**Código**: `backend/app/web/`
**Estado**: hecho y verificado (3 tests)

## 1. Propósito

Una interfaz web mínima para que el dueño **registre y consulte** todo lo del motor
contable sin usar `curl` ni la página `/docs`. Sirve para ver, de un vistazo, que la
contabilidad "se mueve" como debe. Más adelante suma una pestaña para simular la
conversación de WhatsApp sin Meta.

## 2. Alcance

**Sí incluye en esta etapa (Módulo 1):**
- Servida por el propio backend en `/` (StaticFiles de FastAPI). Sin paso de build, sin
  framework con tooling: un `index.html` + `app.js` (JavaScript plano, `fetch`) +
  `styles.css`.
- Consume **la misma API REST** ya probada. **No añade lógica de negocio.**
- Pantallas en dos grupos: **Registrar** (Movimientos, Facturas, Contratos, Terceros) y
  **Analizar** (Balance, Libro diario). El registro de movimientos es lo principal y es la
  pantalla que abre por defecto; el resto es análisis.

**No incluye ahora:**
- Pestaña "Simulador WhatsApp" (se agrega en la etapa del Módulo 2).
- Autenticación / login (una sola persona por ahora).
- Editar o borrar registros (la API tampoco lo permite en v1).
- Tests de navegador (Playwright/Selenium). La lógica ya está cubierta por los tests de la
  API; aquí solo se verifica que las páginas se sirven.

## 3. Reglas de negocio

Ninguna propia. Toda validación y todo cálculo ocurre en el backend. Si la API responde un
error (404, 409, 422...), la interfaz muestra el mensaje `detail` tal cual.

## 4. Modelo de datos

No crea tablas.

## 5. Interfaz

### Cómo se sirve

- `GET /` → `index.html`
- `GET /static/app.js`, `GET /static/styles.css` → los estáticos
- El montaje va **después** de los routers de la API, así `/cuentas`, `/facturas`, etc.
  siguen respondiendo JSON.

### Pantallas y qué llaman

| Pantalla | Llamadas a la API | Contenido |
|---|---|---|
| **Balance** | `GET /balance` (+ checkbox `incluir_interna`) | tabla: código, cuenta, tipo, saldo. Resalta saldos negativos. |
| **Libro diario** | `GET /asientos` (+ filtro `libro`) | por asiento: fecha, descripción, origen, libro, soporte, y sus líneas débito/crédito con el total |
| **Terceros** | `GET /terceros`, `POST /terceros` | tabla + formulario (nombre, NIT/cédula, tipo) |
| **Facturas** | `GET /terceros`, `GET /facturas`, `POST /facturas`, `POST /facturas/{id}/pagar` | tabla (número, tipo, tercero, total, estado) con botón "pagar/cobrar" que abre un mini-formulario (medio de pago, fecha); formulario de alta (tipo, número, fecha, tercero, subtotal, IVA) |
| **Contratos** | `GET /terceros`, `GET /contratos`, `POST /contratos` | tabla + formulario (tercero, objeto, valor, fecha inicio, fecha fin) |
| **Movimiento manual** | `GET /cuentas`, `POST /movimientos` | formulario: fecha, descripción, libro (oficial/interna), soporte, y filas de líneas dinámicas (cuenta, débito, crédito) con "+ agregar línea"; muestra el descuadre en vivo |

### Comportamiento general

- Navegación por pestañas en una barra lateral; una sola página, sin recarga.
- Los montos se muestran con separador de miles.
- Tras un alta exitosa, se limpia el formulario y se recarga la tabla.
- Los errores de la API se muestran en un aviso arriba del formulario.

## 6. Errores

| Caso | Qué hace la interfaz |
|---|---|
| La API responde 4xx/5xx | muestra el `detail` en un aviso rojo, no borra lo que el usuario escribió |
| La API no responde | aviso "no se pudo conectar con el servidor" |

## 7. Casos de prueba

| id del test | tipo | qué verifica | archivo |
|---|---|---|---|
| `test_home_sirve_html` | integración | `GET /` → 200 y `content-type` HTML | `tests/integration/test_web_ui.py` |
| `test_estaticos_se_sirven` | integración | `GET /static/app.js` y `/static/styles.css` → 200 | `tests/integration/test_web_ui.py` |
| `test_api_sigue_respondiendo_con_ui_montada` | integración | `GET /cuentas` → 200 JSON aunque el StaticFiles esté montado en `/` | `tests/integration/test_web_ui.py` |

## 8. Notas / decisiones abiertas

- **Sin build ni framework**: coherente con "cero infraestructura" y con que el dueño pueda
  leer el código. Si la interfaz crece mucho, se reevalúa.
- La pestaña "Simulador WhatsApp" se documenta y agrega junto con el Módulo 2.
- **Dirección del producto (dueño, 2026-09-09):** registrar movimientos de plata es lo
  principal; facturas, contratos y balance son "análisis avanzado". La pantalla de
  movimientos abre por defecto. **Pendiente por decidir:** una entrada simplificada de
  "entró/salió plata" que no obligue a elegir cuentas ni pensar en débito/crédito (el
  sistema elegiría las cuentas por el tipo de movimiento). Hoy la pantalla de movimientos
  todavía pide cuenta + débito + crédito por línea.
- **Datos de demostración:** `backend/scripts/seed_demo.py` carga un negocio inventado
  (terceros, ~14 facturas, movimientos internos/oficiales, contratos) para ver la interfaz
  con contenido. No es para producción.
