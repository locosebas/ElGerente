"""Conexión a la base de datos — SQLAlchemy 2.0 en modo asíncrono.

- `engine`: el motor async, construido a partir de `DATABASE_URL`.
- `SessionLocal`: fábrica de sesiones async.
- `Base`: clase madre de todos los modelos ORM.
- `get_db`: dependencia de FastAPI que entrega una sesión por petición.

Pasar de SQLite a PostgreSQL = cambiar `DATABASE_URL` en el .env. Nada de
este archivo ni de los modelos se toca.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Todos los modelos heredan de aquí; `Base.metadata` conoce todas las tablas."""


_settings = get_settings()

# `future=True` ya es el comportamiento por defecto en 2.0; lo dejamos explícito.
engine = create_async_engine(_settings.database_url, future=True)

SessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Entrega una sesión y la cierra al terminar la petición.

    No hace commit automático: cada servicio decide cuándo confirmar.
    """
    async with SessionLocal() as session:
        yield session
