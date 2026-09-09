# Backend — El Gerente

FastAPI + SQLAlchemy 2.0 (async) + SQLite. Arquitectura **por features**: cada parte
funcional es una carpeta autocontenida. La documentación viva está en
[`../docs/`](../docs/) — empezar por [`../docs/README.md`](../docs/README.md).

## Estado

- **Módulo 1 — motor contable**: completo, 65 tests en verde.
  Features: `contabilidad-nucleo`, `balance`, `terceros`, `facturas`, `pagos`,
  `contratos`, `movimientos` (ver [`../docs/features/README.md`](../docs/features/README.md)).
- **Interfaz gráfica HTML** en `/`: completa.
- **Endurecimiento** (resiliencia a fallos, logs, `/salud`, imagen Docker): completo — ver
  [`../docs/arquitectura/resiliencia-y-logs.md`](../docs/arquitectura/resiliencia-y-logs.md)
  y [`../docs/arquitectura/despliegue.md`](../docs/arquitectura/despliegue.md).
- **Módulo 2 — WhatsApp**: pendiente.

## Estructura

```
app/
  core/            config (.env), engine async, errores de dominio
  contabilidad/    NÚCLEO: cuenta / asiento / linea_asiento, crear_asiento (partida doble), balance, plan de cuentas
  features/
    terceros/      clientes y proveedores
    facturas/      registrar factura emitida/recibida -> asiento automático
    pagos/         pagar/cobrar factura -> asiento automático + estado
    contratos/     registro informativo (sin contabilidad)
    movimientos/   asiento manual: oficial (con soporte) / interno (para-contabilidad)
  main.py          create_app(): ensambla los routers + traduce errores de dominio a HTTP
  models.py        agregador: importa todos los modelos para Alembic y los tests
  seed.py          siembra el plan de cuentas (NO crea tablas)
alembic/           migraciones (el esquema se crea con `alembic upgrade head`)
tests/
  unit/            reglas de negocio, servicios llamados directo
  integration/     app completa vía httpx.AsyncClient + SQLite temporal
scripts/reset_db.py   borra la BD, migra y siembra (solo desarrollo)
```

Cada feature: `models.py` · `schemas.py` · `service.py` (toda la lógica) · `router.py`
(solo traduce HTTP) · `exceptions.py` cuando aplica.

## Cómo correrlo

Este entorno no trae `pip`; se usa [`uv`](https://docs.astral.sh/uv/).

```bash
cd backend
uv venv --python 3.12
uv pip install -e ".[dev]"
cp .env.example .env

.venv/bin/alembic upgrade head        # crea elgerente.db con todas las tablas
.venv/bin/python -m app.seed          # siembra el plan de cuentas

.venv/bin/uvicorn app.main:app --reload
# http://localhost:8000/       interfaz gráfica
# http://localhost:8000/docs   API
# http://localhost:8000/salud  chequeo de salud
```

### Con Docker (app + PostgreSQL)

```bash
# desde la raíz del repo:
cp .env.docker.example .env.docker
docker compose --env-file .env.docker up --build
```

Ver [`../docs/arquitectura/despliegue.md`](../docs/arquitectura/despliegue.md).

## Tests

```bash
.venv/bin/python -m pytest              # toda la suite (56)
.venv/bin/python -m pytest -m "not integration"   # solo unit
.venv/bin/python -m pytest --collect-only -q      # listar sin ejecutar
.venv/bin/ruff check .                  # lint
```

Detalle en [`../docs/arquitectura/testing.md`](../docs/arquitectura/testing.md) y el
catálogo completo en [`../docs/features/pruebas.md`](../docs/features/pruebas.md).

`elgerente.db` y `.env` no se suben al repo (ver `.gitignore`).
