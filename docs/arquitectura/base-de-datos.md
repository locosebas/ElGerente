# Base de datos

## Qué motor y dónde

| Entorno | Motor | Ubicación |
|---|---|---|
| Desarrollo (hoy) | SQLite | archivo `backend/elgerente.db` (no se sube al repo) |
| Producción / multiusuario (futuro) | PostgreSQL | un servidor de base de datos |

Pasar de uno a otro es cambiar **una sola línea** en `backend/.env`:

```
# de esto:
DATABASE_URL=sqlite+aiosqlite:///./elgerente.db
# a esto:
DATABASE_URL=postgresql+asyncpg://usuario:clave@host:5432/elgerente
```

Ningún código cambia: todo pasa por SQLAlchemy, que habla los dos dialectos. `aiosqlite` y
`asyncpg` son los "drivers" async de cada motor.

## Cómo se crea el esquema: con Alembic, no con `create_all`

**El problema del enfoque viejo.** Antes, las tablas se creaban con
`Base.metadata.create_all(engine)`: útil para empezar, pero no deja rastro de los cambios y
no sabe qué hacer cuando la tabla ya existe y tiene datos reales.

**El enfoque nuevo: migraciones.** Cada cambio de estructura de la base de datos (crear una
tabla, agregar una columna...) se escribe como un archivo numerado en
`backend/alembic/versions/`. Cada archivo sabe cómo aplicar el cambio (`upgrade`) y cómo
revertirlo (`downgrade`). La base de datos guarda en qué versión está.

```
alembic/versions/
  01_esquema_inicial.py          # crea las 6 tablas del Módulo 1
  02_conversaciones_whatsapp.py  # crea la tabla de conversaciones del Módulo 2
  ...
```

### Comandos

Desde `backend/`, con el entorno activado:

```bash
alembic upgrade head        # aplica todas las migraciones pendientes (crea/actualiza la BD)
alembic downgrade -1        # revierte la última migración
alembic history             # lista las migraciones y en cuál está la BD
alembic current             # muestra la versión actual de la BD

# Al cambiar un modelo, generar la migración correspondiente (y REVISARLA a mano antes de aplicar):
alembic revision --autogenerate -m "descripción del cambio"
```

`alembic/env.py` está configurado para usar el engine **async** del proyecto y toma la
`DATABASE_URL` de `app.core.config` (el mismo sitio que todo lo demás).

## Datos iniciales (seed)

`backend/app/seed.py` **no crea tablas**. Solo inserta los datos base que el programa
necesita para funcionar: el **plan de cuentas** (las cuentas contables: Caja, Bancos,
etc. — ver la lista en
[`../features/contabilidad-nucleo/spec.md`](../features/contabilidad-nucleo/spec.md)).

Es **idempotente**: si la tabla `cuenta` ya tiene filas, no hace nada. Se puede correr las
veces que sea sin duplicar.

## Puesta en marcha (primera vez)

```bash
cd backend
uv venv --python 3.12                 # crea el entorno virtual (o: python -m venv .venv)
uv pip install -e ".[dev]"            # instala dependencias
cp .env.example .env                  # ajustar si no se quiere el SQLite por defecto

.venv/bin/alembic upgrade head        # crea elgerente.db con todas las tablas
.venv/bin/python -m app.seed          # inserta el plan de cuentas

.venv/bin/uvicorn app.main:app --reload
```

Para empezar de cero rápido en desarrollo: `.venv/bin/python scripts/reset_db.py` (borra el
archivo, re-crea el esquema y vuelve a sembrar).

## La base de datos en los tests

Los tests **no** usan Alembic ni el archivo `elgerente.db`. Cada corrida crea una base de
datos SQLite **en memoria** y levanta el esquema directamente desde los modelos
(`Base.metadata.create_all`). Es más rápido y cada test parte de cero.

Para que el esquema de los modelos y el de las migraciones no se separen sin que nadie se
dé cuenta, hay un test (`tests/integration/test_migraciones.py`) que corre
`alembic upgrade head` sobre una base temporal y comprueba que no queda ninguna diferencia
sin migrar. Si alguien cambia un modelo y olvida generar la migración, ese test falla.
