# Visión técnica

Este documento explica **cómo está armado el backend** y por qué. Está pensado para poder
auditar el proyecto sin conocer de antemano las herramientas.

## Las piezas

| Pieza | Herramienta | Para qué sirve |
|---|---|---|
| Servidor web / API | **FastAPI** | Recibe peticiones HTTP (y los webhooks de WhatsApp) y devuelve respuestas |
| Acceso a la base de datos | **SQLAlchemy 2.0** (modo async) | Traduce entre objetos Python y filas de tablas, sin escribir SQL a mano |
| Base de datos | **SQLite** (un archivo) hoy; **PostgreSQL** cuando haga falta | Guarda los datos de verdad |
| Migraciones | **Alembic** | Lleva el control de los cambios de estructura de la base de datos |
| Configuración | **pydantic-settings** | Lee los ajustes del archivo `.env` |
| Cliente HTTP saliente | **httpx** (async) | Llama a APIs externas (la de WhatsApp del proveedor) |
| Pruebas | **pytest** + **pytest-asyncio** | Corre los tests unitarios y de integración |

## Las capas

Cada petición atraviesa las mismas capas, siempre en el mismo orden:

```
   Petición HTTP  /  mensaje de WhatsApp
            │
            ▼
┌───────────────────────────────┐
│ TRANSPORTE                    │  router de FastAPI / webhook
│ Traduce la entrada.           │  Valida el formato con Pydantic.
│ NO decide nada de negocio.    │  Llama al servicio y traduce errores a HTTP.
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ SERVICIO DE FEATURE           │  app/features/<feature>/service.py
│ TODA la regla de negocio.     │  "Una factura recibida genera este asiento".
│ Funciones async.              │  Lanza errores de dominio (no HTTP).
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ NÚCLEO CONTABLE               │  app/contabilidad/
│ crear_asiento() valida        │  Único punto que escribe en las tablas contables.
│ partida doble. calcular_      │  Nadie mete un asiento descuadrado.
│ balance().                    │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ MODELOS (SQLAlchemy)          │  app/**/models.py
│ Las tablas como clases Python │
└───────────────────────────────┘
```

**Por qué importa esta separación:** para auditar una regla de negocio basta leer *un*
archivo de servicio. Y cuando el Módulo 2 (WhatsApp) necesite registrar una factura,
llamará a `facturas.service.registrar_factura(...)` — la **misma función** que usa la API —
no reimplementará la lógica.

## Por qué asincronismo (async / await)

"Async" quiere decir que, mientras el programa **espera** algo lento (una respuesta de red),
puede atender otra cosa en vez de quedarse bloqueado.

- El **Módulo 1 por sí solo no lo necesita**: leer y escribir en una base de datos local es
  rápido y no hay nada que esperar.
- El **Módulo 2 sí**: cada mensaje de WhatsApp implica llamar a la API del proveedor para
  responderle al usuario. Eso es una espera de red. Con async, el servidor puede atender
  muchas conversaciones a la vez sin trabarse. El Módulo 3 (IA) esperará aún más (la
  respuesta del modelo).

Se decidió usar async **en todo desde el principio** para no tener dos estilos de código
conviviendo cuando lleguen los módulos 2 y 3.

**El costo** (y cómo se paga):

| Costo del async | Cómo se maneja aquí |
|---|---|
| Las relaciones del ORM no se pueden cargar "por sorpresa" (lazy loading) | Se cargan explícitamente con `selectinload(...)` en la consulta |
| El cálculo de balance no puede iterar objetos cómodamente | Se hace con **una sola consulta SQL de agregación** (más rápido igual) |
| Los tests necesitan un runner async | `pytest-asyncio` en modo `auto`: cualquier `async def test_...` funciona sin decorador |

## Recorrido de una petición, de punta a punta

Ejemplo: `POST /facturas` con una factura recibida.

1. **FastAPI** recibe el JSON y lo valida contra el esquema `FacturaCreate` (Pydantic). Si
   falta un campo o el tipo está mal → responde `422` automáticamente.
2. El router `facturas/router.py` pide una sesión de base de datos (`Depends(get_db)`) y
   llama a `facturas.service.registrar_factura(session, ...)`.
3. El **servicio** verifica que el tercero exista (si no → `NoEncontrado`, que el router
   traduce a `404`), calcula `total = subtotal + iva`, arma las tres líneas del asiento
   según la tabla de reglas, y llama a `contabilidad.asientos.crear_asiento(...)`.
4. `crear_asiento` verifica que el asiento **cuadre** (suma de débitos = suma de créditos).
   Si no cuadra → `AsientoDesbalanceado` y no se guarda nada.
5. El servicio guarda la factura enlazada a ese asiento y hace `commit`.
6. El router devuelve la factura creada como JSON (esquema `FacturaOut`).

## Ver también

- [`base-de-datos.md`](base-de-datos.md) — cómo se crea y evoluciona el esquema.
- [`testing.md`](testing.md) — cómo se prueba todo esto.
- [`../aprendizaje/async-await.md`](../aprendizaje/async-await.md) — async explicado desde cero.
