# Resiliencia a fallos y logs

Cómo se comporta el sistema cuando algo sale mal, y qué queda registrado.

## Los tres tipos de error y qué pasa con cada uno

| Tipo | Ejemplo | Respuesta HTTP | Log | ¿Se guarda algo a medias? |
|---|---|---|---|---|
| **Error de dominio** (esperado) | pagar una factura que ya está pagada | el código que corresponde (404, 409, 422...) con `{"detail": "mensaje claro"}` | `INFO` — "Error de dominio 409: ..." | No |
| **Datos de entrada inválidos** | falta un campo, tipo equivocado | `422` con la lista de campos que fallan | `INFO` — "Datos de entrada inválidos: ..." | No |
| **Error inesperado** (bug, fallo de infraestructura) | la base de datos se cae a mitad de una operación | `500` con `{"detail": "Error interno del servidor. Revisá los logs."}` — **sin filtrar detalles internos** | `ERROR` con el traceback completo | No — ver "transacciones" abajo |

En los tres casos **el servidor sigue vivo**: un error en una petición no afecta a las
demás. Hay un test que lo verifica (`test_error_inesperado_devuelve_500_generico`).

## Transacciones: todo o nada

Cada petición que escribe usa **una** transacción de base de datos. La lógica está en
`app/core/db.py` (`get_db`):

- si el servicio termina bien, hace `commit`;
- si lanza una excepción (de dominio o inesperada), hace **`rollback`** antes de cerrar la
  sesión.

Por eso, por ejemplo, si `registrar_factura` crea el asiento y después falla al guardar la
factura, **no queda el asiento suelto**: se deshace todo. La generación de asientos
(`crear_asiento`) además valida el cuadre de partida doble *antes* de tocar la base de
datos.

## Base de datos caída o lenta

- **PostgreSQL** (producción): el pool de conexiones usa `pool_pre_ping` (verifica la
  conexión antes de usarla) y `pool_recycle` (renueva conexiones viejas). Si el servidor de
  BD se reinicia, la app se recupera sola en la siguiente petición.
- **Al arrancar**: si la base de datos no responde, la app **arranca igual** pero lo deja
  claro en el log (`ERROR`) y el endpoint `/salud` responde `"degradado"`. Así el
  contenedor no entra en un ciclo de reinicios y, cuando la BD vuelve, todo funciona.
- **El contenedor Docker** reintenta las migraciones hasta 10 veces al arrancar (la BD de
  `docker compose` puede tardar en aceptar conexiones).

## Endpoint de salud

`GET /salud` → `{"estado": "ok", "base_de_datos": true}`

- `estado: "ok"` si la base de datos responde; `"degradado"` si no.
- Lo usa el `healthcheck` de Docker / la nube para saber si la instancia está sana.
- No requiere autenticación y no expone datos.

## Los logs

- **Todo va a stdout** (así lo recoge Docker y cualquier nube sin configurar nada).
- **Un formato único**: `fecha  NIVEL  logger  mensaje`.
- Cada logger se llama `elgerente.<área>`: `elgerente.http`, `elgerente.contabilidad`,
  `elgerente.facturas`, `elgerente.arranque`... — se puede filtrar por área.
- **Nivel configurable**: `LOG_LEVEL` en el `.env` (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

### Qué se registra

| Momento | Nivel | Ejemplo |
|---|---|---|
| Arranque | `INFO` | `El Gerente arrancando — entorno=prod  base_de_datos=postgresql+asyncpg://elgerente:***@db:5432/elgerente` |
| Arranque | `INFO` / `WARNING` | `Plan de cuentas: 10 cuentas` · o `El plan de cuentas está vacío. Correr: python -m app.seed` |
| Cada petición | `INFO` | `POST /facturas -> 200 (18 ms)` |
| Cada petición 5xx | `WARNING` | `GET /balance -> 500 (11 ms)` |
| Hecho de negocio | `INFO` | `Factura F-001 registrada — #3 tipo=recibida tercero=1 total=595000.00` |
| Hecho de negocio | `INFO` | `Asiento #7 creado — origen=factura libro=oficial lineas=3` |
| Error de dominio | `INFO` | `Error de dominio 404: Factura 9999 no existe` |
| Asiento descuadrado (no debería pasar) | `ERROR` | `Asiento descuadrado rechazado — origen=manual debito=100 credito=90` |
| Error inesperado | `ERROR` | traceback completo + `Error inesperado en POST /movimientos` |

- La **contraseña de la base de datos nunca aparece** en los logs (se enmascara).
- Los montos sí se registran: son datos del propio negocio, en su propio servidor.
- Las peticiones a `/`, `/salud` y `/static/*` con respuesta correcta **no se loguean**
  (serían ruido: el healthcheck pega cada 10 segundos).

## Cómo probar la resiliencia

`tests/integration/test_servicio.py`:
- `/salud` responde bien;
- un fallo simulado en un servicio → `500` genérico, sin filtrar el mensaje interno, y el
  servidor sigue respondiendo otras peticiones;
- un error de dominio → código correcto y mensaje claro;
- datos inválidos → `422` con detalle.
