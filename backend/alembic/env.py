"""Entorno de Alembic, configurado para el engine asíncrono del proyecto.

Alembic por dentro es síncrono, así que abrimos la conexión async y le
pedimos que corra las migraciones con `connection.run_sync(...)`.

`target_metadata` apunta a `Base.metadata`, que conoce todas las tablas
declaradas en los modelos. Importamos `app.models` para que esos modelos
queden registrados antes de comparar.
"""
from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine

# Registra todos los modelos en Base.metadata (import con efecto secundario).
import app.models  # noqa: F401,E402
from alembic import context
from app.core.config import get_settings
from app.core.db import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# La URL puede venir del propio comando (útil en tests, que apuntan a una BD
# temporal); si no, se toma de la configuración del proyecto.
DATABASE_URL = config.get_main_option("sqlalchemy.url") or get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # necesario para ALTER TABLE en SQLite
    )
    with context.begin_transaction():
        context.run_migrations()


def _do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(DATABASE_URL, future=True)
    async with engine.connect() as connection:
        await connection.run_sync(_do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
