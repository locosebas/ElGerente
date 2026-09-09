# Qué es una API (y qué es una API REST)

## La idea

Una **API** (Application Programming Interface) es la lista de cosas que un programa sabe
hacer y que otro programa puede pedirle. Es un menú: "puedes pedirme *registrar una
factura*, *listar los terceros*, *calcular el balance*", y cada opción tiene una forma
exacta de pedirse y una forma exacta de responder.

En El Gerente, el **motor contable** (Módulo 1) expone una API. Quien la usa:

- hoy: el propio dueño probando, y la interfaz gráfica HTML;
- después: el Módulo 2 (WhatsApp) — aunque ese, por estar en el mismo programa, llama
  directamente a las funciones de servicio, sin pasar por la red.

## API REST sobre HTTP

**HTTP** es el protocolo de la web (el mismo que usa el navegador). Una petición HTTP tiene:

- un **método** (o "verbo"): `GET` (traer datos), `POST` (crear algo), `PUT`/`PATCH`
  (modificar), `DELETE` (borrar);
- una **ruta**: `/facturas`, `/balance`, `/terceros/5`;
- opcionalmente un **cuerpo** (body): datos en formato JSON;
- opcionalmente **parámetros de query**: `/balance?incluir_interna=true`.

Y la respuesta tiene:

- un **código de estado**: `200` (ok), `201` (creado), `404` (no existe), `422` (datos
  mal), `409` (conflicto), `500` (error del servidor);
- un **cuerpo**: normalmente JSON.

**REST** es un estilo de diseñar estas APIs: cada "cosa" (recurso) tiene su ruta, y los
verbos HTTP expresan qué hacer con ella. Ejemplos de El Gerente:

| Quiero... | Petición |
|---|---|
| Ver el plan de cuentas | `GET /cuentas` |
| Registrar un cliente | `POST /terceros` con `{"nombre": "...", "nit_cedula": "...", "tipo": "cliente"}` |
| Ver una factura concreta | `GET /facturas/3` |
| Marcar la factura 3 como pagada | `POST /facturas/3/pagar` con `{"medio_pago": "bancos", "fecha": "2026-09-10"}` |
| Ver el balance incluyendo lo interno | `GET /balance?incluir_interna=true` |

## Cómo se ve en este proyecto

- **FastAPI** es la herramienta que convierte funciones de Python en endpoints HTTP.
- Cada feature tiene un `router.py` con sus endpoints. El router **solo traduce**: recibe
  el JSON, lo valida, llama al servicio, y convierte el resultado (o el error) en una
  respuesta HTTP.
- **Pydantic** define la forma exacta de cada entrada y salida (los "esquemas"). Si mandas
  una factura sin `numero`, FastAPI responde `422` solo, sin que nadie lo programe.
- FastAPI genera una **documentación interactiva automática** en `http://localhost:8000/docs`:
  ahí se ve la lista completa de endpoints y se pueden probar desde el navegador.

## Determinístico

Toda esta API es **código normal, determinístico**: dadas las mismas entradas, siempre
produce el mismo resultado, y se puede leer línea por línea para entender exactamente qué
hace. No hay inteligencia artificial en el motor contable. La IA entra recién en el Módulo
3, y solo para leer documentos — ver
[`deterministico-vs-ia.md`](deterministico-vs-ia.md).
