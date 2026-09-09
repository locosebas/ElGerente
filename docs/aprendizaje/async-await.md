# async / await (asincronismo)

## El problema que resuelve

Imagina un cajero de banco (el servidor) atendiendo clientes (las peticiones).

- **Modo síncrono (bloqueante):** un cliente pide algo que tarda (una transferencia
  internacional que hay que confirmar por teléfono). El cajero se queda con el teléfono en
  la oreja esperando, y **la fila entera se detiene** aunque los demás solo quieran
  consultar su saldo.
- **Modo asíncrono:** mientras espera la confirmación por teléfono, el cajero atiende a los
  siguientes de la fila. Cuando llega la confirmación, retoma al primer cliente.

`async` / `await` es lo que le permite al servidor "atender a otros mientras espera".

## Cuándo ayuda y cuándo no

Async solo ayuda cuando el programa **espera algo externo**: una respuesta de red, una API,
un disco lento. No acelera cálculos.

| Tarea | ¿Async ayuda? |
|---|---|
| Leer/escribir en una base de datos local | Poco (es rápido) |
| Llamar a la API de WhatsApp para responderle a alguien | **Sí** (es una espera de red) |
| Llamar a un modelo de IA y esperar su respuesta | **Sí, mucho** |
| Sumar una lista de números | No |

## Cómo se ve en el código

```python
# Función normal (síncrona):
def obtener_factura(id):
    return db.get(Factura, id)

# Función async:
async def obtener_factura(id):
    return await db.get(Factura, id)
```

- `async def` declara una función que puede "pausarse".
- `await` marca el punto donde se espera algo; ahí el servidor puede irse a atender otra
  cosa.
- Una función `async` solo se puede llamar con `await` desde otra función `async`. Por eso,
  una vez que entra async, sube por toda la cadena: router, servicio, acceso a datos.

## Por qué El Gerente lo usa en todo desde el inicio

El Módulo 1 solo no lo necesitaría. Pero los Módulos 2 (WhatsApp) y 3 (IA) sí. Mantener
una sola forma de escribir código —en vez de migrar de síncrono a async a mitad de
camino, o tener las dos conviviendo— sale más barato y es más fácil de auditar.

## Lo que hay que tener en cuenta (y ya está resuelto en el proyecto)

1. **Carga de relaciones explícita.** En modo síncrono, si tienes un `asiento` y accedes a
   `asiento.lineas`, el ORM va a la base de datos "por sorpresa". En async eso no se
   permite: hay que pedir las líneas por adelantado en la consulta, con
   `selectinload(Asiento.lineas)`.
2. **El balance se calcula con SQL, no iterando objetos.** Es una consulta de agregación
   (`SUM(...) GROUP BY cuenta`). Además de encajar con async, es más rápida.
3. **Los tests son async.** `pytest-asyncio` está configurado en modo automático; cualquier
   `async def test_...` simplemente funciona.
4. **El driver de la base de datos también es async:** `aiosqlite` para SQLite, `asyncpg`
   para PostgreSQL. Se elige según la `DATABASE_URL`.
